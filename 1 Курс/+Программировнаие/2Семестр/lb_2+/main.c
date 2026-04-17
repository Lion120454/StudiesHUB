#include <stdio.h>
#include <conio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include <math.h>
char *top(char arr){//строчную букву делает заглавной
    if(arr == 'Є')
        return '®';
    if((arr >= 97 && arr <= 122)||(arr >= 'а' && arr <= '€'))
        return arr - 32;
}
char *stoupper(char *arr){//все буквы в строке делает заглавными
    char *str = malloc(strlen(arr));
    for(int i = 0; i < strlen(arr); i++)
    {
        str[i] = top(arr[i]);
    }
    return str;
}
//-----------------------------------------------------------------------------------------------------------------
int per(char *str){//переводит строку в которой записано число символами в число int
    int s = 0, a = 0, num = 0;
    if(((str[0] < 48 || str[0] > 57)&&(str[1] < 48 || str[1] > 57)))
        return 0;
    if(str[0] == 45 || str[0] == 43)
        a = 1;
    for(int i = a; i < strlen(str); i++){
        if(str[i] >= 48 && str[i] <= 57){
            s++;
        }
        else{
            break;
        }
    }

    char strnum[s];//создание нового массива который содержит только цифры из строки

    for(int i = 0; i < s; i++){
        strnum[i] = str[i+a];
    }

    for(int i = 0; i < s; i++){
        num = num + (strnum[i] - 48) * pow(10, s-i-1);
    }
    if(a == 1 && str[0] == 45)
        num = num * -1;
    return num;
}
//-----------------------------------------------------------------------------------------------------------------
char *numtos(int num){//переводит число int в строку
    int i = num, length = 0;
    while(i!=0){
        length++;
        i = i/10;
    }
    char *str = malloc(length+1);
    if(num > 0){
        sprintf(str, "%c %i", '+', num);
    }
    if(num < 0){
        num = num * -1;
        sprintf(str, "%c %i", '-', num);
    }
    if(num == 0){
        str[0]='0';
    }
    return str;
}
//-----------------------------------------------------------------------------------------------------------------
char *bintodec(char *bin){//перевод двоичной строки в 10чное число
    strrev(bin);//разворот строки
    int d = 0;
    for(int i = 0;i < strlen(bin); i++){
        if(bin[i] == '1')
        d = d + pow(2, i-1);
    }

    int j = d, length = 0;
    while(j!=0){//подсчет длины 10чного числа
        length++;
        j = j/10;
    }

    char *str = malloc(length);
    sprintf(str, "%i", d);//перевод числа в строку
    return str;
}

int main(){
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    setlocale(LC_ALL, "Rus");
    int a, c;
    char arr[100];
    while(1){
    printf("1 - stoupper\n");
    printf("2 - stonum\n");
    printf("3 - numtos\n");
    printf("4 - bintodec\n");
    scanf("%i", &c);
    switch(c){
        case 1:
            printf("¬ведите строку:\n");
            getch();
            fgets(arr, 100, stdin);
            fgets(arr, 100, stdin);
            char *str = stoupper(arr);
            printf("%s\n", str);
            break;
        case 2:
            printf("¬ведите строку:\n");
            fgets(arr, 100, stdin);
            fgets(arr, 100, stdin);
            printf("%i\n", per(arr));
            break;
        case 3:
            printf("¬ведите число:\n");
            scanf("%i", &a);
            char *str1 = numtos(a);
            printf("%s\n", str1);
            break;
        case 4:
            printf("¬ведите двоичную строку:\n");
            fgets(arr, 100, stdin);
            fgets(arr, 100, stdin);
            char *str2 = bintodec(arr);
            printf("%s\n", str2);
            break;
    }
    printf("\n");
    }
    return 0;
}
