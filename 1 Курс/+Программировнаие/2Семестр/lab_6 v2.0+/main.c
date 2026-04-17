#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include <stdbool.h>

typedef struct
{
    char surname[100];
    char number[100];
    char uslessButNeeded[50];
    char uslessButNeeded_2[50];
    char uslessButNeeded_3[50];
}book;

int countStr()
{
    FILE* bk;
    while((bk=fopen("Book.txt", "r"))==NULL)
    {
        perror("\nError. Не удалось открыть файл\t\n");
        return EXIT_FAILURE;
    }

    size_t counter = 0;
    int ch, pre = EOF;

    while ( ( ch = fgetc( bk ) ) != EOF )
    {
        pre = ch;

        if ( ch == '\n' )
        {
         counter++;
        }
    }

    if ( pre == EOF )
        puts( "Файл пуст" );
    else if ( pre != '\n'  )
    {
        counter++;
    }
    fclose(bk);
    return (counter);
}


void fileReedOpen(book *book)
{
    FILE* bk;
    int j=0;
    while((bk=fopen("Book.txt", "r"))==NULL)
        printf("\nError. Не удалось открыть файл\t\n");
    while (!feof(bk))
    {
        fscanf(bk, "%s %s %s %s %s", book[j].uslessButNeeded, book[j].surname, book[j].uslessButNeeded_2, book[j].uslessButNeeded_3, book[j].number);
        j++;
    }
    fclose(bk);
}

char addcont(book *book, int i)
{
    int count;
    char choose;
    for (int j=i; ; j++)
    {
        count=j;
        printf("\nДобавить новый контакт д/н?\n");
        scanf("%c",&choose); getchar();
        switch (choose)
        {
        case 'д':
        {
            printf("\nВведите фамилию: ");
            gets(book[j].surname);
            printf("Введите номер: ");
            gets(book[j].number);
            break;
        }
        case 'н':
        {
            break;
        }
        default:
            printf("\Ошибка\n");
        }
        if (choose=='н')
            break;
    }

    printf("\n\n\tТелефонная книга:\n");

    for (int j=0; j<count; j++)
    {
        if (((strcmp(book[j].surname,"0"))==0) && ((strcmp(book[j].number,"0"))==0))
        {
            count=count-1;
        }
        if (((strcmp(book[j].surname,"0"))!=0) && ((strcmp(book[j].number,"0"))!=0))
        {
            printf("Фамилия:%s, Номер:%s\n",book[j].surname,book[j].number);
        }
    }
    printf("Телефонная книга содержит: %d контакты \n\n",count);

    return (count);
}

void findsurname(book *book, int i)
{
    bool flag=false;
    int index;
    char surname[100];
    gets(surname);
    for (int j=0; j<i; j++)
    {
        if ((strcmp(surname,((book[j].surname))))==0)
        {
            flag=true;
            index=j;
            break;
        }
    }

    if (flag==true)
    {
        printf("\n%s is in Телефонная книга\n\n",surname);
        printf("\tИнформация о человеке:\n");
        printf("Фамилия: %s Номер телефона: %s\n",book[index].surname,book[index].number);
    }
    else
        printf("\nЧеловек не найден\n");
}

void findnumber(book *book, int i)
{
    int index;
    bool flag=false;
    char number[100];
    gets(number);
    for (int j=0; j<i; j++)
    {
        if ((strcmp(number,((book[j].number))))==0)
        {
            flag=true;
            index=j;
            break;
        }
    }
    if (flag==true)
    {
        printf("\nЧеловек с этим номером: %s находится в телефонной книге\n\n",number);
        printf("\tИнформация:\n");
        printf("Фамилия: %s Номер телефона: %s\n",book[index].surname,book[index].number);
    }
    else
        printf("\nЧеловек не найден\n");
}

void delcont(book *book, int i)
{
    int index;
    bool flag=false;
    char surname[100], choose;
    gets(surname);
    for (int j=0; j<i; j++)
    {
        if ((strcmp(surname,((book[j].surname))))==0)
        {
            flag=true;
            index=j;
            break;
        }
    }
    if (flag==true)
    {
            printf("\nУдалить контакт %s? д/н\n",book[index].surname);
            scanf("%c",&choose); getchar();
            switch (choose)
            {
            case 'д':
                {
                    strcpy(book[index].surname, "0");
                    strcpy(book[index].number, "0");
                    printf("\nКонтакт был удален \n");
                    break;
                }
            case 'н':
            {
                printf("\nВы отменили удаление контакта %s\n",book[index].surname);
                break;
            }
            default:
                printf("\nОшибка\n");
            }
    }
    else
        printf("\nЧеловек не найден\n");
}

