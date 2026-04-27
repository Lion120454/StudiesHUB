using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ССП3
{
    public class StepperMotor : Motor// Шаговый двигатель
    {
        private readonly byte[] _sequence =
        {
        0b00000001,  // 1
        0b00000010,  // 2
        0b00000100,  // 4
        0b00001000   // 8
    };

        private int _currentStep; //текущий шаг
        private int _direction; // направление( 1 - вперед, -1 - назад)
        private double _stepDelay; // задержка между шагами в секундах

        public StepperMotor() : base()
        {
            _currentStep = 0;
            _direction = 1;
            _stepDelay = 0.1;
        }

        public override void SetFrequency(float frequency)
        {
            if (frequency == 0)
            {
                Stop();
                return;
            }

            Frequency = frequency;
            // Рассчитываем задержку между шагами на основе частоты
            // 1 Гц ≈ 1 шаг в секунду
            _stepDelay = 1.0 / (frequency * 4); // 4 шага на полный цикл


            if (!IsRunning)
            {
                Start();
            }

            RunComand();
            Console.WriteLine($"Шаговый двигатель: установлена частота {frequency} Гц");
            Console.WriteLine($"Задержка между шагами: {_stepDelay:F4} сек");
        }

        public override void Start()
        {
            IsRunning = true;
            Console.WriteLine("Шаговый двигатель: запущен");
        }

        public override void Stop()
        {
            IsRunning = false;
            Frequency = 0;
            Console.WriteLine("Шаговый двигатель: остановлен");
        }

        public override void Reverse()
        {
            _direction *= -1;
            string directionText = _direction == 1 ? "прямое" : "обратное";
            Console.WriteLine($"Шаговый двигатель: направление изменено на {directionText}");
        }

        // Метод для выполнения одного шага
        public void ExecuteStep()
        {
            if (!IsRunning) return;

            // Получаем текущий байт из последовательности
            byte stepByte = _sequence[_currentStep];

            // Отображаем сигнал с временной меткой
            Console.WriteLine($"[{DateTime.Now}] Шаговый двигатель: отправлен байт {Convert.ToString(stepByte, 2).PadLeft(8, '0')}");

            // Переходим к следующему шагу
            _currentStep = (_currentStep + _direction + _sequence.Length) % _sequence.Length;
        }

        // Демонстрация работы шагового двигателя
        public void RunComand()
        {
            Console.Write("Введите кол. шагов:");
            int steps = Convert.ToInt32(Console.ReadLine());
            Console.WriteLine($"\nДемонстрация шагового двигателя ({steps} шагов):");
            for (int i = 0; i < steps; i++)
            {
                ExecuteStep();
            }
            _currentStep = 0;
        }
    }
}
