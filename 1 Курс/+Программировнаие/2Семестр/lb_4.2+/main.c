#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
typedef struct
{
        char N[25];
        int R;
        int K;
}Srav;

char  *sr(int n,Srav tovar[n],char *t1,char *t2)
{
    int q1,q2;
    for(int i;i<n;i++)
    {
       if(strcmp (tovar[i].N, t1)==0)
        {
            q1=i;
        }
       if(strcmp (tovar[i].N, t2)==0)
        {
            q2=i;
        }
    }
    if(tovar[q1].R>tovar[q2].R)
    {
        return tovar[q1].N;
    }
    if(tovar[q1].R<tovar[q2].R)
    {
        return tovar[q2].N;
    }
    if(tovar[q1].R==tovar[q2].R)
    {
        if(tovar[q1].K>tovar[q2].K)
        {
            return tovar[q1].N;
        }
        if(tovar[q1].K<tovar[q2].K)
        {
            return tovar[q2].N;
        }
    }
}

int main()
{
    //SetConsoleCP(1251);
    //SetConsoleOutputCP(1251);
    system("chcp 1251");
    system("cls");
    int n;
    printf("Введите кол. товаров: ");
    scanf("%d",&n);
    Srav tovar[n];
    for (int i = 0; i<n; i++)
    {
        printf("Введите %d название товара : ", i + 1);
        scanf("%s", tovar[i].N);
        printf("Введите %d Цену в рублях : ", i + 1);
        scanf("%d", &tovar[i].R);
        printf("Введите %d Цену в копейках : ", i + 1);
        scanf("%d", &tovar[i].K);
    }
    char t1[25];
    char t2[25];
    printf("Введите 1 товар для сравнения: ");
    scanf("%s",t1);
    printf("Введите 2 товар для сравнения: ");
    scanf("%s",t2);
    char *o=sr(n,tovar,t1,t2);
    printf("Самый дорогой товар: %s",o);
    getch();
    return 0;
}
