clear; clc;

// Система уравнений
function F = system_eq(X)
    x = X(1); y = X(2);
    F = [sin(y) + 2*x - 2; cos(x-1) + y - 0.7];
endfunction

// Якобиан
function J = jacobian(X)
    x = X(1); y = X(2);
    J = [2, cos(y); -sin(x-1), 1];
endfunction

// Параметры решения
x0 = [0.5; 0.5];
tolerance = 1e-8;
max_iter = 100;

// Решение методом Ньютона
X = x0;
printf("Метод Ньютона:\n");
printf("Итерация\tx\t\ty\t\tОшибка\n");
printf("==========================================\n");

error=tolerance+1;

while (error>tolerance)
    F_val = system_eq(X);
    J_val = jacobian(X);
    delta = linsolve(J_val,F_val);
    X_new = X + delta;
    error = norm(X_new - X);
    
    printf("t\t%.6f\t%.6f\t%.2e\n", X(1), X(2), error);
    X = X_new;
end

printf("\nФинальное решение:\n");
printf("x = %.8f\n", X(1));
printf("y = %.8f\n", X(2));

// Проверка
F_final = system_eq(X);
printf("\nНевязки:\n");
printf("sin(y) + 2x - 2 = ", F_final(1));
printf("cos(x-1) + y - 0.7 = %.2e\n", F_final(2));
