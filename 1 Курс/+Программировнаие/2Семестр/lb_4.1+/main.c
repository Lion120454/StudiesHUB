#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
typedef struct
{
        char S[25];
        char C[25];
}Poisk;

void  ps(int n,char *p,Poisk city[n])
{
    for(int i=0;i<n;i++)
    {
        if(strcmp (city[i].S, p)==0)
        {
            printf("%s\n",city[i].C);
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
    printf("Введите кол. стран: ");
    scanf("%d",&n);
    char p[25];
    Poisk city[n];
    for (int i = 0; i<n; i++)
    {
        printf("Введите %d Страну : ", i + 1);
        scanf("%s", city[i].S);
        printf("Введите %d Город : ", i + 1);
        scanf("%s", city[i].C);
    }
    printf("Введите Страну:");
    scanf("%s",p);
    ps(n,p,city);
    getch();
    return 0;
}
