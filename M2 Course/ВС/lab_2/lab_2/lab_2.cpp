#include <iostream>
#include <clocale>

using namespace std;

int main() {
    setlocale(LC_ALL, "rus");
    double A = 2.5;
    double B = 4.0;
    double C = 3.0;
    double D = 2.0;
    double Y;


    cout << "A= " << A << endl;
    cout << "B= " << B << endl;
    cout << "C= " << C << endl;
    cout << "D= " << D << endl;
    cout << "Вычисление: Y = A * B + (C^2) / D" << endl;

    __asm {
        fld A; Загрузить A в ST(0)
        fmul B; ST(0) = A * B

        fld C; Загрузить C в ST(0), A* B сдвигается в ST(1)
        fmul ST(0), ST(0); ST(0) = C * C

        fdiv D; ST(0) = C ^ 2 / D

        faddp ST(1), ST(0); ST(1) = ST(1) + ST(0), затем вытолкнуть ST(0)
        ; Теперь результат в ST(0)

        fstp Y; Сохранить ST(0) в Y и очистить стек
    }

    cout << "Результат Y = " << Y << endl;
    return 0;
}