#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
int** nul(int m,int a[m][m])
{
    int i,j,k=0;
    for(j=0;j<m;j++)
    {
        k++;
        for(i=k;i<m;i++)
        {
            a[i][j]=0;
        }
    }
    return a;
}
int main()
{
    setlocale(LC_ALL, "Rus");
    int i,j,m;
    printf("¬ведите m \n");
    scanf("%d",&m);
    int a[m][m];
    for(i=0;i<m;i++)
    {
        for(j=0;j<m;j++)
        {
            a[i][j]=1+rand()%50;
            printf(" %d",a[i][j]);
        }
        printf(" \n");
    }
    printf(" \n");
    nul(m,a);
    for(i=0;i<m;i++)
    {
        for(j=0;j<m;j++)
        {
            printf(" %d",a[i][j]);
        }
        printf(" \n");
    }
    getch();
    return 0;
}