void surnameChange(book *book, int i)
{
    int index;
    bool flag=false;
    char surname[100], choose;
    gets(surname);
    for (int j=0; j<i; j++)
    {
        if ((strcmp(surname,((book[j].surname))))==0)
        {
            flag=true;
            index=j;
            break;
        }
    }
    if (flag==true)
    {
            printf("\nИзменить фамилию контакта %s? д/н\n",book[index].surname);
            scanf("%c",&choose); getchar();
            switch (choose)
            {
            case 'д':
            {
                printf("Введите новую фамилию контакта %s \n",book[index].surname);
                gets(book[index].surname);
                printf("Вы успешно изменили фамилию контакта на %s\n",book[index].surname);
                break;
            }
            case 'н':
            {
                printf("\nВы отменили изменение контакта %s\n",book[index].surname);
                break;
            }
            default:
                printf("\nВвод ошибки\n");
            }
    }
    else
        printf("Человек не найден\n");
}

void numberChange(book *book, int i)
{
    int index;
    bool flag=false;
    char surname[100], choose;
    gets(surname);
    for (int j=0; j<i; j++)
    {
        if ((strcmp(surname,((book[j].surname))))==0)
        {
            flag=true;
            index=j;
            break;
        }
    }
    if (flag==true)
    {
            printf("\nВы хотите изменить контактный номер %s? д/н\n",book[index].surname);
            scanf("%c",&choose); getchar();
            switch (choose)
            {
            case 'д':
            {
                printf("Введите новый номер для %s \n",book[index].surname);
                gets(book[index].number);
                printf("Контактный номер изменен на %s\n",book[index].number);
                break;
            }
            case 'н':
            {
                printf("\nВы отменили изменение контакта %s\n",book[index].surname);
                break;
            }
            default:
                printf("\nВвод ошибки\n");
            }
    }
    else
        printf("Человек не найден\n");
}

//bool sravnenie(int i; int j; book *book)
//{
//    if(strlen(book[i].surname) < strlen(book[j].surname))
//    {
//        for(int k=0; k < strlen(book[i].surname); k++)
//        {
//            if(book[i].surname[k]);
//
//        }
//
//    }
//}

