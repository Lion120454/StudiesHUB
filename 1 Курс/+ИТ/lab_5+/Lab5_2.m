summ=0;
X = 10;
n=0;
while abs(X)>(10^(-4))
    X=(((-1)^n)*(2*X).^(2*n))/(fact(2*n));
    summ=summ+(X);
    n=n+1;
end
summ
X