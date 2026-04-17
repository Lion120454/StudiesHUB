#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <stdbool.h>
int* MS(int** a, int m, int n, int index)//Массив только не повторяющихся элементов
{
    int* arr = malloc(sizeof(int)*n);
    for (int i = 0; i < n; i++)
    {
        arr[i] = 101;
    }
    for (int i = 0; i < n; i++)
    {
        for (int j = i; j < n; j++)
        {
            if (i != j)
            {
                if (a[index][i] == a[index][j])
                {
                    if (arr[j] != j)
                    {
                        arr[j] = j;
                    }
                }
            }
        }
    }
    return arr;
}
int main()
{
    setlocale(LC_ALL ,"Rus");
    srand(time(NULL));
    int m, n, c = 0, t = 0;
    printf("Введите кол-во строк матрицы: ");
    scanf("%d", &m);
    printf("Введите кол-во столбцов: ");
    scanf("%d", &n);
    int** a = malloc(sizeof(int*)*m);
    for (int i = 0; i < m; i++)
    {
        *(a+i) = malloc(sizeof(int)*n);
    }
    for (int i = 0; i < m; i++)
    {
        for (int j = 0; j < n; j++)
        {
            a[i][j] = rand()%5;
            printf(" %d ", a[i][j]);
        }
        printf("\n");
    }
    int* mas = MS(a,m,n, 0);
    for (int i = 0; i < n; i++)
    {
        if (mas[i] == 101)
            t++;
    }
    for (int i = 1; i < m; i++)
    {
        int* arr = MS(a,m,n,i);
        int t1 = 0, f = 0;
        bool fl = true;
        for (int j = 0; j < n; j++)
        {
            if (arr[j] == 101)
                t1++;
        }
        if (t1 == t)
        {
            for (int j = 0; j < n; j++)
            {
                if (mas[j] == 101)
                {
                    for (int k = 0; k < n; k++)
                    {
                        if (arr[k] == 101)
                        {
                            if (a[0][j] == a[i][k])
                                f++;
                        }
                    }
                }
            }
        }
        else
            fl = false;
        if ((f == t) && (fl == true))
            c++;
        free(arr);
    }
    printf("\nКол-во похожих строчек = %d\n", c);
    return 0;
}
