#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>

typedef struct
{
    char n[10];
    char f[10];
    int r;
}Decimal;

Decimal summarize(Decimal number[3])
{
    int n,n1,n2,f,f1,f2,r1,r2,c,c1,k=0,q=0;
    n1=atoi(number[0].n);
    n2=atoi(number[1].n);
    f1=atoi(number[0].f);
    f2=atoi(number[1].f);
    r1=pow(10, number[0].r);
    r2=pow(10, number[1].r);
    if(number[0].r>number[1].r)
    {
        for(int i=number[1].r;i<number[0].r;i++)
        {
            f2=f2*10;
            r2=r2*10;
        }
    }
    if(number[0].r<number[1].r)
    {
        for(int i=number[0].r;i<number[1].r;i++)
        {
            f1=f1*10;
            r1=r1*10;
        }
    }
    n=n1+n2;
    f=f1+f2;
    if(f>r1)
    {
        n++;
        f=f-r1;
    }
    c1=f;
    c=0;
    for(int i=0;c1>0;i++)
    {
        c1=c1/10;
        c++;
    }
    if(c!=number[0].r||c!=number[1].r)
    {
        char p[20];
        k++;
        sprintf(p, "%d", f);
        if(number[0].r>number[1].r)
        {
            c1=number[0].r-c;
        }
        if(number[0].r<number[1].r)
        {
            c1=number[1].r-c;
        }
        if(number[0].r==number[1].r)
        {
            c1=number[0].r-c;
        }
        q=0;
        for(int i=0;i<number[0].r+1;i++)
        {
            if(i<c1)
            {
                number[3].f[i]='0';
            }
            if(i>=c1)
            {
                number[3].f[i]=p[q];
                q++;
            }
        }
    }
    if(k==0)
    {
        sprintf(number[3].f, "%d", f);
    }
    sprintf(number[3].n, "%d", n);
    printf("%s,%s",number[3].n,number[3].f);
}

Decimal subtract(Decimal number[3])
{
    int n,n1,n2,f,f1,f2,r,r1,r2,c,c1,m=0,q=0;
    n1=atoi(number[0].n);
    n2=atoi(number[1].n);
    f1=atoi(number[0].f);
    f2=atoi(number[1].f);
    r1=pow(10, number[0].r);
    r2=pow(10, number[1].r);
    if(number[0].r>number[1].r)
    {
        for(int i=number[1].r;i<number[0].r;i++)
        {
            f2=f2*10;
            r2=r2*10;
            r=number[0].r;
        }
    }
    if(number[0].r<number[1].r)
    {
        for(int i=number[0].r;i<number[1].r;i++)
        {
            f1=f1*10;
            r1=r1*10;
            r=number[1].r;
        }
    }
    if(number[0].r==number[1].r)
    {
        r=number[0].r;
    }
    if(n1>n2)
    {
        n=n1-n2;
        if(f1>f2)
        {
            f=f1-f2;
        }
        if(f1<f2)
        {
            f=f2-f1;
            f=r1-f;
            n--;
        }
    }
    if(n1<n2)
    {
        n=n2-n1;
        n=n*-1;
        if(f1>f2)
        {
            f=f1-f2;
            f=r1-f;
            n++;
        }
        if(f1<f2)
        {
            f=f2-f1;
        }
    }
    if(n1==n2)
    {
        n=n1-n2;
        if(f1>f2)
        {
            f=f1-f2;
        }
        if(f1<f2)
        {
            f=f2-f1;
            m++;
        }
    }
    c1=f;
    c=0;
    for(int i=0;c1>0;i++)
    {
        c1=c1/10;
        c++;
    }
    q=0;
    if(c!=r)
    {
        char p[20];
        sprintf(p, "%d", f);
        if(number[0].r>number[1].r)
        {
            c1=number[0].r-c;
        }
        if(number[0].r<number[1].r)
        {
            c1=number[1].r-c;
        }
        if(number[0].r==number[1].r)
        {
            c1=number[0].r-c;
        }
        for(int i=0;i<number[0].r+1;i++)
        {
            if(i<c1)
            {
                number[3].f[i]='0';
            }
            if(i>=c1)
            {
                number[3].f[i]=p[q];
                q++;
            }
        }
    }
    if(c==r)
    {
        sprintf(number[3].f, "%d", f);
    }
    char p1[10];
    if(m==1)
    {
        q=0;
        sprintf(p1, "%d", n);
        number[3].n[0]='-';
        for(int i=1;i<strlen(p1)+1;i++)
        {
            number[3].n[i]=p1[q];
            q++;
        }
    }
    if(m==0)
    {
        sprintf(number[3].n, "%d", n);
    }
    printf("%s,%s",number[3].n,number[3].f);
}

