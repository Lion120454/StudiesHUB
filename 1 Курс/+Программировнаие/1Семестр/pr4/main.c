#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

double series(double x, double eps)
{
    double a,n=1,sum;
    a=x/6;
    sum=a;
    while(1==1)
    {
        a=((2*n*x)-(3*x))/((8*n*n*n)-(2*n));
        sum=sum+a;
        n++;
        if(fabs(a)<=eps)
        {
         break;
        }
    }
    return sum;
}

int main()
{
    double eps,left,right,l,t,x;
    setlocale (LC_CTYPE, "RUSSIAN");
    while(1==1)
    {
        printf("Введите границы интервала\n");
        printf("Левая:");
        scanf("%lf",&left);
        printf("Правая:");
        scanf("%lf",&right);
        if(right<left)
        {
            printf("Левая должна быть меньше правой! Повторите.\n");
        }
        if(right==left)
        {
            printf("Левая должна равнятся правой! Повторите.\n");
        }
        else
        {
            break;
        }
    }

    l=right-left;

    while(1==1)
    {
        printf("Введите шаг табулирования:");
        scanf("%lf",&t);
        if(t>l||t<=0)
        {
            printf("Шаг должен быть меньше длины интервала!\n");
        }
        else
        {
            break;
        }
    }

    while(1 == 1)
    {
        printf("Введите допустимую погрешность вычисления\n");
        printf("0<eps<1:");
        scanf("%lf",&eps);
        if(eps>=1||eps<=0)
        {
            printf("Введено недопустимое значение.\n");
        }
        else
        {
            break;
        }
    }

    printf("+_____________+_____________+\n");
    printf("|______X______|_____F(x)____|\n");
    printf("+_____________+_____________+\n");
    for(x=left;x<=right+eps;x=x+t)
    {
        printf("|__%lf__|__%lf__|\n",x,series(x,eps));
    }
    printf("+_____________+_____________+\n");
    getch();
    return 0;
}
