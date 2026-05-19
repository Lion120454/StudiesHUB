import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import gymnasium as gym
from collections import deque
import matplotlib.pyplot as plt
import time
import os
import warnings
warnings.filterwarnings("ignore")

class ActorCritic(nn.Module):
    """Простая но эффективная архитектура"""
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        
        # Общая часть
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        
        # Actor - предсказывает действия
        self.actor = nn.Linear(hidden_dim, action_dim)
        
        # Critic - предсказывает ценность состояния
        self.critic = nn.Linear(hidden_dim, 1)
        
        # Важно: специальная инициализация для исследования
        nn.init.orthogonal_(self.fc1.weight, gain=np.sqrt(2))
        nn.init.orthogonal_(self.fc2.weight, gain=np.sqrt(2))
        nn.init.orthogonal_(self.actor.weight, gain=0.01)  # Маленький gain для разнообразия
        nn.init.orthogonal_(self.critic.weight, gain=1.0)
        
        # Смещения в 0
        for m in [self.fc1, self.fc2, self.actor, self.critic]:
            nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        action_logits = self.actor(x)
        state_value = self.critic(x)
        
        return action_logits, state_value

class A2CAgent:
    """Простой и эффективный A2C агент"""
    def __init__(self, state_dim, action_dim, lr=0.002, gamma=0.99, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        self.network = ActorCritic(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr)
        
        self.gamma = gamma
        
        # Загружаем модель если она существует
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        # Буферы для одного эпизода
        self.reset_episode()
    
    def reset_episode(self):
        self.log_probs = []
        self.values = []
        self.rewards = []
        self.entropies = []
    
    def load_model(self, path):
        """Загрузка сохраненной модели"""
        try:
            self.network.load_state_dict(torch.load(path, map_location=self.device))
            self.network.eval()  # Переключаем в режим оценки
            print(f"✅ Модель загружена из {path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def save_model(self, path):
        """Сохранение модели"""
        torch.save(self.network.state_dict(), path)
        print(f"💾 Модель сохранена в {path}")
    
    def get_action(self, state, deterministic=False):
        """Выбрать действие"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        logits, value = self.network(state)
        probs = F.softmax(logits, dim=-1)
        
        if deterministic:
            action = torch.argmax(probs)
        else:
            # Создаем распределение и семплируем
            dist = Categorical(probs)
            action = dist.sample()
            
            # Сохраняем для обучения
            self.log_probs.append(dist.log_prob(action))
            self.values.append(value)
            self.entropies.append(dist.entropy())
        
        return action.item()
    
    def update(self):
        """Обновить сеть в конце эпизода"""
        # Конвертируем в тензоры
        log_probs = torch.cat(self.log_probs)
        values = torch.cat(self.values)
        entropies = torch.cat(self.entropies)
        
        # Вычисляем returns (дисконтированные награды)
        returns = []
        R = 0
        for r in reversed(self.rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        
        returns = torch.FloatTensor(returns).to(self.device)
        
        # Нормализуем returns для стабильности
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Вычисляем advantage
        advantages = returns - values.squeeze()
        
        # Функции потерь
        actor_loss = -(log_probs * advantages.detach()).mean()
        critic_loss = advantages.pow(2).mean()
        entropy_bonus = -0.01 * entropies.mean()  # Маленький бонус за исследование
        
        # Общая потеря
        loss = actor_loss + 0.5 * critic_loss + entropy_bonus
        
        # Обновляем веса
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=0.5)
        self.optimizer.step()
        
        # Очищаем буферы
        self.reset_episode()
        
        return loss.item()

def train_with_progress(episodes=3000, model_path="lunar_lander_success.pth"):
    """Обучение с подробным отслеживанием прогресса"""
    env = gym.make("LunarLander-v3")
    
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    print(f"🚀 Начинаем обучение LunarLander-v3")
    print(f"Состояний: {state_dim}, Действий: {action_dim}")
    print(f"Действия: 0=Ничего, 1=Левый, 2=Главный, 3=Правый\n")
    
    agent = A2CAgent(state_dim, action_dim, lr=0.002, model_path=model_path)
    
    # Статистика
    rewards_history = []
    recent_rewards = deque(maxlen=100)
    best_reward = -float('inf')
    best_avg_reward = -float('inf')
    
    # График в реальном времени
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    for episode in range(1, episodes + 1):
        state, _ = env.reset()
        episode_reward = 0
        done = False
        steps = 0
        
        # Один эпизод
        while not done and steps < 1000:
            action = agent.get_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Модифицируем награды для лучшего обучения
            shaped_reward = reward
            
            # Поощряем использование главного двигателя когда близко к земле
            if state[1] < 0.5 and action == 2:  # Низко и включен главный двигатель
                shaped_reward += 0.1
            
            # Штрафуем за бездействие когда быстро падает
            if state[3] < -1.0 and action == 0:  # Быстро падает и ничего не делает
                shaped_reward -= 0.1
            
            agent.rewards.append(shaped_reward)
            episode_reward += reward  # Оригинальная награда для статистики
            
            steps += 1
            state = next_state
        
        # Обновляем сеть
        loss = agent.update()
        
        # Собираем статистику
        rewards_history.append(episode_reward)
        recent_rewards.append(episode_reward)
        avg_reward = np.mean(recent_rewards)
        
        if episode_reward > best_reward:
            best_reward = episode_reward
        
        # Автосохранение лучшей модели
        if len(recent_rewards) >= 100 and avg_reward > best_avg_reward:
            best_avg_reward = avg_reward
            agent.save_model(model_path)
            print(f"   📈 Автосохранение! Новая лучшая средняя награда: {avg_reward:.1f}")
        
        # Выводим прогресс
        if episode % 10 == 0:
            print(f"Ep {episode:4d} | "
                  f"Reward: {episode_reward:7.1f} | "
                  f"Avg100: {avg_reward:7.1f} | "
                  f"Best: {best_reward:7.1f} | "
                  f"Steps: {steps:3d} | "
                  f"Loss: {loss:.4f}")
        
        # Обновляем графики каждые 50 эпизодов
        if episode % 50 == 0:
            ax1.clear()
            ax2.clear()
            
            # График наград
            ax1.plot(rewards_history, alpha=0.6, linewidth=1, color='blue')
            
            # Скользящее среднее
            if len(rewards_history) > 100:
                moving_avg = np.convolve(rewards_history, np.ones(100)/100, mode='valid')
                ax1.plot(range(100, len(rewards_history)+1), moving_avg, 
                        color='red', linewidth=2, label=f'Avg: {avg_reward:.1f}')
            
            ax1.axhline(y=200, color='green', linestyle='--', alpha=0.7, label='Success (200)')
            ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Crash line')
            ax1.set_xlabel('Episode')
            ax1.set_ylabel('Reward')
            ax1.set_title('Training Progress')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Распределение последних 100 наград
            if len(recent_rewards) > 10:
                ax2.hist(list(recent_rewards), bins=20, color='skyblue', edgecolor='black')
                ax2.axvline(x=200, color='green', linestyle='--', label='Success')
                ax2.axvline(x=0, color='red', linestyle='--', label='Crash')
                ax2.set_xlabel('Reward')
                ax2.set_ylabel('Frequency')
                ax2.set_title('Reward Distribution (Last 100)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.pause(0.01)
        
        # Проверка на решение
        if len(recent_rewards) >= 100 and avg_reward >= 200:
            print(f"\n🎉 ЗАДАЧА РЕШЕНА на эпизоде {episode}!")
            print(f"Средняя награда за 100 эпизодов: {avg_reward:.1f}")
            agent.save_model(model_path)
            break
    
    plt.ioff()
    plt.show()
    env.close()
    
    return agent, rewards_history

def test_agent(agent, num_episodes=5, render=True):
    """Тестирование обученного агента"""
    render_mode = "human" if render else None
    env = gym.make("LunarLander-v3", render_mode=render_mode)
    
    results = []
    
    for i in range(num_episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
            
            with torch.no_grad():
                logits, _ = agent.network(state_tensor)
                probs = F.softmax(logits, dim=-1)
                action = torch.argmax(probs).item()  # Детерминированная политика
            
            state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward
            
            if render:
                time.sleep(0.02)
        
        results.append(total_reward)
        
        # Оценка результата
        if total_reward >= 200:
            status = "✅ ОТЛИЧНО"
        elif total_reward >= 0:
            status = "⚠️ НОРМАЛЬНО"
        else:
            status = "💥 ПЛОХО"
        
        print(f"Тест {i+1}: Reward = {total_reward:7.1f} - {status}")
    
    env.close()
    
    print(f"\n📊 Средняя награда: {np.mean(results):.1f}")
    print(f"📈 Лучшая: {np.max(results):.1f}")
    print(f"📉 Худшая: {np.min(results):.1f}")
    print(f"✅ Успешных посадок: {sum(1 for r in results if r >= 200)}/{num_episodes}")
    
    return results

def analyze_agent(agent):
    """Анализ того, чему научился агент"""
    env = gym.make("LunarLander-v3")
    
    print("\n" + "="*60)
    print("📊 АНАЛИЗ СТРАТЕГИИ")
    print("="*60)
    
    actions_names = ["0-Ничего", "1-Левый", "2-Главный", "3-Правый"]
    
    # Тестовые сценарии
    scenarios = [
        (0.0, 0.0, 0.0, -0.5, 0.0, "Зависит над центром"),
        (1.0, 0.5, 0.0, -1.0, 0.0, "Смещен вправо, падает"),
        (-1.0, 1.0, 0.0, -0.5, 0.0, "Смещен влево, высоко"),
        (0.0, 0.3, 0.0, -2.0, 0.0, "Низко, быстро падает"),
        (0.0, 1.5, 0.0, -0.1, 0.0, "Высоко, почти завис"),
    ]
    
    for x, y, vx, vy, angle, desc in scenarios:
        state = np.array([x, y, vx, vy, angle, 0.0, 0.0, 0.0])
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
        
        with torch.no_grad():
            logits, value = agent.network(state_tensor)
            probs = F.softmax(logits, dim=-1).squeeze().cpu().numpy()
        
        print(f"\n📍 {desc}")
        print(f"   Позиция: x={x:.1f}, y={y:.1f}, vx={vx:.1f}, vy={vy:.1f}")
        print(f"   Ценность состояния: {value.item():.2f}")
        print("   Вероятности действий:")
        
        for name, prob in zip(actions_names, probs):
            bar = "█" * int(prob * 40)
            print(f"     {name}: {bar} {prob:.2%}")
    
    env.close()

def check_model_exists(model_path="lunar_lander_success.pth"):
    """Проверка наличия обученной модели"""
    if os.path.exists(model_path):
        print(f"✅ Найдена обученная модель: {model_path}")
        return True
    else:
        print(f"❌ Модель не найдена: {model_path}")
        return False

def main():
    """Основная функция с проверкой модели"""
    MODEL_PATH = "lunar_lander_success.pth"
    
    print("🌙 LUNAR LANDER - A2C АГЕНТ")
    print("="*60)
    
    # Проверяем наличие модели
    model_exists = check_model_exists(MODEL_PATH)
    
    if model_exists:
        print("\n📂 Обнаружена сохраненная модель!")
        print("Что вы хотите сделать?")
        print("1. Использовать существующую модель (демонстрация)")
        print("2. Обучить новую модель")
        print("3. Дообучить существующую модель")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == "1":
            # Просто загружаем и используем
            print("\n📥 Загрузка модели...")
            
            # Создаем временную среду для получения размерностей
            temp_env = gym.make("LunarLander-v3")
            state_dim = temp_env.observation_space.shape[0]
            action_dim = temp_env.action_space.n
            temp_env.close()
            
            agent = A2CAgent(state_dim, action_dim, model_path=MODEL_PATH)
            
            # Анализируем стратегию
            analyze_agent(agent)
            
            # Демонстрируем
            print("\n" + "="*60)
            print("🎮 ДЕМОНСТРАЦИЯ ОБУЧЕННОГО АГЕНТА")
            print("="*60)
            input("\nНажмите Enter для просмотра 5 посадок...")
            test_agent(agent, num_episodes=5, render=True)
            
        elif choice == "2":
            # Обучаем новую модель
            print("\n🔄 Обучение новой модели...")
            print("Старая модель будет перезаписана.")
            input("Нажмите Enter для начала обучения...")
            
            agent, history = train_with_progress(episodes=3000, model_path=MODEL_PATH)
            
            # Анализируем
            analyze_agent(agent)
            
            # Тестируем
            print("\n" + "="*60)
            print("🎮 ТЕСТИРОВАНИЕ НОВОГО АГЕНТА")
            print("="*60)
            input("\nНажмите Enter для просмотра 5 тестовых посадок...")
            test_agent(agent, num_episodes=5, render=True)
            
        elif choice == "3":
            # Дообучаем существующую модель
            print("\n📈 Дообучение существующей модели...")
            input("Нажмите Enter для начала дообучения...")
            
            agent, history = train_with_progress(episodes=1000, model_path=MODEL_PATH)
            
            # Анализируем
            analyze_agent(agent)
            
            # Тестируем
            print("\n" + "="*60)
            print("🎮 ТЕСТИРОВАНИЕ ДООБУЧЕННОГО АГЕНТА")
            print("="*60)
            input("\nНажмите Enter для просмотра 5 тестовых посадок...")
            test_agent(agent, num_episodes=5, render=True)
        
        else:
            print("Неверный выбор. Использую существующую модель.")
            # Загружаем и показываем
            temp_env = gym.make("LunarLander-v3")
            state_dim = temp_env.observation_space.shape[0]
            action_dim = temp_env.action_space.n
            temp_env.close()
            
            agent = A2CAgent(state_dim, action_dim, model_path=MODEL_PATH)
            test_agent(agent, num_episodes=5, render=True)
    
    else:
        print("\n🆕 Модель не найдена. Начинаем обучение...")
        input("Нажмите Enter для начала обучения...")
        
        agent, history = train_with_progress(episodes=3000, model_path=MODEL_PATH)
        
        # Анализируем
        analyze_agent(agent)
        
        # Тестируем
        print("\n" + "="*60)
        print("🎮 ТЕСТИРОВАНИЕ ОБУЧЕННОГО АГЕНТА")
        print("="*60)
        input("\nНажмите Enter для просмотра 5 тестовых посадок...")
        test_agent(agent, num_episodes=5, render=True)

if __name__ == "__main__":
    main()