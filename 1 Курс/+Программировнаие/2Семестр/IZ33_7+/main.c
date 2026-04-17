#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
typedef struct
{
        char S[100];
        char I[100];
        char G[25];
}Poisk;

char  ps(int n,char *p, Poisk anket[n])
{
    for(int i=0;i<n;i++)
    {
        if(strcmp (anket[i].G, p)==0)
        {
            printf("%s.",anket[i].S);
            printf("%s\n",anket[i].I);
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
    printf("Введите кол. студентов: ");
    scanf("%d",&n);
    char p[25];
    Poisk anket[n];
    for (int i = 0; i<n; i++)
    {
        printf("Введите %d Фамилию : ", i + 1);
        scanf("%s", anket[i].S);
        printf("Введите %d Инициалы : ", i + 1);
        scanf("%s", anket[i].I);
        printf("Введите %d Номер группы : ", i + 1);
        scanf("%s", anket[i].G);
    }
    printf("Введите группу:");
    scanf("%s",p);
    ps(n,p,anket);
    getch();
    return 0;
}
