#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <dos.h>

typedef struct//структура одной записи
{
    char *name;
    char *number;
}phone;
typedef struct//структура страницы записей
{
    phone *note;
    int count;
}page;

page *book = NULL;

int strsim(char *a, char *b)//сравнение строк
{
    if(strlen(a) != strlen(b))//не равны если разная длина
    {
        return 0;
    }
    for(int i = 0; i < strlen(a); i++)//поэлементное сравнение
    {
        if(a[i] != b[i]){
            return 0;
        }
    }
    return 1;
}

int newNote(page *book, char *name, char *number)//создание новой записи
{
    char letter = name[0];//берем первую букву имени записи
    if(letter == -38 || letter == -36 || letter == -6 || letter == -4 || letter == -72 || letter == -88)//исключаем имена, с буквами ь ъ ё
    {
        return -2;
    }
    if(letter > -33)//смещение для имен с букв от а до ъ
    {
        letter = letter - 32;
    }
    if(letter == -37)//ы
    {
        letter--;
    }
    if(letter > -36)//после ь
    {
        letter = letter - 2;
    }
    int page = letter + 64;//определение номера страницы;
    phone *test;
    if(searchNote(book, name, number) != 0)//вызов функции поиска записи для проверки существующего имени/номера
    {
        return 0;
    }

    book[page].count++;//увеличение страницы
    book[page].note = (phone*)realloc(book[page].note, (book[page].count)*sizeof(phone));

    book[page].note[book[page].count - 2].name = (char*)malloc(strlen(name));//определение длины имени и номера новой записи
    book[page].note[book[page].count - 2].number = (char*)malloc(strlen(number));

    strcpy(book[page].note[book[page].count - 2].name, name);//добавление новой записи
    strcpy(book[page].note[book[page].count - 2].number, number);

    return 1;
}

int printPage(page *book, int a){//вывод страницы под номером а
    a = a - 1;
    /*int i, j, b, h = 0, g = 0, B = 0;
    char str[20];
    char str1[20];
    char str2[20];
    for(i = 0; i < book[a].count - 2; i++)
    {
        for(j = i + 1; j < book[a].count - 1; j++)
        {
            if(strcmp(book[a].note[i].name, book[a].note[j].name) > 0)
            {
                strcpy(str, book[a].note[i].name);
                strcpy(book[a].note[i].name, book[a].note[j].name);
                strcpy(book[a].note[j].name, str);

                strcpy(str, book[a].note[i].number);
                strcpy(book[a].note[i].number, book[a].note[j].number);
                strcpy(book[a].note[j].number, str);
            }
            if(strlen(book[a].note[i].name) < strlen(book[a].note[j].name))
            {
                strcpy(str, book[a].note[i].name);
                strcpy(book[a].note[i].name, book[a].note[j].name);
                strcpy(book[a].note[j].name, str);

                strcpy(str, book[a].note[i].number);
                strcpy(book[a].note[i].number, book[a].note[j].number);
                strcpy(book[a].note[j].number, str);
            }
            if(strlen(book[a].note[i].name) > strlen(book[a].note[j].name))
            {
                strcpy(str, book[a].note[j].name);
                strcpy(book[a].note[j].name, book[a].note[i].name);
                strcpy(book[a].note[i].name, str);

                strcpy(str, book[a].note[j].number);
                strcpy(book[a].note[j].number, book[a].note[i].number);
                strcpy(book[a].note[i].number, str);
            }
            if(strcmp(book[a].note[i].name, str1) > 0)
            {
                strcpy(str1, book[a].note[i].name);
                strcpy(str2, book[a].note[i].number);
            }
            if(strcmp(book[a].note[j].name, str1) > 0)
            {
                strcpy(str1, book[a].note[j].name);
                strcpy(str2, book[a].note[j].number);
            }
        }
    }
    for(int s = 0; s < book[a].count - 2; s++)
    {
    if(strcmp(book[a].note[0].name, str1) <= 0)
    {
        for(b = 0; b < book[a].count - 2 - h; b++)
        {
            if(strcmp(book[a].note[b].name, str1) == 0)
            {
                break;
            }
            else
            {
                g++;
            }
        }
        for(g; g < book[a].count - 2 - h; g++)
        {
            strcpy(book[a].note[g].name, book[a].note[g + 1].name);
            strcpy(book[a].note[g].number, book[a].note[g + 1].number);
        }
        strcpy(book[a].note[book[a].count - 2 - h].name, str1);
        strcpy(book[a].note[book[a].count - 2 - h].number, str2);

        strcpy(str1, book[a].note[0].name);
        strcpy(str2, book[a].note[0].number);
        h++;
        g = 0;

        for(b = 0; b < book[a].count - 2 - h; b++)
        {
            if(strcmp(book[a].note[b].name, str1) > 0)
            {
                strcpy(str1, book[a].note[b].name);
                strcpy(str2, book[a].note[b].number);
            }
        }
    }
    }*/
    sort_book(book,a);
    printf("-------------------\n");//разметка

    for(int i = 0; i < book[a].count - 1; i++){//вывод
        printf("%s ", book[a].note[i].name);
        printf("%s\n", book[a].note[i].number);
    }
    printf("-------------------\n");
    return 0;
}

