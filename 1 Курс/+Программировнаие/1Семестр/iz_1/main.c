#include <stdio.h>
#include <stdlib.h>

int even_dig(int N)
{
int x,i,a=0,a1=0,o=0,j=10,j1=10;
x=N;
do
    {
        x=x/10;
        a++;
    }while(x>0);
    if(a%2==0)
    {
        a1=a/2;
    }
    else
    {
        a1=(a/2)+1;
    }
    for(i=2;i<a;i++)
    {
      j=j*10;
    }
    for(i=2;i<a1;i++)
    {
        j1=j1*10;
    }
    for(i=0;j!=0;i++)
    {
      x = (N / j) % 10;
      o=o+(x*j1);
      j = j / 100;
      j1=j1/10;
    }
    return o;
}

int main()
{
    int N,t=0;
    scanf("%d",&N);
    t=even_dig(N);
    printf("%d",t);
    getch();
    return 0;
}
