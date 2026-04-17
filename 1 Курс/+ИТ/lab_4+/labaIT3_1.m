[x, y] = meshgrid([-2:2], [-2:2])
z = (2.*x.^2-y-3).^2+x.^2+2.*x+2;
surf(x, y, z)

[xmin, minf] = fminsearch(@fun2, [1; 1])






[x, y] = meshgrid([-1:1], [-1:1])
z = (2*x.^2 + y - 3).^2 + x.^2 - 2*x + 2;
surf(x, y, z)
[xmin, minf] = fminsearch(@F3, [1; 1])
