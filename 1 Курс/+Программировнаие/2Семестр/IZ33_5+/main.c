#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
char *Zam(char *S)
{
    int p=strlen(S)-1,a=0,k=0;
    for(int i = 0; i < strlen(S)-1; i++)
    {
        if(S[i]=='.')
        {
            a++;
        }
    }
    a=a*2;
    int g=strlen(S)-1+a;
    char *m = (char*)malloc(g);
    for(int i=0;i<strlen(S)-1;i++)
    {
        if(S[i]=='.')
        {
           m[k]=S[i];
           m[k+1]=S[i];
           m[k+2]=S[i];
           k=k+3;
        }
        if(S[i]!='.')
        {
            m[k]=S[i];
            k++;
        }
    }return m;
}
//пир.пр.ва.ро
int main()
{
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    char *S = (char*)malloc(100);
    fgets(S,100,stdin);
    printf("%s",Zam(S));
    getch();
    return 0;
}
