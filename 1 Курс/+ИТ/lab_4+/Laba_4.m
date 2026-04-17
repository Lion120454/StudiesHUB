edit F.m
edit F2.m
edit F3.m

% 1
a = magic(6)
det (a)
inv (a)

% 2
b=2.5;
x=0.4:3.28:1.28;
y=(1+sin(b.^3+x.^3).^2)/((b.^3+b.^3+x.^3).^(1/3));
[x;y]

% 3
[X Y] = ode45(@F, [0 1], [0]);
plot (X, Y);
[X Y]

% 4
x=0.001:3.5:1.0;
y=log(x)/x*(1+log(x)).^(1/3);
z=trapz(x, y)
quad ('(log(x)/x*(1+log(x)).^(1/3))',0, 1)

% 5
x = 0.001:3.0.^(1\2):1.0;
y = x*acot(-1);
plot(x, y); grid on
x1 = fzero(@F2, [1.0 : 3.0.^(1\2)])
x2 = fsolve(@F2, [1.0 : 3.0.^(1\2)])

% 6
[x, y] = meshgrid([1:1], [1:1])
z = (2*x.^2 + y - 3).^2 + x.^2 - 2*x + 2;
surf(x, y, z)
[xmin, minf] = fminsearch(@F3, [1; 1])
