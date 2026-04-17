#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
void deletePS0vS(char *S, char *S0){//удаляет первое вхождение S0 в стоке S
    int sim = 0, p = 0;
    for(int i = 0; i < strlen(S); i++){
        if(S[i] == S0[0]){
           sim = 1;
            for(int j = 0; j < strlen(S0)-1; j++){
                if(S[i+j] != S0[j]){
                    sim = 0;
                }
            }
            if(sim == 1){
                p = i;
                break;
            }
        }
    }
    if(sim == 1){
        for(int i = 0; i < strlen(S0) - 1; i++){
            for(int j = p; j < strlen(S); j++){
                S[j] = S[j+1];
            }
        }

    }
    else{
        printf("Couldn't find substring\n");
    }
    printf("S = %s", S);
}
//-----------------------------------------------------------------------------------------------
void deleteS0vS(char *S, char *S0){//удаляет каждое вхождение S0 в стоке S
    int c = 0, s = 0;
    int *p;
    p = (int*)malloc(0 * sizeof(int));
    for(int i = 0; i < strlen(S); i++){
        if(S[i] == S0[0]){
            s = 1;
            for(int j = 0; j < strlen(S0)-1; j++){
                if(S[i+j] != S0[j]){
                    s = 0;
                }
            }
            if(s == 1){
                p = (int*)realloc(p, c + 1 * sizeof(int));
                p[c] = i;
                c++;
            }
        }
    }

    if(c > 0){
        for(int k = 0; k < c; k++){
            for(int i = 0; i < strlen(S0)-1; i++){
                for(int j = p[k]; j < strlen(S); j++){
                    S[j] = S[j+1];
                }
            }
            for(int l = 0; l < c; l++){
                p[l] = p[l] - strlen(S0) + 1;
            }
        }

    }
    else{
        printf("Error\n");
    }
    printf("S = %s", S);
    free(p);
}
//-----------------------------------------------------------------------------------------------
void zam(char *S, char *S1, char *S2){//заменяет первое вхождение S1 на S2 в стоке S
    int s = 0, p = 0;
    for(int i = 0; i < strlen(S); i++){
        if(S[i] == S1[0]){
            s = 1;
            for(int j = 0; j < strlen(S1)-1; j++){
                if(S[i+j] != S1[j]){
                    s = 0;
                }
            }
            if(s == 1){
                p = i;
                break;
            }
        }
    }
    int d;
    if(strlen(S1) < strlen(S2)){
        d = strlen(S2) - strlen(S1);
        char newS[strlen(S) + d - 1];
        for(int i = 0; i < p; i++){
            newS[i] = S[i];
        }
        for(int i = 0; i < strlen(S2) - 1; i++){
            newS[p + i] = S2[i];
        }
        for(int i = p + strlen(S2) - 1; i < strlen(S) + d - 1; i++){
            newS[i] = S[i - d];
        }
        printf("%s\n", newS);
    }

    if(strlen(S1) > strlen(S2)){
        d = strlen(S1) - strlen(S2);
        for(int i = 0; i < d; i++){
            for(int j = p; j < strlen(S); j++){
                S[j] = S[j + 1];
            }
       }
       for(int i = 0; i < strlen(S2) - 1; i++){
            S[i + p] = S2[i];
        }
        printf("%s\n", S);
    }

    if(strlen(S1) == strlen(S2)){
        for(int i = 0; i < strlen(S1) - 1; i++){
            S[i + p] = S2[i];
        }
        printf("%s", S);
    }

}
//-----------------------------------------------------------------------------------------------
void OutP(char *S){//выводит подстроку находящуюся между 2 первыми пробелами в строке S
    int f, s;
    for(int i = 0; i < strlen(S); i++){
        if(S[i] == ' '){
            f = i;
            s = i;
            break;
        }
    }

    for(int i = f + 1; i < strlen(S); i++){
        if(S[i] == ' '){
            s = i;
            break;
        }
    }
    int d = s - f - 1;
    char sub[d];
    for(int i = 0; i < d; i++){
        sub[i] = S[i + f + 1];
    }
    printf("%s\n", sub);
}

int main()
{
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);
    char S[100];
    char S0[25];
    char S1[25];
    int c;
    while(1){
        printf("1 - deletePS0vS\n2 - deleteS0vS\n3 - zam\n4 - OutP\n");
        scanf("%i", &c);
        switch(c){
        case 1:
            printf("Enter S: \n");
            fgets(S, 100, stdin);
            fgets(S, 100, stdin);
            printf("Enter S0: \n");
            fgets(S0, 25, stdin);
            deletePS0vS(S, S0);
            break;
        case 2:
            printf("Enter S: \n");
            fgets(S, 100, stdin);
            fgets(S, 100, stdin);
            printf("Enter S0: \n");
            fgets(S0, 25, stdin);
            deleteS0vS(S, S0);
            break;
        case 3:
            printf("Enter S: \n");
            fgets(S, 100, stdin);
            fgets(S, 100, stdin);
            printf("Enter S1: \n");
            fgets(S0, 25, stdin);
            printf("Enter S2: \n");
            fgets(S1, 25, stdin);
            zam(S, S0, S1);
            break;
        case 4:
            printf("Enter S: \n");
            fgets(S, 100, stdin);
            fgets(S, 100, stdin);
            OutP(S);
            break;

        }
        printf("\n------------------------------\n");
    }
    return 0;
}
