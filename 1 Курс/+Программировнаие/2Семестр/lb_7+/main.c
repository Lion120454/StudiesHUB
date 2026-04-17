#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include <ctype.h>

char* summarize(char* terms[], int n);
char* subtract(char* terms[]);
char* multiply(char* factors[], int n);
int check_str(char* expr);
void removeSigns(char* str);
void deleteMatch(char* s, char* s0);

char* summarize(char* terms[], int n){
    int term1[1024];
    int term2[1024];
    int len_t1, len_t2;
    for (int i = 0; n > 1; ++i) {
        if (terms[0][0] != '-')
            len_t1 = strlen(terms[0]);
        else
            len_t1 = strlen(terms[0]) - 1;
        if (terms[1][0] != '-')
            len_t2 = strlen(terms[1]);
        else
            len_t2 = strlen(terms[1]) - 1;
        if (len_t1 < len_t2) {
            char* buff = malloc(sizeof(*buff) * 1024);
            buff = terms[1];
            terms[1] = terms[0];
            terms[0] = buff;
            int a = 0;
            a = len_t1;
            len_t1 = len_t2;
            len_t2 = a;
        }
        int sign1, sign2;
        len_t1++;
        for (int j = 0; j < len_t1; ++j) {
            if (terms[0][0] == '-') {
                sign1 = 0;
                term1[j + 1] = terms[0][j + 1] - 48;
            } else {
                sign1 = 1;
                term1[j + 1] = terms[0][j] - 48;
            }
        }
        term1[0] = 0;
        for (int j = 0; j < len_t1; ++j) {
            if (terms[1][0] == '-') {
                sign2 = 0;
                if (j < len_t1 - len_t2)
                    term2[j] = 0;
                else
                    term2[j] = terms[1][j - (len_t1 - len_t2) + 1] - 48;
            } else {
                sign2 = 1;
                if (j < len_t1 - len_t2)
                    term2[j] = 0;
                else
                    term2[j] = terms[1][j - (len_t1 - len_t2)] - 48;
            }
        }
        int temp_sum = 0;
        if ((!sign1 && !sign2) || (sign1 && sign2)) {
            for (int j = len_t1 - 1; j > 0; --j) {
                temp_sum = term1[j] + term2[j];
                if (temp_sum < 10) {
                    term1[j] = temp_sum;
                } else {
                    term1[j - 1]++;
                    term1[j] = temp_sum - 10;
                }
            }
            if (sign1 && sign2) {
                if (term1[0] == 0) {
                    for (int i = 0; i < len_t1; ++i)
                        terms[0][i] = term1[i + 1] + 48;
                } else {
                    for (int i = 0; i < len_t1; ++i)
                        terms[0][i] = term1[i] + 48;
                }
                terms[0][len_t1] = '\0';
            } else if (!sign1 && !sign2) {
                if (term1[0] == 0) {
                    for (int i = 0; i < len_t1; ++i)
                        terms[0][i + 1] = term1[i + 1] + 48;
                } else {
                    for (int i = 0; i < len_t1; ++i)
                        terms[0][i + 1] = term1[i] + 48;
                }
                terms[0][0] = '-';
                terms[0][len_t1 + 1] = '\0';
            }
        }
        if ((sign1 && !sign2) || (!sign1 && sign2)) {
            subtract(terms);
        }
        for (int j = 1; j < n - 1; ++j)
            terms[j] = terms[j + 1];
        n--;
    }
    return terms[0];
}