int searchNote(page *book, char *name, char *number)//поиск записи по имени и номеру
{
    char letter = *name;
    if(letter > -33)
    {
        letter = letter - 32;
    }
    if(letter == -37)
    {
        letter--;
    }
    if(letter > -36)
    {
        letter = letter - 2;
    }
    int page = letter + 64;
    if(page < 0 || page > 29)//за пределами страниц
    {
        return 0;
    }

    for(int i = 0; i < book[page].count - 1; i++)//поиск по имени на определенной странице
    {
        if(strcmp(book[page].note[i].name, name) == 0)
        {
            return 1;
        }
    }

    for(int i = 0; i < 30; i++)//поиск по номеру по всей книге
    {
        for(int j = 0; j < book[i].count - 1; j++)
        {
            if(strcmp(book[i].note[j].number, number) == 0)
            {
                return 1;
            }
        }
    }

    return 0;
}

phone* searchByName(page *book, char *name)//поиск по имени
{
    char letter = *name;//определение страницы
    if(letter > -33)
    {
        letter = letter - 32;
    }
    if(letter == -37)
    {
        letter--;
    }
    if(letter > -36)
    {
           letter = letter - 2;
    }
    int page;
    page = letter + 64;
    if(page < 0 || page > 29)//за пределами книги
    {
        printf("Запись не найдена\n");
        return NULL;
    }
    for(int i = 0; i < book[page].count - 1; i++)//поиск и вывод нужной записи
    {
        if(strcmp(book[page].note[i].name, name) == 0)
        {
            printf("%s ", book[page].note[i].name);
            printf("%s\n", book[page].note[i].number);
            return &book[page].note[i];
        }
    }
    printf("Запись не найдена\n");
    return NULL;
}

void deleteNote(page *book, phone note)//удаление записи
{
    char letter = *note.name;//определение страницы
    if(letter > -33)
    {
        letter = letter - 32;
    }
    if(letter == -37)
    {
        letter--;
    }
    if(letter > -36)
    {
        letter = letter - 2;
    }
    int page;
    page = letter + 64;
    int pos;
    for(int i = 0; i < book[page].count - 1; i++)//определение номера удаляемой записи на странице
    {
        if(strcmp(book[page].note[i].name, note.name) == 0)
        {
            pos = i;
        }
    }
    for(int i = pos; i < book[page].count - 2; i++)//смещение записей после удаляемой на 1 влево
    {
        strcpy(book[page].note[i].name, book[page].note[i+1].name);
        strcpy(book[page].note[i].number, book[page].note[i+1].number);
    }
    book[page].count--;//уменьшение количества записей на странице
    book[page].note = (phone*)realloc(book[page].note, book[page].count*sizeof(phone));
}

phone* searchByNumber(page *book, char *number)//поиск по номеру
{
    for(int i = 0; i < 30; i++)//поиск по всей книге
    {
        for(int j = 0; j < book[i].count - 1; j++)
        {
            if(strcmp(book[i].note[j].number, number) == 0)
            {
                printf("%s ", book[i].note[j].name);
                printf("%s\n", book[i].note[j].number);
            return &book[i].note[j];
            }
        }
    }
    printf("Запись не найдена\n");
    return NULL;
}

int editName(page *book, phone note, char *name)//изменить имя записи
{
    char letter = name[0];
    char letter2 = note.name[0];
    char *number;
    strcpy(number, note.number);//изменение имени
    if(letter == letter2)//если первые буквы совпадают, оставляем на этой же странице
    {
        strcpy(note.name, name);
    }
    else//если нет, удаляем и пересоздаем на новой
    {
        deleteNote(book, note);//удаляем
        newNote(book, name, number);//создаем
    }
    return 1;
}

int editNumber(page *book, phone note, char *number)//изменить номер
{
    for(int i = 0; i < 30; i++)//поиск записи по этому номеру
    {
        for(int j = 0; j < book[i].count - 1; j++)
        {
            if(strcmp(book[i].note[j].number, number) == 0)
            {
                return 0;
            }
        }
    }
    strcpy(note.number, number);//если записи с новым номером нет, то изменяем номер
    return 1;
}

