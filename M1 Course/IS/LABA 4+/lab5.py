import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import gymnasium as gym
from collections import deque
import matplotlib.pyplot as plt

class ActorCritic(nn.Module):
    """Нейронная сеть для Actor-Critic архитектуры"""
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(ActorCritic, self).__init__()
        
        # Общие слои
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Actor head (политика)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # Critic head (функция ценности)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state):
        shared_features = self.shared(state)
        action_probs = self.actor(shared_features)
        state_value = self.critic(shared_features)
        return action_probs, state_value
    
    def act(self, state):
        """Выбор действия и вычисление логарифма вероятности"""
        state = torch.FloatTensor(state).unsqueeze(0)
        action_probs, state_value = self.forward(state)
        
        # Создаем распределение и семплируем действие
        dist = Categorical(action_probs)
        action = dist.sample()
        action_logprob = dist.log_prob(action)
        
        return action.item(), action_logprob, state_value

class A2C:
    """Advantage Actor-Critic агент"""
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, 
                 entropy_coef=0.01, value_loss_coef=0.5, max_grad_norm=0.5):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor_critic = ActorCritic(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=lr)
        
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.value_loss_coef = value_loss_coef
        self.max_grad_norm = max_grad_norm
        
        # Для хранения треков обучения
        self.log_probs = []
        self.values = []
        self.rewards = []
        self.entropies = []
    
    def select_action(self, state):
        """Выбор действия для заданного состояния"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        action_probs, state_value = self.actor_critic(state)
        
        dist = Categorical(action_probs)
        action = dist.sample()
        
        # Сохраняем для обновления
        self.log_probs.append(dist.log_prob(action))
        self.values.append(state_value)
        self.entropies.append(dist.entropy())
        
        return action.item()
    
    def compute_returns(self, next_value, dones):
        """Вычисление дисконтированных возвратов"""
        returns = []
        R = next_value
        
        for step in reversed(range(len(self.rewards))):
            R = self.rewards[step] + self.gamma * R * (1 - dones[step])
            returns.insert(0, R)
        
        return torch.cat(returns).detach()
    
    def update(self, next_state, done):
        """Обновление параметров сети"""
        # Преобразуем в тензоры
        log_probs = torch.cat(self.log_probs)
        values = torch.cat(self.values)
        entropies = torch.cat(self.entropies)
        
        # Вычисляем возвраты
        with torch.no_grad():
            if not done:
                next_state = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
                _, next_value = self.actor_critic(next_state)
            else:
                next_value = torch.zeros(1, 1).to(self.device)
        
        returns = []
        R = next_value
        for r in reversed(self.rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        
        returns = torch.cat(returns).detach()
        
        # Вычисляем преимущество (advantage)
        advantages = returns - values.squeeze()
        
        # Функции потерь
        actor_loss = -(log_probs * advantages.detach()).mean()
        critic_loss = advantages.pow(2).mean()
        entropy_loss = -entropies.mean()
        
        # Общая функция потерь
        loss = actor_loss + self.value_loss_coef * critic_loss + self.entropy_coef * entropy_loss
        
        # Оптимизация
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.actor_critic.parameters(), self.max_grad_norm)
        self.optimizer.step()
        
        # Очищаем буферы
        self.log_probs = []
        self.values = []
        self.rewards = []
        self.entropies = []
        
        return loss.item()

def train(env_name="CartPole-v1", episodes=1000, print_every=100):
    """Обучение A2C агента"""
    env = gym.make(env_name)
    
    state_dim = env.observation_space.shape[0]
    
    # Проверяем тип пространства действий
    if isinstance(env.action_space, gym.spaces.Discrete):
        action_dim = env.action_space.n
    else:
        action_dim = env.action_space.shape[0]
    
    agent = A2C(state_dim, action_dim)
    
    episode_rewards = []
    avg_rewards = []
    recent_rewards = deque(maxlen=100)
    
    for episode in range(1, episodes + 1):
        state, _ = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            # Выбор действия
            action = agent.select_action(state)
            
            # Шаг в среде
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Сохраняем награду
            agent.rewards.append(reward)
            episode_reward += reward
            
            # Обновление агента
            if done:
                agent.update(next_state, done)
            
            state = next_state
        
        episode_rewards.append(episode_reward)
        recent_rewards.append(episode_reward)
        avg_reward = np.mean(recent_rewards)
        avg_rewards.append(avg_reward)
        
        # Вывод прогресса
        if episode % print_every == 0:
            print(f"Episode {episode}/{episodes} | "
                  f"Reward: {episode_reward:.2f} | "
                  f"Avg Reward (100 eps): {avg_reward:.2f}")
        
        # Условие завершения обучения
        if avg_reward >= env.spec.reward_threshold if env.spec.reward_threshold else 195:
            print(f"\nЗадача решена на эпизоде {episode}!")
            print(f"Средняя награда за 100 эпизодов: {avg_reward:.2f}")
            break
    
    env.close()
    
    return agent, episode_rewards, avg_rewards

def plot_results(rewards, avg_rewards):
    """Визуализация результатов обучения"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # График наград по эпизодам
    ax1.plot(rewards, alpha=0.6, label='Episode Reward')
    ax1.plot(avg_rewards, label='Average Reward (100 eps)', linewidth=2)
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.set_title('Training Progress')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # График скользящего среднего
    ax2.plot(avg_rewards, linewidth=2, color='green')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Average Reward (100 eps)')
    ax2.set_title('Smoothed Training Progress')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def test_agent(agent, env_name="CartPole-v1", episodes=5, render=True):
    """Тестирование обученного агента"""
    env = gym.make(env_name, render_mode="human" if render else None)
    
    for episode in range(1, episodes + 1):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(agent.device)
            action_probs, _ = agent.actor_critic(state_tensor)
            dist = Categorical(action_probs)
            action = dist.sample().item()
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward
            state = next_state
        
        print(f"Test Episode {episode}: Total Reward = {total_reward}")
    
    env.close()