void sort_book(book* book)
{
    int i,j,k,l,tmp;
    char str1[30];
    char str2[30];
    char str3[30];
    for (i = 0; i < sizeof(book)/sizeof(book[0]) - 1 ; i++)
    {
        for (j = i+1; j < sizeof(book)/sizeof(book[0]); j++)
        {
            strcpy(str1,book[i].surname);
            strcpy(str2,book[j].number);
            k = 0;
            while ((k < strlen(str1))||( k < strlen(str2)))
            {
                if ((int)str1[k] > (int)str2[k])
                {
                    strcpy(book[i].surname,str2);
                    strcpy(book[j].surname,str1);
                    strcpy(str3, book[i].number);
                    strcpy(book[i].number, book[j].number);
                    strcpy(book[j].number, str3);
                    break;
                } else
                {
                    if ((int)str1[k] < (int)str2[k]) {break;}
                }
                k++;
            }
        }
    }
}
int main()
{
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    book book[100];
    int count=countStr();
    fileReedOpen(book);

    int chooseCase;

    do
    {
    printf("\n \n"
           "1 - Добавить новый контакт \n"
           "2 - Найти контакт по фамилии \n"
           "3 - Найти контакт по номеру \n"
           "4 - Удалить контакт \n"
           "5 - Изменить фамилию существующего контакта \n"
           "6 - Изменить номер телефона существующего контакта\n"
           "7 - Показать список контактов\n"
           "8 - Сохранить файл\n"
           "9 - Завершить работу\n\n");
    scanf("%d",&chooseCase); getchar();
    switch (chooseCase)
    {
        case 1:
    {
            printf("\nДобавить новый контакт\n");
            count=addcont(book, count);
            break;
    }
        case 2:
        {
            printf("\nВведите фамилию контакта, который вы хотите найти\n");
            findsurname(book, count);
            break;
        }
        case 3:
        {
            printf("\nВведите номер телефона контакта, который вы хотите найти\n");
            findnumber(book, count);
            break;
        }
        case 4:
        {
            printf("\nВведите фамилию контакта, который вы хотите удалить\n");
            delcont(book,count);
            break;
        }
        case 5:
        {
            printf("\nВведите фамилию контакта, который вы хотите изменить\n");
            surnameChange(book,count);
            break;
        }
        case 6:
        {
            printf("\nВведите фамилию контакта, номер которого вы хотите изменить\n");
            numberChange(book,count);
            break;
        }
        case 7:
        {
            printf("\n\tСписок контактов:\n");
            int change=0;
            for (int j=0; j<count; j++)
            {
                if (((strcmp(book[j].surname,"0"))==0) && ((strcmp(book[j].number,"0"))==0))
                {
                    change++;
                    continue;
                }
                if (((strcmp(book[j].surname,"0"))!=0) && ((strcmp(book[j].number,"0"))!=0))
                {
                    printf("Фамилия: %s, Номер: %s\n",book[j].surname,book[j].number);
                }
            }
            printf("Телефонная книга в настоящее время содержит: %d контакты\n",count-change);
            break;
        }
        case 8:
        {
            FILE* file;
            file=fopen("Book.txt", "w");
            FILE* fileP;
            fileP=fopen("PhoneBook.txt", "w");

            int change=0;
            for (int j=0; j<count; j++)
            {
                if (((strcmp(book[j].surname,"0"))==0) && ((strcmp(book[j].number,"0"))==0))
                {
                    change++;
                    continue;
                }
            }
            int i,j,k,l;
            char str1[30];
            char str2[30];
            char str3[30]={};
            for (i = 0; i < count-change - 1 ; i++)
            {
                for (j = i+1; j < count-change; j++)
                {
                    strcpy(str1,book[i].surname);
                    strcpy(str2,book[j].surname);
                    k = 0;
                    while ((k < strlen(str1))||( k < strlen(str2)))
                    {
                        if ((int)str1[k] > (int)str2[k])
                        {
                            strcpy(book[i].surname,str2);
                            strcpy(book[j].surname,str1);
                            strcpy(str3,book[i].number);
                            strcpy(book[i].number,book[j].number);
                            strcpy(book[j].number,str3);
                            break;
                        } else
                        {
                            if ((int)str1[k] < (int)str2[k]) {break;}
                        }
                        k++;
                    }
                }
            }
            for (int j=0; j<count; j++)
            {
                 if (((strcmp(book[j].surname,"0"))==0) && ((strcmp(book[j].number,"0"))==0))
                 {
                     continue;
                 }
                 if (((strcmp(book[j].surname,"0"))!=0) && ((strcmp(book[j].number,"0"))!=0))
                 {
                     if (j+1==count)
                     {
                          fprintf(file,"Фамилия: %s \t\t\t\t\t|\t Номер: %s",book[j].surname,book[j].number);
                          break;
                     }
                    fprintf(file,"Фамилия: %s \t\t\t\t\t|\t Номер: %s\n",book[j].surname,book[j].number);
                 }
            }

            char ew[1]={};
            ew[0] = book[0].surname[0];
            int flag = 1;
            for (int j=0; j<count-change; j++)
            {
                 if (((strcmp(book[j].surname,"0"))==0) && ((strcmp(book[j].number,"0"))==0))
                 {
                     continue;
                 }
                 if (((strcmp(book[j].surname,"0"))!=0) && ((strcmp(book[j].number,"0"))!=0))
                 {
                     if (j+1==count)
                     {
                          fprintf(fileP,"Фамилия: %s \t\t\t\t\t|\t Номер: %s",book[j].surname,book[j].number);
                          break;
                     }
                     if((book[j].surname[0] == ew[0]) && (flag==1))
                     {
                         fprintf(fileP,"\n\t\t\t\t\tСтраница <%s>\n", ew);
                         flag=0;
                     }
                     if(book[j].surname[0] != ew[0])
                     {
                         ew[0] = book[j].surname[0];
                         fprintf(fileP,"\n\t\t\t\t\tСтраница <%s>\n", ew);
                     }
                    fprintf(fileP,"Фамилия: %s \t\t\t\t\t|\t Номер: %s\n",book[j].surname,book[j].number);
                 }
            }
            puts ("Файл сохранен");
            fclose(file);
            fclose(fileP);
            break;
        }
        case 9:
        {
            return 1;
        }
    }
    }while(chooseCase!=9);
    return 0;
}
