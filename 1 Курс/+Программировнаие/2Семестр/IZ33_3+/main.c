#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
int** zam(int n,int m,int a[n][m])
{
int i,j,max,min,x1,x2,y1,y2;
for(i=0;i<n;i++)
{
    max=a[i][0];
    min=a[i][0];
    for(j=0;j<m;j++)
    {
        if(a[i][j]<min)
        {
            min=a[i][j];
            x1=i;
            y1=j;
        }
        if(a[i][j]>max)
        {
            max=a[i][j];
            x2=i;
            y2=j;
        }
    }
    a[x1][y1]=max;
    a[x2][y2]=min;
}
printf(" \n");
for(i=0;i<n;i++)
    {
        for(j=0;j<m;j++)
        {
            printf(" %d",a[i][j]);
        }
        printf(" \n");
    }

}
int main()
{
    setlocale(LC_ALL, "Rus");
    int i,j,n,m;
    printf("¬ведите n \n");
    scanf("%d",&n);
    printf("¬ведите m \n");
    scanf("%d",&m);
    int a[n][m];
    for(i=0;i<n;i++)
    {
        for(j=0;j<m;j++)
        {
            a[i][j]=1+rand()%50;
            printf(" %d",a[i][j]);
        }
        printf(" \n");
    }
    zam(n,m,a);
    getch();
    return 0;
}