# Дополнительная реализация с параллельными средами для лучшей производительности
class ParallelA2C:
    """A2C с параллельными средами для более стабильного обучения"""
    
    def __init__(self, state_dim, action_dim, num_envs=4, lr=3e-4, gamma=0.99,
                 entropy_coef=0.01, value_loss_coef=0.5, max_grad_norm=0.5):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor_critic = ActorCritic(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=lr)
        
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.value_loss_coef = value_loss_coef
        self.max_grad_norm = max_grad_norm
        self.num_envs = num_envs
    
    def compute_advantages(self, rewards, values, dones, next_value):
        """Вычисление преимуществ с GAE"""
        returns = []
        advantages = []
        
        gae = 0
        R = next_value.squeeze()
        
        for step in reversed(range(len(rewards))):
            R = rewards[step] + self.gamma * R * (1 - dones[step])
            td_error = rewards[step] + self.gamma * values[step + 1] * (1 - dones[step]) - values[step]
            gae = td_error + self.gamma * 0.95 * gae * (1 - dones[step])
            
            returns.insert(0, R)
            advantages.insert(0, gae)
        
        return torch.FloatTensor(returns), torch.FloatTensor(advantages)

# Пример использования
if __name__ == "__main__":
    # Обучаем агента на CartPole
    print("Начинаем обучение A2C агента...")
    agent, rewards, avg_rewards = train(
        env_name="CartPole-v1",
        episodes=1000,
        print_every=50
    )
    
    # Визуализируем результаты
    plot_results(rewards, avg_rewards)
    
    # Тестируем обученного агента
    print("\nТестирование обученного агента...")
    test_agent(agent, episodes=3, render=False)
    
    # Сохраняем модель
    torch.save(agent.actor_critic.state_dict(), "a2c_model.pth")
    print("\nМодель сохранена как 'a2c_model.pth'")