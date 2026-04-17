function dydx = F(x,y)
dydx = zeros(1,1);
dydx(1) = (x.^3*sin(y)+1)
end
