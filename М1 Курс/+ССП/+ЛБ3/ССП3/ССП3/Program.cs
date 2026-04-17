using System;
using System.Collections.Generic;

using System.Threading.Tasks;

namespace ССП3
{    
    public class MotorDemo
    {
        public static void DemonstrateMotors()
        {
            // Создаем двигатели
            var stepper = new StepperMotor();
            var dcMotor = new DCMotor();

            var motors = new List<Motor> { stepper, dcMotor };

            Console.WriteLine(new string('=', 50));
            Console.WriteLine("ДЕМОНСТРАЦИЯ РАБОТЫ С ДВИГАТЕЛЯМИ");
            Console.WriteLine(new string('=', 50));

            // Демонстрируем работу с каждым двигателем через методы абстрактного класса
            for (int i = 0; i < motors.Count; i++)
            {
                var motor = motors[i];
                Console.WriteLine($"\n--- Двигатель {i + 1}: {motor.GetType().Name} ---");

                // Получаем начальный статус
                Console.WriteLine("Начальный статус:");
                PrintStatus(motor.GetStatus());

                // Устанавливаем частоту
                motor.SetFrequency(2.0f); // 2 Гц

                // Изменяем направление
                motor.Reverse();

                // Снова устанавливаем частоту
                motor.SetFrequency(3.0f);

                // Получаем финальный статус
                Console.WriteLine("Финальный статус:");
                PrintStatus(motor.GetStatus());

                // Останавливаем двигатель
                motor.Stop();
            }
        }

        private static void PrintStatus(Dictionary<string, object> status)
        {
            foreach (var item in status)
            {
                Console.WriteLine($"  {item.Key}: {item.Value}");
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            MotorDemo.DemonstrateMotors();
            Console.ReadKey();
        }
    }
}