Decimal multiply(Decimal number[3])    //5.3*3.4=18.02
{
    int n1,n2,q1,q2,g=0,m1,m2,m,f,f1,c,b;
    char p1[20];
    char p2[20];
    char p3[20];
    n1=strlen(number[0].n)+strlen(number[0].f);
    n2=strlen(number[1].n)+strlen(number[1].f);
    q1=strlen(number[0].n);
    q2=strlen(number[1].n);
    for(int i=0;i<n1;i++)
    {
        if(i<q1)
        {
            p1[i]=number[0].n[i];
        }
        if(i>=q1)
        {
            p1[i]=number[0].f[g];
            g++;
        }
    }
    g=0;
    for(int i=0;i<n2;i++)
    {
        if(i<q2)
        {
            p2[i]=number[1].n[i];
        }
        if(i>=q2)
        {
            p2[i]=number[1].f[g];

            g++;
        }
    }
    p2[n2]='\0';
    m1=atoi(p1);
    m2=atoi(p2);
    m=m1*m2;
    b=m;
    c=0;
    for(int i=0;b>0;i++)
    {
        b=b/10;
        c++;
    }
    f=c-number[0].r-number[1].r;
    sprintf(p3, "%d", m);
    if(p3[c-1]=='0')
    {
        p3[c-1]='\0';
    }
    g=0;
    if(f==0)
    {
        sprintf(number[3].n, "%d", g);
        sprintf(number[3].f, "%d", m);
    }
    if(f>0)
    {
        for(int i=0;i<c;i++)
        {
            if(i<f)
            {
                number[3].n[i]=p3[i];
            }
            if(i>=f)
            {
                number[3].f[g]=p3[i];
                g++;
            }
        }
        number[3].n[f]='\0';
    }
    if(f<0)
    {
        f1=f*-1;
        sprintf(number[3].n, "%d", g);
        for(int i=0;i<number[0].r+number[1].r;i++)
        {
            if(i<f1)
            {
                number[3].f[i]='0';
            }
            if(i>=f1)
            {
                number[3].f[i]=p3[g];
                g++;
            }
        }
    }
    printf("%s,%s",number[3].n,number[3].f);
}

int main()
{
    setlocale (LC_CTYPE, "RUSSIAN");
    int k=0,q=0,c;
    char num[20];
    Decimal number[3];
    for(int i=0;i<2;i++)
    {
        k=0;
        printf("¬ведите %d число : \n", i + 1);
        scanf("%s", &num);
        for(int j=0;num[j]!=',';j++)
        {
            k++;
        }
        number[i].r=strlen(num)-k-1;
        for(int j=0;j<k;j++)
        {
            number[i].n[j] = num[j];
        }
        number[i].n[k]='\0';
        q=0;
        k++;
        for(int j=k;j<strlen(num);j++)
        {
            number[i].f[q] = num[j];
            q++;
        }
    }
    printf("\n+:");
    summarize(number);
    getch();
    printf("\n-:");
    subtract(number);
    getch();
    printf("\n*:");
    multiply(number);
    getch();
    getch();
    return 0;
}
