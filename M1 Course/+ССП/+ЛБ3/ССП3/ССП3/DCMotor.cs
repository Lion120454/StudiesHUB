using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ССП3
{
    public class DCMotor : Motor// Двигатель постоянного тока
    {
        private float _voltage; // Напряжение
        private int _direction; // направление (1 - вперед, -1 - назад)

        public DCMotor() : base()
        {
            _voltage = 0.0f;
            _direction = 1;
        }

        public override void SetFrequency(float frequency)
        {
            Frequency = frequency;

            _voltage = frequency * 0.1f * _direction; // 0.1 В на 1 Гц

            // Формируем последовательность для отправки в контроллер
            // код символа 'u' + значение напряжения (float)
            byte[] voltageBytes = CreateCommandBytes('u', _voltage);

            Console.WriteLine("Двигатель постоянного тока: отправлена команда:");
            Console.WriteLine($"  Код символа: 'u' ({(int)'u'})");
            Console.WriteLine($"  Напряжение: {_voltage:F2} В");
            Console.WriteLine($"  Байты: {BitConverter.ToString(voltageBytes)}");

            // Имитация получения подтверждения от контроллера
            ReceiveConfirmation();

            if (!IsRunning && frequency != 0)
            {
                Start();
            }
            else if (frequency == 0)
            {
                Stop();
            }
        }

        private byte[] CreateCommandBytes(char symbol, float value)
        {
            byte[] bytes = new byte[5]; // 1 байт для символа + 4 байта для float
            bytes[0] = (byte)symbol;
            byte[] floatBytes = BitConverter.GetBytes(value);
            Array.Copy(floatBytes, 0, bytes, 1, 4);
            return bytes;
        }

        private void ReceiveConfirmation()
        {
            // Имитируем задержку обработки
            Thread.Sleep(100);

            // Формируем подтверждение: код 'f' + частота (float)
            byte[] confirmationBytes = CreateCommandBytes('f', Frequency);

            Console.WriteLine("Двигатель постоянного тока: получено подтверждение:");
            Console.WriteLine($"  Код символа: 'f' ({(int)'f'})");
            Console.WriteLine($"  Частота: {Frequency:F2} Гц");
            Console.WriteLine($"  Байты: {BitConverter.ToString(confirmationBytes)}");
        }

        public override void Start()
        {
            IsRunning = true;
            Console.WriteLine("Двигатель постоянного тока: запущен");
        }

        public override void Stop()
        {
            IsRunning = false;
            Frequency = 0;
            _voltage = 0.0f;
            Console.WriteLine("Двигатель постоянного тока: остановлен");
        }

        public override void Reverse()
        {
            _direction *= -1;
            string directionText = _direction == 1 ? "прямое" : "обратное";
            Console.WriteLine($"Двигатель постоянного тока: направление изменено на {directionText}");

            // При изменении направления обновляем напряжение
            if (IsRunning)
            {
                SetFrequency(Frequency);
            }
        }
    }
}
