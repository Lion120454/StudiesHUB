#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <dos.h>
#include <locale.h>
typedef struct
{
    char str[100];
}fs;

int In(int x,int k)
{
    fs pr[k];
    FILE *file1;
    FILE *file2;
    int g=0,i=0;
    x=x+5;
    if((file1 = fopen("F.txt","r"))==NULL||(file2 = fopen("G.txt","w"))==NULL)
    {
        printf("Не удалось открыть файлы\n");
        return;
    }
    else
    {
        printf("Удалось открыть файлы\n");
    }
    while(fgetc(file1) != EOF)
    {
        if(g>=x)
        {
            fgets(pr[i].str, 80, file1);
            i++;
        }
        g++;
    }
    for(int j=0;j<i;j++)
    {
        fputs(pr[j].str,file2);
    }
    fclose(file1);
    fclose(file2);
}

int main()
{
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    setlocale(LC_ALL, "Rus");
    int c=0;
    FILE *file;
    char s[100];
    if((file = fopen("F.txt","r"))==NULL)
    {
        printf("Не удалось открыть файл\n");
        return;
    }
    else
    {
        printf("Удалось открыть файл\n");
    }

    int max=0,x=0,k=0;
    while(fgetc(file) != EOF)
    {
        c=0;
        fgets(s, 80, file);
        for(int i=0;i<strlen(s);i++)
        {
            if(s[i]==' '&&s[i+1]==' ')
            {
                c++;
            }
            if(max<c)
            {
                max=c;
                x=k;
            }
            k++;
        }
    }
    printf("k=%d\n",k);
    printf("max=%d\n",max);
    fclose(file);
    In(x,k);
    getch();
    return 0;
}
