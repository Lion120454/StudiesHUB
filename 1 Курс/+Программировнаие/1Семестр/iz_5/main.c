#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
int mp(int m[],int n)
{
    int i,max=0,min=100,x,y;
    for(i=0;i<n;i++)
    {
        if(max<m[i])
        {
            max=m[i];
            x=i;
        }
    }
    for(i=0;i<n;i++)
    {
        if(min>m[i])
        {
            min=m[i];
            y=i;
        }
    }
    for(i=y;i<n-1;i++)
    {
        m[i+1]=m[i]+m[i+1];
        m[i+2]=m[i+1]-m[i];
        m[i+1]=m[i+1]-m[i+2];
    }
    m[y]=0;
    for(i=n+1;i>x+1;i--)
    {
        m[i]=m[i-1];
    }
    m[x+1]=0;
}

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int n,i;
    printf("¬ведите размер массива: ");
    scanf("%d",&n);
    int m[n+2];
    for(i=0;i<n+2;i++)
    {
        m[i]=1+rand()%50;
        printf("%d ",m[i]);
    }
    printf(" \n");
    mp(m,n);
    for(i=0;i<n+2;i++)
    {
        printf("%d ",m[i]);
    }
    getch();
    return 0;
}
