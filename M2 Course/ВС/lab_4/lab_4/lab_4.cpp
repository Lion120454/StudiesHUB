#include <iostream>
#include <immintrin.h> // Заголовочный файл для SSE/AVX
#include <vector>
#include <cstdlib>
#include <ctime>

void printArray(const std::vector<float>& arr, const char* name) {
    std::cout << name << ": ";
    for (float val : arr) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
}

int main() {
    setlocale(LC_ALL, "Russian");
    const int n = 12; // Размер массивов (кратен 4 для удобства SSE)

    // Создаем массивы (используем vector для удобства)
    std::vector<float> A(n), B(n), C(n), Y(n);

    // Заполняем массивы случайными числами от 0 до 10
    srand(static_cast<unsigned>(time(0)));
    for (int i = 0; i < n; ++i) {
        A[i] = static_cast<float>(rand() % 100) / 10.0f;
        B[i] = static_cast<float>(rand() % 100) / 10.0f;
        C[i] = static_cast<float>(rand() % 100) / 10.0f;
    }

    // Вывод исходных данных
    printArray(A, "Массив A");
    printArray(B, "Массив B");
    printArray(C, "Массив C");
    std::cout << "------------------------" << std::endl;

    // --- Блок SSE вычислений ---

    // Проходим по массивам с шагом 4 (так как SSE обрабатывает 4 float за раз)
    for (int i = 0; i < n; i += 4) {
        // 1. Загружаем по 4 элемента из массивов A, B и C в регистры xmm
        // _mm_loadu_ps используется, если память не выровнена по 16 байт.
        __m128 vec_A = _mm_loadu_ps(&A[i]);
        __m128 vec_B = _mm_loadu_ps(&B[i]);
        __m128 vec_C = _mm_loadu_ps(&C[i]);

        // 2. Выполняем умножение: vec_A * vec_B
        // Инструкция _mm_mul_ps выполняет 4 умножения параллельно
        __m128 vec_mul = _mm_mul_ps(vec_A, vec_B);

        // 3. Выполняем сложение: (A*B) + C
        // Инструкция _mm_add_ps выполняет 4 сложения параллельно
        __m128 vec_result = _mm_add_ps(vec_mul, vec_C);

        // 4. Сохраняем результат обратно в массив Y
        _mm_storeu_ps(&Y[i], vec_result);
    }

    // --- Конец блока SSE ---

    printArray(Y, "Массив Y (результат)");

    // Проверка правильности (скалярный расчет)
    std::cout << "\nПроверка первых 4 элементов:" << std::endl;
    for (int i = 0; i < 4; ++i) {
        float check = A[i] * B[i] + C[i];
        std::cout << "Y[" << i << "] SSE: " << Y[i] << " | Обычный: " << check << std::endl;
    }

    return 0;
}