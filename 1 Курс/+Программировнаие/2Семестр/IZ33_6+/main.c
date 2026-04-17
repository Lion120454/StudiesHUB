#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include <math.h>

char *bin(char *bin)
{
    strrev(bin);
    int d = 0;
    for(int i = 0;i < strlen(bin); i++)
    {
        if(bin[i] == '1')
        d = d + pow(2, i-1);
    }
    int j = d, length = 0;
    while(j!=0)
    {
        length++;
        j = j/10;
    }
    char *s2 = malloc(length);
    sprintf(s2, "%i", d);
    return s2;
}
int main()
{
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    setlocale(LC_ALL, "Rus");
    char s[100];
    printf("¬ведите двоичную строку:\n");
    fgets(s, 100, stdin);
    char *s2 = bin(s);
    printf("%s\n", s2);
    getch();
}
