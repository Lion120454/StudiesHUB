#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int n,j=1,i;
    printf("¬ведите размер массива: \n");
    scanf("%d",&n);
    int m[n];
    for(i=0;i<n;i++)
    {
        m[i]=1 + rand()%20;
        printf(" %d",m[i]);
    }
    printf("\n");
    for(i=0;i<n/2;i++)
    {
        m[i] = m[i] + m[n - j];
        m[n - j] = m[i] - m[n - j];
        m[i] = m[i] - m[n - j];
        j++;
    }
    for(i=0;i<n;i++)
    {
        printf(" %d",m[i]);
    }
    getch();
    return 0;
}
