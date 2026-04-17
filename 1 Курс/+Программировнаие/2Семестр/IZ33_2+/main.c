/*Дана матрица размера M ? N. В каждой её строке найти количество элементов,
меньших среднего арифметического всех элементов этой строки.
*/
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <time.h>
int* p(int m, int n, int **a)
{
    int i,j,k=0,s=0;
    float ar=0;
    int *v=malloc(sizeof(int*)*m);
    for(i=0;i<m;i++)
    {
        k=0;
        ar=0;
        s=0;
        for(j=0;j<n;j++)
        {
            k=k+a[i][j];
        }
        ar=(float)k/n;
        for(j=0;j<n;j++)
        {
            if((float)a[i][j]<ar)
            {
                s++;
            }
        }
        v[i]=s;
        //printf("%d=%d \n",i+1,s);
    }
    return v;
}

int main()
{
    srand(time(NULL));
    setlocale (LC_CTYPE, "RUSSIAN");
    int i,j,m,n;
    printf("Введите кол.строк: ");
    scanf("%d",&m);
    printf("Введите кол.столбцов: ");
    scanf("%d",&n);
    int **a=malloc(sizeof(int*)*m);
    for(i=0;i<m;i++)
    {
        a[i] = malloc(n * sizeof(int));
        for(j=0;j<n;j++)
        {
            a[i][j]=1+rand()%10;
            printf("%d ",a[i][j]);
        }
        printf("\n");
    }
    printf("\n");
    int* v;
    v = calloc(m , sizeof(int));
    v=p(m,n,a);
    //p(m,n,a);
    for(i=0;i<m;i++)
    {
        printf("%d=%d \n",i+1,v[i]);
    }
    for (i = 0; i < m; i++)
        free(a[i]);
    free(a);
    return 0;
}
