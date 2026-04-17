#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int m,n,i,j,s=0,max=0,min=100,x1=0,y1=0,x2=0,y2=0;
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
    for(i=0;i<m;i++)
    {
        max=0;
        min=100;
        for(j=0;j<n;j++)
        {
            if(a[i][j]<min)
            {
                min=a[i][j];
                x2=i;
                y2=j;
            }
        }

        for(j=0;j<n;j++)
        {
            if(a[i][j]>max)
            {
              max=a[i][j];
              x1=i;
              y1=j;
            }
        }
        a[x1][y1]=min;
        a[x2][y2]=max;
    }

    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            printf("%d ",a[i][j]);
        }
        printf(" \n");
    }
    return 0;
}
