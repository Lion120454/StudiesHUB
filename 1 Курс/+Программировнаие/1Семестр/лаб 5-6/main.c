#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
const int a=5;
void Out(int m[5][5])
{
    int i,j;
    for (i = 0; i < a; i++)
    {
        for (j = 0; j < a; j++)
        {
            printf(" %d", m[i][j]);
        }
        printf(" \n");
    }
}

void poisk(int m[5][5])
{
    int x,y,max=0,s,i,j;
    for(i=0;i<a;i++)
    {
        s=0;
        for(j=0;j<a;j++)
        {
            s=s+m[i][j];
        }
        if(max<s)
        {
            max=s;
            x=i;
            y=j;
        }
    }
printf("Наибоее отдалёная точка от начала координат (%d,%d)",x,y);
}


int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int f,i,j;
    printf("Выберите способ ввода(1 - Заданный массив, 2 - Вручную,3 - Рандомный массив)\n");
    printf("Способ:");
    scanf("%d", &f);
    if(f==1)
    {
        int m[5][5] = {
                    {2,6,32,77,41},
                    {27,40,43,2,21},
                    {18,29,45,11,54},
                    {30,52,33,37,90},
                    {83,48,39,64,58}
                  };
        Out(m);
        poisk(m);
    }

    if(f==2)
    {
        printf("Размерность матрицы по умолчанию равна 5\n");
        int m[5][5];
        for(i=0;i<a;i++)
        {
            for(j=0;j<a;j++)
            {
                printf("Ведите элемент: \n");
                scanf("%d",&m[i][j]);
            }
        }
        Out(m);
        poisk(m);
    }

    if(f==3)
    {
        int m[5][5];
        for(i=0;i<a;i++)
        {
            for(j=0;j<a;j++)
            {
                m[i][j]=1 + rand()%100;
            }
        }
        Out(m);
        poisk(m);
    }
    getch();
}
