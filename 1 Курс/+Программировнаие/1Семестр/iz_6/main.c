#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int m,n,i,j,s=0;
    printf("¬ведите число столбцов \n");
    scanf("%d",&m);
    printf("¬ведите число строк \n");
    scanf("%d",&n);
    int a[m][n];
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
        a[i][j]=1 + rand()%20;
        printf("%d ",a[i][j]);
        }
        printf(" \n");
    }
    printf(" \n");
    for(j=0;j<n;j=j+2)
    {
        s=0;
        for(i=0;i<m;i++)
        {
            s=s+a[i][j];
        }
        printf("s%d=%d \n",j,s);
    }
    return 0;
}
