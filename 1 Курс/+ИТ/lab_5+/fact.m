function f = fact(x)
% fact(x) - функция вычисления факториала x!
 f = 1;
 if x > 0
 for i = 1:x
 f = f*i;
 end
 end
