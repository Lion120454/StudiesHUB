#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <locale.h>
int o(int n)
{
    int i,s=0,g;
    float max=20.00,min= 5 ,h;
    for(i=0;i<n;i++)
    {
        h=(float) rand() / RAND_MAX * (max - min) + min;
        g=roundf(h);
        printf("%.2f= %d \n ",h,g);
        s=s+g;
    }
    printf("—умма %d",s);
}

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int n,i,s=0,g;
    printf("¬ведите число \n");
    scanf("%d",&n);
    o(n);
    getch();
    return 0;
}
