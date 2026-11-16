#include <iostream>
#include <clocale>
using namespace std;

int main() {
    setlocale(LC_ALL, "rus");
    const int n = 10; //Размер массива
    int arr[n] = { 5, -3, 8, -1, -7, 2, 0, -4, 9, -6 }; //Масив
    int sum = 0; //Сумма

    __asm {
        xor eax,  eax; //sum = 0
        xor ecx,  ecx; //i = 0
        mov edx, n;  //edx = n
        lea esi, arr;  //esi = &arr[0]

        loop_start:
        cmp ecx, edx //Сравнение i и n путём вычитания
            jge loop_end; //если i >= n, выход

            mov ebx, [esi + ecx * 4];  //ebx = arr[i]
            test ebx, ebx //побитовое И(проверка на отрицательность)
            jns skip;  //если arr[i] >= 0, пропустить

            add eax, ebx;  //sum += arr[i]
            skip:
        inc ecx;  //i++
            jmp loop_start
            loop_end :
        mov sum, eax
    }

    cout << "Сумма отрицательных элементов: " << sum <<endl;
    return 0;
}