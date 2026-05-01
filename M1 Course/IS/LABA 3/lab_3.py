import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.utils import save_image
from torch.utils.data import DataLoader
import os
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt

# ОБЯЗАТЕЛЬНО для Windows - защита мультипроцессинга
if __name__ == '__main__':
    # Конфигурация для MNIST (100 эпох)
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100, help="Количество эпох")
    parser.add_argument("--batch_size", type=int, default=64, help="Размер батча")
    parser.add_argument("--lr", type=float, default=0.0002, help="Скорость обучения")
    parser.add_argument("--latent_dim", type=int, default=100, help="Размер латентного вектора")
    parser.add_argument("--image_size", type=int, default=64, help="Размер изображения")
    parser.add_argument("--channels", type=int, default=1, help="Каналы (1 - ч/б для MNIST)")
    parser.add_argument("--dataset", type=str, default="mnist", help="Датасет (mnist)")
    parser.add_argument("--output_dir", type=str, default="mnist_output", help="Папка для результатов")
    parser.add_argument("--save_interval", type=int, default=10, help="Сохранять модели каждые N эпох")
    parser.add_argument("--num_workers", type=int, default=0, help="Количество рабочих процессов (0 для Windows)")
    opt = parser.parse_args()

    # Создание папок
    os.makedirs(opt.output_dir, exist_ok=True)
    os.makedirs(os.path.join(opt.output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(opt.output_dir, "models"), exist_ok=True)

    # Настройка устройства
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Используется устройство: {device}")
    print(f"Количество эпох: {opt.epochs}")
    print(f"Датасет: MNIST (рукописные цифры)")

    # Загрузка датасета MNIST
    def get_dataloader(image_size, batch_size):
        transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])  # Нормализация для ч/б изображений
        ])
        
        dataset = torchvision.datasets.MNIST(
            root="./data", train=True, download=True, transform=transform
        )
        
        return DataLoader(dataset, batch_size=batch_size, shuffle=True, 
                         num_workers=opt.num_workers, pin_memory=False)

    # Архитектура DCGAN для MNIST
    class Generator(nn.Module):
        """Генератор для ч/б изображений MNIST"""
        def __init__(self, latent_dim, channels, image_size):
            super(Generator, self).__init__()
            self.latent_dim = latent_dim
            self.image_size = image_size
            
            self.init_size = image_size // 16  # 64 // 16 = 4
            self.init_channels = 512
            
            self.fc = nn.Linear(latent_dim, self.init_channels * self.init_size * self.init_size)
            
            self.conv_blocks = nn.Sequential(
                nn.BatchNorm2d(self.init_channels),
                nn.Upsample(scale_factor=2),
                nn.Conv2d(self.init_channels, 256, 3, stride=1, padding=1),
                nn.BatchNorm2d(256, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Upsample(scale_factor=2),
                nn.Conv2d(256, 128, 3, stride=1, padding=1),
                nn.BatchNorm2d(128, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Upsample(scale_factor=2),
                nn.Conv2d(128, 64, 3, stride=1, padding=1),
                nn.BatchNorm2d(64, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Upsample(scale_factor=2),
                nn.Conv2d(64, channels, 3, stride=1, padding=1),
                nn.Tanh()
            )
        
        def forward(self, z):
            out = self.fc(z)
            out = out.view(out.shape[0], self.init_channels, self.init_size, self.init_size)
            img = self.conv_blocks(out)
            return img

    class Discriminator(nn.Module):
        """Дискриминатор для ч/б изображений MNIST"""
        def __init__(self, channels, image_size):
            super(Discriminator, self).__init__()
            
            self.conv_blocks = nn.Sequential(
                nn.Conv2d(channels, 32, 3, 2, 1),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Dropout2d(0.25),
                nn.Conv2d(32, 64, 3, 2, 1),
                nn.BatchNorm2d(64, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Dropout2d(0.25),
                nn.Conv2d(64, 128, 3, 2, 1),
                nn.BatchNorm2d(128, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Dropout2d(0.25),
                nn.Conv2d(128, 256, 3, 2, 1),
                nn.BatchNorm2d(256, 0.8),
                nn.LeakyReLU(0.2, inplace=True),
                nn.Dropout2d(0.25),
            )
            
            ds_size = image_size // 16
            self.fc = nn.Sequential(
                nn.Linear(256 * ds_size * ds_size, 1),
                nn.Sigmoid()
            )
        
        def forward(self, img):
            out = self.conv_blocks(img)
            out = out.view(out.shape[0], -1)
            validity = self.fc(out)
            return validity

    # Инициализация моделей
    generator = Generator(opt.latent_dim, opt.channels, opt.image_size).to(device)
    discriminator = Discriminator(opt.channels, opt.image_size).to(device)

    # Функция инициализации весов
    def weights_init_normal(m):
        classname = m.__class__.__name__
        if classname.find("Conv") != -1:
            torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
        elif classname.find("BatchNorm") != -1:
            torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
            torch.nn.init.constant_(m.bias.data, 0.0)

    generator.apply(weights_init_normal)
    discriminator.apply(weights_init_normal)

    # Оптимизаторы
    optimizer_G = optim.Adam(generator.parameters(), lr=opt.lr, betas=(0.5, 0.999))
    optimizer_D = optim.Adam(discriminator.parameters(), lr=opt.lr, betas=(0.5, 0.999))

    # Функция потерь
    adversarial_loss = nn.BCELoss()

    # Загрузка данных
    print("Загрузка датасета MNIST...")
    dataloader = get_dataloader(opt.image_size, opt.batch_size)
    print(f"Датасет загружен. Количество батчей: {len(dataloader)}")

    # Фиксированный шум для визуализации прогресса
    fixed_noise = torch.randn(64, opt.latent_dim, device=device)

    # Списки для хранения истории потерь
    g_losses = []
    d_losses = []

    # Обучение
    print(f"\nНачинаем обучение DCGAN на датасете MNIST")
    print(f"Всего эпох: {opt.epochs}")
    print(f"Размер батча: {opt.batch_size}")
    print(f"Размер латентного пространства: {opt.latent_dim}")
    print("-" * 50)
    
    for epoch in range(opt.epochs):
        epoch_g_loss = 0
        epoch_d_loss = 0
        
        for i, (imgs, _) in enumerate(tqdm(dataloader, desc=f"Эпоха {epoch+1}/{opt.epochs}")):
            batch_size = imgs.shape[0]
            imgs = imgs.to(device)
            
            # Сглаживание меток для стабильности
            valid = torch.full((batch_size, 1), 0.9, device=device)
            fake = torch.zeros(batch_size, 1, device=device)
            
            # ---------------------
            # 1. Обучение дискриминатора
            # ---------------------
            optimizer_D.zero_grad()
            
            # Реальные изображения
            real_loss = adversarial_loss(discriminator(imgs), valid)
            
            # Фейковые изображения
            z = torch.randn(batch_size, opt.latent_dim, device=device)
            gen_imgs = generator(z)
            fake_loss = adversarial_loss(discriminator(gen_imgs.detach()), fake)
            
            d_loss = (real_loss + fake_loss) / 2
            d_loss.backward()
            optimizer_D.step()
            
            # ---------------------
            # 2. Обучение генератора
            # ---------------------
            optimizer_G.zero_grad()
            
            z = torch.randn(batch_size, opt.latent_dim, device=device)
            gen_imgs = generator(z)
            g_loss = adversarial_loss(discriminator(gen_imgs), valid)
            
            g_loss.backward()
            optimizer_G.step()
            
            # Накопление потерь
            epoch_g_loss += g_loss.item()
            epoch_d_loss += d_loss.item()
            
            # Вывод статистики каждые 100 батчей
            if i % 100 == 0:
                print(f"\n[Эпоха {epoch+1}/{opt.epochs}] [Батч {i}/{len(dataloader)}] "
                      f"[D loss: {d_loss.item():.4f}] [G loss: {g_loss.item():.4f}]")
        
        # Сохранение средних потерь за эпоху
        avg_g_loss = epoch_g_loss / len(dataloader)
        avg_d_loss = epoch_d_loss / len(dataloader)
        g_losses.append(avg_g_loss)
        d_losses.append(avg_d_loss)
        
        # Сохранение сгенерированных изображений
        with torch.no_grad():
            fake_images = generator(fixed_noise)
            save_image(fake_images, f"{opt.output_dir}/images/epoch_{epoch+1:03d}.png", 
                      nrow=8, normalize=True)
        
        # Сохранение моделей каждые save_interval эпох
        if (epoch + 1) % opt.save_interval == 0:
            torch.save(generator.state_dict(), f"{opt.output_dir}/models/generator_epoch_{epoch+1}.pth")
            torch.save(discriminator.state_dict(), f"{opt.output_dir}/models/discriminator_epoch_{epoch+1}.pth")
            print(f"\n✓ Модели сохранены для эпохи {epoch+1}")
        
        # Вывод прогресса
        print(f"\nЭпоха {epoch+1}/{opt.epochs} завершена.")
        print(f"  Средний D loss: {avg_d_loss:.4f}")
        print(f"  Средний G loss: {avg_g_loss:.4f}")
        print("-" * 50)

    # Сохранение финальных моделей
    torch.save(generator.state_dict(), f"{opt.output_dir}/models/final_generator.pth")
    torch.save(discriminator.state_dict(), f"{opt.output_dir}/models/final_discriminator.pth")
    
    # Построение графика потерь
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(g_losses, label='Generator Loss', color='blue')
    plt.plot(d_losses, label='Discriminator Loss', color='red')
    plt.xlabel('Эпоха')
    plt.ylabel('Потери')
    plt.title('Потери генератора и дискриминатора')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(g_losses, label='Generator Loss', color='blue')
    plt.xlabel('Эпоха')
    plt.ylabel('Потери')
    plt.title('Потери генератора')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{opt.output_dir}/losses_plot.png", dpi=150)
    plt.show()
    
    # Генерация финальных изображений
    def generate_final_images(num_images=64):
        with torch.no_grad():
            noise = torch.randn(num_images, opt.latent_dim, device=device)
            generated = generator(noise)
            save_image(generated, f"{opt.output_dir}/final_generated_digits.png", 
                      nrow=8, normalize=True)
            print(f"\n✓ Сохранено {num_images} сгенерированных цифр в {opt.output_dir}/final_generated_digits.png")
    
    generate_final_images()
    
    # Функция для демонстрации реальных vs сгенерированных
    def compare_real_vs_fake():
        # Получаем батч реальных изображений
        real_imgs, _ = next(iter(dataloader))
        real_imgs = real_imgs[:16].to(device)
        
        # Генерируем фейковые
        with torch.no_grad():
            noise = torch.randn(16, opt.latent_dim, device=device)
            fake_imgs = generator(noise)
        
        # Сохраняем сравнение
        comparison = torch.cat([real_imgs, fake_imgs], dim=0)
        save_image(comparison, f"{opt.output_dir}/real_vs_fake.png", 
                  nrow=8, normalize=True)
        print(f"✓ Сравнение реальных и сгенерированных сохранено в {opt.output_dir}/real_vs_fake.png")
    
    compare_real_vs_fake()
    
    # Создание GIF анимации
    def create_progress_gif():
        try:
            import imageio
            import glob
            
            images = []
            image_files = sorted(glob.glob(f"{opt.output_dir}/images/epoch_*.png"))
            
            if len(image_files) > 0:
                # Берем каждую 5-ю эпоху для GIF (чтобы не был слишком большим)
                for filename in image_files[::5]:
                    images.append(imageio.imread(filename))
                
                if images:
                    imageio.mimsave(f"{opt.output_dir}/training_progress.gif", images, duration=0.5)
                    print(f"✓ GIF анимация сохранена в {opt.output_dir}/training_progress.gif")
        except ImportError:
            print("  (Установите imageio для создания GIF: pip install imageio)")
    
    create_progress_gif()
    
    print("\n" + "="*50)
    print("ОБУЧЕНИЕ УСПЕШНО ЗАВЕРШЕНО!")
    print(f"Результаты сохранены в папке: {opt.output_dir}")
    print("="*50)
    print("\nСгенерированные изображения цифр:")
    print(f"  - Финальные цифры: {opt.output_dir}/final_generated_digits.png")
    print(f"  - Сравнение реальных и фейковых: {opt.output_dir}/real_vs_fake.png")
    print(f"  - График потерь: {opt.output_dir}/losses_plot.png")
    print(f"  - Анимация прогресса: {opt.output_dir}/training_progress.gif")
    print(f"  - Модели: {opt.output_dir}/models/")