char* subtract(char* terms[]){
    int term1[1024];
    int term2[1024];
    int sign1 = 1, sign2 = 1;
    int sign;
    if (terms[0][0] == '-') {
        sign1 = 0;
        deleteMatch(terms[0], "-");
    }
    if (terms[1][0] == '-') {
        sign2 = 0;
        deleteMatch(terms[1], "-");
    }
    int len_upper, len_lower;
    if (strcmp(terms[0], terms[1]) > 0 || strlen(terms[0]) > strlen(terms[1])) {
        sign = sign1;
        len_upper = strlen(terms[0]);
        len_lower = strlen(terms[1]);
        for (int i = 0; i < len_upper; ++i) {
            term1[i] = terms[0][i] - 48;
            if (i < (len_upper - len_lower)) {
                term2[i] = 0;
            } else {
                term2[i] = terms[1][i - (len_upper - len_lower)] - 48;
            }
        }
    } else {
        len_upper = strlen(terms[1]);
        len_lower = strlen(terms[0]);
        sign = sign2;
        for (int i = 0; i < len_upper; ++i) {
            term1[i] = terms[1][i] - 48;
            if (i < (len_upper - len_lower)) {
                term2[i] = 0;
            } else {
                term2[i] = terms[0][i - (len_upper - len_lower)] - 48;
            }
        }
    }
    for (int i = len_upper - 1; i > (len_upper - len_lower - 1); --i) {
        if (term1[i] < term2[i]) {
            term1[i - 1]--;
            term1[i] += 10;
        }
        term1[i] -= term2[i];
    }
    if (!sign) {
        terms[0][0] = '-';
        if (term1[0] == 0) {
            int i;
            for (i = 0; i < len_upper; ++i) {
                terms[0][i + 1] = term1[i + 1] + 48;
            }
            terms[0][i] = '\0';
        } else {
            int i;
            for (i = 0; i < len_upper; ++i) {
                terms[0][i + 1] = term1[i] + 48;
            }
            terms[0][i + 1] = '\0';
        }
    } else {
        if (term1[0] == 0) {
            int i;
            for (i = 0; i < len_upper; ++i) {
                terms[0][i] = term1[i + 1] + 48;

            }
            terms[0][i - 1] = '\0';
        } else {
            int i;
            for (i = 0; i < len_upper; ++i) {
                terms[0][i] = term1[i] + 48;
            }
            terms[0][i] = '\0';
        }
    }
    return terms[0];
}

char* multiply(char* factors[], int n){
    int factor1[1024], factor2[1024];
    int len_f1, len_f2;
    for (int i = 0; n > 1; ++i) {
        if (factors[0][0] != '-')
            len_f1 = strlen(factors[0]);
        else
            len_f1 = strlen(factors[0]) - 1;
        if (factors[1][0] != '-')
            len_f2 = strlen(factors[1]);
        else
            len_f2 = strlen(factors[1]) - 1;
        if (len_f1 < len_f2) {
            char* buff = malloc(sizeof(*buff) * 1024);
            buff = factors[1];
            factors[1] = factors[0];
            factors[0] = buff;
            int a = 0;
            a = len_f1;
            len_f1 = len_f2;
            len_f2 = a;
        }
        int sign1, sign2;
        len_f1++;
        for (int j = 0; j < len_f1; ++j) {
            if (factors[0][0] == '-') {
                sign1 = 0;
                factor1[j + 1] = factors[0][j + 1] - 48;
            } else {
                sign1 = 1;
                factor1[j + 1] = factors[0][j] - 48;
            }
        }
        factor1[0] = 0;
        for (int j = 0; j < len_f1; ++j) {
            if (factors[1][0] == '-') {
                sign2 = 0;
                if (j < len_f1 - len_f2)
                    factor2[j] = 0;
                else
                    factor2[j] = factors[1][j - (len_f1 - len_f2) + 1] - 48;
            } else {
                sign2 = 1;
                if (j < len_f1 - len_f2)
                    factor2[j] = 0;
                else
                    factor2[j] = factors[1][j - (len_f1 - len_f2)] - 48;
            }
        }
        int temp_mult = 0;
        char* mult_terms[1024];
        char* factor_terms[1024];
        int mult_term[1000];
        int term_len = 0;
        for (int j = len_f1 - 1; j >= len_f1 - len_f2; --j) {
            for (int k = len_f1 - 1; k > 0; --k) {
                temp_mult = factor1[k] * factor2[j];
                if (temp_mult >= 10) {
                    term_len = 2;
                    mult_term[0] = temp_mult / 10;
                    mult_term[1] = temp_mult % 10;
                    for (int t = 2; t < 2 + (len_f1 - k - 1) + (len_f1 - j - 1); ++t) {
                        mult_term[t] = 0;
                        term_len++;
                    }
                    char* new_term1 = malloc(sizeof(new_term1) * 1024);
                    for (int l = 0; l < term_len; ++l) {
                        new_term1[l] = mult_term[l] + 48;
                        new_term1[l + 1] = '\0';
                    }
                    mult_terms[k - 1] = new_term1;
                } else {
                    mult_term[0] = temp_mult;
                    term_len = 1;
                    for (int t = 1; t < 1 + (len_f1 - k - 1) + (len_f1 - j - 1); ++t) {
                        mult_term[t] = 0;
                        term_len++;
                    }
                    char* new_term2 = malloc(sizeof(new_term2) * 1024);
                    for (int l = 0; l < term_len; ++l) {
                        new_term2[l] = mult_term[l] + 48;
                        new_term2[l + 1] = '\0';
                    }
                    mult_terms[k - 1] = new_term2;
                }
            }
            factor_terms[len_f1 - 1 - j] = summarize(mult_terms, len_f1 - 1);

        }
        if ((sign1 && sign2) || (!sign1 && !sign2) )
            factors[0] = summarize(factor_terms, len_f2);
        else if ((!sign1 && sign2) || (sign1 && !sign2)) {
            factors[0][0] = '-';
            strcpy(strstr(factors[0], "-") + 1, summarize(factor_terms, len_f2));
        }
        for (int j = 1; j < n - 1; ++j)
            factors[j] = factors[j + 1];
        n--;
    }
    return factors[0];
}

