#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
int tw(int k,int n)
{
    int i,j,g,s=0,t;
    for(i=0;i<k;i++)
    {
        t=0;
        for(j=0;j<n;j++)
        {
            g=1+rand()%5;
            printf("%d ",g);
            if(t==0&&g==2)
            {
                s++;
                t++;
            }
        }
        printf(" \n");
    }
    printf("Число наборов %d",s);
}

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int k=3,n=4;
    tw(k,n);
    getch();
    return 0;
}
