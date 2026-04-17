#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>

typedef struct
{
    char plat[25];
    char pol[25];
    double sum;
}schet;

int Out(int n,schet order[n],char *p)
{
    int k=0;
    for(int i=0;i<n;i++)
    {
        if(strcmp (order[i].plat, p)==0)
        {
            printf("—о счЄта %s была сн€та сумма в размере %d и была переведена на счЄт %s\n",order[i].plat,order[i].sum,order[i].pol);
            k=1;
        }
    }
    if(k=0)
    {
        printf("»звените,такого счЄта нет(");
    }
}

int main()
{
    system("chcp 1251");
    system("cls");
    int n;
    printf("¬ведите кол. счетов");
    scanf("%d",&n);
    schet order[n];
    for(int i=0;i<n;i++)
    {
        printf("¬ведите %d счЄт плательщика : ", i + 1);
        scanf("%s", &order[i].plat);
        printf("¬ведите %d счЄт получател€ : ", i + 1);
        scanf("%s", &order[i].pol);
        printf("¬ведите %d сумму перевода : ", i + 1);
        scanf("%d", &order[i].sum);
    }
    char p[25];
    printf("¬ведите счЄт искомого получател€:" );
    scanf("%s",p);
    Out(n,order,p);
    getch();
    return 0;
}