int check_str(char* str){
    for (int i = 0; str[i] != '\0'; ++i)
        if ((str[i] != '+' && str[i] != '-' && str[i] != '*' && !isdigit(str[i])) ||
            (str[0] == '+' || str[0] == '*' || (str[0] == '-' && str[1] == '-')) ||
            ((str[i] == '-' && str[i + 1] == '+') || (str[i] == '+' && str[i + 1] == '+')) ||
            (str[i] == '-' && str[i + 1] == '-' && str[i + 2] == '-') ||
            (str[i + 1] == '\0' && (str[i] == '-' || str[i] == '+' || str[i] == '*')) ||
            ((str[i] == '*' && str[i + 1] == '+') || (str[i] == '*' && str[i + 1] == '*')) ||
            ((str[i] == '+' && str[i + 1] == '*') || (str[i] == '-' && str[i + 1] == '*'))) {
            printf("Неверное выражение");
            return 0;
        }
    return 1;
}

void removeSigns(char* str){
    for (int i = 0; str[i] != '\0'; ++i) {
        if (str[i] == '-' && str[i + 1] == '-') {
            str[i] = '+';
            for (int j = i + 1; str[j] != '\0'; ++j)
					str[j] = str[j + 1];
        }
        if (str[i] == '+' && str[i + 1] == '-') {
			str[i] = '-';
			for (int j = i; str[j] != '\0'; ++j)
				str[j] = str[j + 1];
		}
    }
    for (int i = 0; str[i] != '\0'; ++i){
        if (*(str + i) == '-' && i != 0 && *(str + i - 1) != '*') {
            char* str_buff = malloc(sizeof(*str_buff) * 1024);
            strcpy(str_buff, str + i);
            strcpy(str + i, "+");
            strcpy(str + i + 1, str_buff);
            free(str_buff);
            i++;
        }
	}
}

void deleteMatch(char* s1, char* s2){
    char* temp = strstr(s1, s2);
    if (temp != NULL) {
        int n = strlen(s2);
        strcpy(temp, temp + n);
    }
}

int main(){
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
    char* str;
    str = malloc(sizeof(*str) * 1024);

    while(1){
    puts("\nВведите выражение: ");
    gets(str);
    removeSigns(str);
    char* terms[1024];
    int num_terms = 0;
    if (check_str(str) == 1) {
        char* term = malloc(sizeof(*term) * 1024);
        term = strtok(str, "+");
        for (num_terms = 0; term != NULL; ++num_terms) {
            terms[num_terms] = term;
            term = strtok(NULL, "+");
        }
        free(term);
    } else main();
    for (int i = 0; i < num_terms; ++i) {
        for (int j = 0; terms[i][j] != '\0'; ++j) {
            if (terms[i][j] == '*') {
                int num_facts = 0;
                char* factors[1024];
                char* factor = malloc(sizeof(*factor) * 1024);
                factor = strtok(terms[i], "*");
                for (num_facts = 0; factor != NULL; ++num_facts) {
                    factors[num_facts] = factor;
                    factor = strtok(NULL, "*");
                }
                free(factor);
                terms[i] = multiply(factors, num_facts);
            }
        }
    }
    printf("Ответ: %s\n", summarize(terms, num_terms));
	}
    free(str);
    return 0;
}
