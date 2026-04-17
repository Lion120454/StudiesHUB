#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
void Out(int **m,int a)
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

void poisk(int **m,int a)
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
    printf("Выберите способ ввода(1 - Вручную,2 - Рандомный массив)\n");
    printf("Способ:");
    scanf("%d", &f);
    if(f==1)
    {
        int **m = 0;
        int a;
        printf("Введите размерность матрицы: \n");
        scanf("%d",&a);
        m=malloc(sizeof(*m)*a);
        for(i = 0; i < a; i++)
        {
            m[i] = malloc(sizeof(**m)*a);
        }
        for(i=0;i<a;i++)
        {
            for(j=0;j<a;j++)
            {
                printf("Введите элемент \n");
                scanf("%d",&m[i][j]);
            }
        }
        Out(m,a);
        poisk(m,a);
        for(i = a; i > 0; i--)
        {
            free(m[i]);
        }
    }

    if(f==2)
    {
        int **m = 0;
        int a;
        a = 1 + rand()%5;
        m = malloc(a * sizeof(*m));
        for(i = 0; i < a; i++)
        {
            m[i] = malloc(sizeof(**m)*a);
        }
        for(i=0;i<a;i++)
        {
            for(j=0;j<a;j++)
            {
                m[i][j]=1 + rand()%100;
            }
        }
        Out(m,a);
        poisk(m,a);
        for(i = a; i > 0; i--)
        {
            free(m[i]);
        }
    }
    getch();
}
