using System;
using System.Threading;
using System.Diagnostics;

namespace ССП_2
{
    class Program
    {
        // Общий ресурс - счетчик элементов в диапазоне
        private static int countInRange = 0;
        private static readonly object lockObject = new object();

        // Параметры задачи
        private static double minValue, maxValue;
        private static double[,] matrix;

        static double[,] CreateMatrix()
        {
            Console.Write("Введите количество столбцов: ");
            int columns = Convert.ToInt32(Console.ReadLine());
            Console.Write("Введите количество строк: ");
            int lines = Convert.ToInt32(Console.ReadLine());
            matrix = new double[lines, columns];
            Random r = new Random();
            for (int i = 0; i < lines; i++)
            {
                for (int j = 0; j < columns; j++)
                {
                    matrix[i, j] = r.Next(-10, 10);
                }
            }
            return matrix;
        }//Создание матрицы
        static void PrintMatrix()
        {
            for (int i = 0; i < matrix.GetLength(0); i++)
            {
                for (int j = 0; j < matrix.GetLength(1); j++)
                {
                    Console.Write($"{matrix[i, j],8:F2}");
                }
                Console.WriteLine("");
            }
        }//Вывод матрицы
        static void InputRange()//Ввод диапозона
        {
            Console.Write("Введите минимальное значение диапазона: ");
            minValue = Convert.ToDouble(Console.ReadLine());
            Console.Write("Введите максимальное значение диапазона: ");
            maxValue = Convert.ToDouble(Console.ReadLine());

            if (minValue > maxValue)
            {
                Console.WriteLine("Минимальное значение больше максимального! Меняем местами.");
                double temp = minValue;
                minValue = maxValue;
                maxValue = temp;
            }

            Console.WriteLine($"Диапазон для поиска: [{minValue}, {maxValue}]");
        }
        static int CountInRangeSequential()
        {
            int count = 0;
            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (matrix[i, j] >= minValue && matrix[i, j] <= maxValue)
                    {
                        count++;
                    }
                }
            }
            return count;
        }//Последовательный подсчет
        static void CountInRangeParallel(int threadCount)
        {
            countInRange = 0;

            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);

            // Создаем и запускаем потоки
            Thread[] threads = new Thread[threadCount];

            for (int i = 0; i < threadCount; i++)
            {
                int threadIndex = i;
                threads[i] = new Thread(() => ProcessSubmatrix(threadIndex, threadCount, rows, cols));
                threads[i].Start();
            }

            // Ожидаем завершения всех потоков
            foreach (Thread thread in threads)
            {
                thread.Join();
            }

        }//Организация многопоточной обработки
        static void ProcessSubmatrix(int threadIndex, int totalThreads, int totalRows, int totalCols)
        {
            // Разделяем матрицу по строкам
            int rowsPerThread = totalRows / totalThreads;
            int startRow = threadIndex * rowsPerThread;
            int endRow = (threadIndex == totalThreads - 1) ? totalRows : startRow + rowsPerThread;

            int localCount = 0;

            // Подсчитываем элементы в диапазоне для своей подматрицы
            for (int i = startRow; i < endRow; i++)
            {
                for (int j = 0; j < totalCols; j++)
                {
                    if (matrix[i, j] >= minValue && matrix[i, j] <= maxValue)
                    {
                        localCount++;
                    }
                }
            }

            // Безопасно добавляем локальный счетчик к общему
            lock (lockObject)
            {
                countInRange += localCount;
                //Console.WriteLine($"Поток {threadIndex}: найдено {localCount} элементов");
            }
        }

        static void Main(string[] args)
        {
            // Инициализация матрицы
            while (true)
            {
                CreateMatrix();

                // Ввод диапазона
                InputRange();

                // Вывод исходной матрицы
                //PrintMatrix();
                Console.WriteLine($"Диапазон для поиска: [{minValue}, {maxValue}]");

                DateTime startTime = DateTime.Now;
                // Подсчет в основном потоке для проверки
                int sequentialCount = CountInRangeSequential();
                DateTime endTime = DateTime.Now;
                Console.WriteLine($"\nРезультат последовательного подсчета: {sequentialCount}, Время: {(endTime-startTime).TotalMilliseconds} ms");


                // Многопоточный подсчет
                startTime = DateTime.Now;
                int threadCount = Environment.ProcessorCount;
                Console.WriteLine($"Количество логических процессоров: {threadCount}");
                Math.Min(threadCount, matrix.GetLength(0));
                CountInRangeParallel(threadCount);
                endTime = DateTime.Now;
                Console.WriteLine($"Результат параллельного подсчета: {countInRange}, Время: {(endTime - startTime).TotalMilliseconds} ms");
            
                // Проверка корректности
                if (sequentialCount == countInRange)
                {
                    Console.WriteLine("Результаты совпадают! Программа работает корректно.");
                }
                else
                {
                    Console.WriteLine("Результаты не совпадают! Возникла ошибка в синхронизации.");
                }
                Console.ReadKey();
            }
        }
    }
}