void loadFile(page *book)//загрузить файл
{
    FILE *file;//создаем объект для считывания потока из файла
    if((file = fopen("save.txt","r"))==NULL)//проверка на удачность открытия файла
    {
        printf("Не удалось открыть файл\n");
        return;
    }
    else
    {
        printf("Удалось открыть файл\n");
    }
    char str[41];
    char nameStr[20];
    char numStr[20];
    int a = 0, b = 0;
    while(fgetc(file) != EOF)//проходимся по каждой строке открытого файла
    {
        fscanf(file, "%s", &str);//считываем всю строку
        for(int i = 0; i < strlen(str); i++)//делим строку на имя и номер
        {
            if(str[i] == '|')//до символа | это имя, после номер
            {
                a = 1;
                b = i + 1;
                i++;
            }
            if(a == 0)
            {
                nameStr[i] = str[i];
                nameStr[i+1] = '\0';
            }
            if(a == 1)
            {
                numStr[i-b] = str[i];
                numStr[i-b+1] = '\0';
            }
        }
        printf("|%s| ", nameStr);
        printf("|%s|", numStr);
        b = newNote(book, nameStr, numStr);//создаем все записи из файла в памяти массива
        printf("%i\n",b);
        b = 0;
        a = 0;
    }
    printf("Загрузка упешна\n");
    fclose(file);
}
void sort_book(page *book,int a)
{
    printf("s\n");
    int i,j,k,l,tmp;
    char str1[100];
    char str2[100];
    char str3[100];
    for (i = 0; i < book[a].count - 2 ; i++)
    {
        for (j = i;  j < book[a].count - 1; j++)
        {
            strcpy(str1,book[a].note[i].name);
            strcpy(str2,book[a].note[j].number);
            k = 0;
            while ((k < strlen(str1))||( k < strlen(str2)))
            {
                if ((int)str1[k] > (int)str2[k])
                {
                    strcpy(book[a].note[i].name,str2);
                    strcpy(book[a].note[j].name,str1);
                    strcpy(str3, book[a].note[i].number);
                    strcpy(book[a].note[i].number, book[a].note[j].number);
                    strcpy(book[a].note[j].number, str3);
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
void saveFile(page *book)//сохраняем в файл
{
    FILE *file;//открываем поток
    if((file = fopen("save.txt","w"))==NULL)//проверяем файл
    {
        printf("Не удалось открыть файл\n");
        return;
    }
    else{
        system("ClS");
    }
    char str[41];
    int a;
    fprintf(file, "%c", '1');//в начало файла должен быть записан 1 символ на первой строке
    for(int i = 0; i < 30; i++)//проходимся по всей книге
    {
        for(int j = 0; j < book[i].count - 1; j++)
        {
            fprintf(file, "\n%s", book[i].note[j].name);//добавляем имя
            fprintf(file, "%c", '|');
            fprintf(file, "%s", book[i].note[j].number);//добавляем номер
        }
    }
    printf("Успешно сохранено\n");
    fclose(file);
}

int main(){
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    book = (page*) malloc(31*sizeof(page));//определяем заданный глобально массив страниц
    for(int i = 0; i < 31; i++){//каждой странице даем одну пустую запись
        book[i].note = (phone*)malloc((1)*sizeof(phone));
        book[i].count = 1;
    }
    int a, b, res;
    phone *note;
    char number[20];//строки под ввод имени и номера
    char name[20];

    while(1){
        printf("1. Создать запись\n");
        printf("2. Поиск записи по фамилии\n");
        printf("3. Поиск записи по номеру\n");
        printf("4. Открыть страницу\n");
        printf("5. Сохранить\n");
        printf("6. Загрузить\n");
        printf("\n");
        scanf("%i", &a);
        if(a == 1){
            printf("Введите номер телефона\n");
            scanf("%s", &number);
            printf("Введите фамилию\n");
            scanf("%s", &name);
            res = newNote(book, name, number);
            if(res == 1){
                printf("Создание записи успешно\n");
            }
            else{
                printf("Ошибка при создании записи\n");
            }
        }
        else if(a == 2){
            printf("Введите фамилию\n");
            scanf("%s", &name);
            printf("------------------------\n");

            if((note = searchByName(book, name)) != NULL){

                printf("Хотите изменить запись?\n");
                printf("1 - изменить номер\n");
                printf("2 - изменить имя\n");
                printf("3 - удалить\n");
                scanf("%i", &a);
                if(a == 1){
                    printf("Введите новый номер\n");
                    scanf("%s", &number);
                    res = editNumber(book, *note, number);
                    printf("%i", res);
                }
                if(a == 2){
                    printf("Введите новое имя\n");
                    scanf("%s", &name);
                    res = editName(book, *note, name);
                    printf("%i", res);
                }
                if(a == 3){
                    deleteNote(book, *note);
                }
            }
        }
        else if(a == 3){
            printf("Введите номер\n");
            scanf("%s", &number);

            if((note = searchByNumber(book, number)) != 0){
                printf("Хотите изменить запись?\n");
                printf("1 - изменить номер\n");
                printf("2 - изменить имя\n");
                printf("3 - удалить\n");
                scanf("%i", &a);
                if(a == 1){
                    printf("Введите номер\n");
                    scanf("%s", &number);
                    res = editNumber(book, *note, number);
                    printf("%i", res);
                }
                if(a == 2){
                    printf("Введите новое имя\n");
                    scanf("%s", &name);
                    res = editName(book, *note, name);
                    printf("%i", res);
                }
                if(a == 3){
                    deleteNote(book, *note);
                }
            }
        }
        else if(a == 4){
            printf("Введите номер страницы\n");
            scanf("%i", &b);
            a = printPage(book, b);
        }
        else if(a == 5){
            saveFile(book);
        }
        else if(a == 6){
            loadFile(book);
        }
        else{
            system("CLS");
        }
         getch();
        system("CLS");
    }
    return 0;
}
