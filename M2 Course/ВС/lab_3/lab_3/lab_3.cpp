#include <iostream>
#include <vector>
#include <cstdint> // Для использования int8_t, int16_t

int main() {
    setlocale(LC_ALL, "Russian");

    // Пример размерности массивов
    const size_t N = 5;

    // Исходные массивы
    // A и B - байты (от -128 до 127)
    std::vector<int8_t> A = { 10, -20, 30, 50, -5 };
    std::vector<int8_t> B = { 2, 5, -3, 4, 10 };

    // C - слова (от -32768 до 32767)
    std::vector<int16_t> C = { 100, -200, 3000, -4000, 500 };

    // Результирующий массив Y. 
    // Используем int32_t, так как A*B может дать до ~16000, + C может дать больше 32767.
    std::vector<int32_t> Y(N);

    std::cout << "Вычисление массива Y = A * B + C" << std::endl;
    std::cout << "--------------------------------" << std::endl;

    for (size_t i = 0; i < N; ++i) {
        // Явное приведение типов для избежания переполнения при умножении
        int32_t product = static_cast<int32_t>(A[i]) * static_cast<int32_t>(B[i]);

        // Вычисление результата
        Y[i] = product + static_cast<int32_t>(C[i]);

        // Вывод промежуточных данных для проверки
        std::cout << "i=" << i
            << " | A=" << (int)A[i]
            << " B=" << (int)B[i]
            << " C=" << C[i]
            << " | A*B=" << product
            << " -> Y=" << Y[i] << std::endl;
    }

    return 0;
}