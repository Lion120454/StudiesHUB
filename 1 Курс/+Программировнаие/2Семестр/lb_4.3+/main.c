#include <stdlib.h>
#include <locale.h>
#include <string.h>
typedef struct
{
        char S[25];
        char N[100];
}Pbook;

char  ps(int n,char *p,Pbook contact[n])
{
    for(int i=0;i<n;i++)
    {
        if(strcmp (contact[i].S, p)==0)
        {
            printf("%s\n",contact[i].N);
        }
    }
}
char  pn(int n,char *p,Pbook contact[n])
{
    for(int i=0;i<n;i++)
    {
        if(strcmp (contact[i].N, p)==0)
        {
            printf("%s\n",contact[i].S);
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
    printf("Введите кол. контактов: ");
    scanf("%d",&n);
    char p[25];
    Pbook contact[n];
    for (int i = 0; i<n; i++)
    {
        printf("Введите %d Фамилию : ", i + 1);
        scanf("%s", contact[i].S);
        printf("Введите %d Номер : ", i + 1);
        scanf("%s", contact[i].N);
    }
    int c;
    while(1)
    {
        printf("1 - Поиск по фамилии\n2 - Поиск по Номеру\n");
        scanf("%i", &c);
        switch(c)
        {
        case 1:
            printf("Введите Фамилию:");
            scanf("%s",p);
            ps(n,p,contact);
            break;
        case 2:
            printf("Введите Номер:");
            scanf("%s",p);
            pn(n,p,contact);
            break;
        }
    }
    getch();
    return 0;
}
