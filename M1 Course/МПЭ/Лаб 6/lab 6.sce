// ====================================================================
// Лабораторная работа №6 (№7) - Метод крутого восхождения
// Модель объекта: квадратичная зависимость
// ====================================================================

clear; clc; clf;

// ---- 1. Коэффициенты модели -------------------------------------------------
beta0 = 4;
beta1 = 3;
beta2 = 4;
beta12 = 3;
beta11 = -4;
beta22 = -5;

// ---- 2. Функция отклика -----------------------------------------------------
function y = model(x1, x2)
    y = beta0 + beta1*x1 + beta2*x2 + beta12*x1.*x2 + beta11*x1.^2 + beta22*x2.^2;
endfunction

// ---- 3. Функция градиента ---------------------------------------------------
function grad = gradient(x1, x2)
    grad1 = beta1 + beta12*x2 + 2*beta11*x1;   // dy/dx1
    grad2 = beta2 + beta12*x1 + 2*beta22*x2;   // dy/dx2
    grad = [grad1, grad2];
endfunction

// ---- 4. Параметры метода ----------------------------------------------------
X1_start = 15;          // начальное значение X1
X2_start = 85;          // начальное значение X2
delta = 10;             // шаг варьирования факторов
max_cycles = 3;         // максимальное число циклов крутого восхождения
max_steps_per_cycle = 5; // шагов в одном цикле
max_total_points = 25;   // всего измерений

// ---- 5. Метод крутого восхождения БЕЗ помех ---------------------------------
x1 = X1_start;
x2 = X2_start;
traj_clean = [x1, x2];
Y_clean = model(x1, x2);

for cycle = 1:max_cycles
    g = gradient(x1, x2);
    norm_g = norm(g);
    if norm_g < 1e-6 then break; end  // останов, если градиент почти ноль
    
    // Нормированный шаг
    step_x1 = delta * g(1) / norm_g;
    step_x2 = delta * g(2) / norm_g;
    
    for step = 1:max_steps_per_cycle
        x1 = x1 + step_x1;
        x2 = x2 + step_x2;
        traj_clean = [traj_clean; x1, x2];
        Y_clean = [Y_clean; model(x1, x2)];
        
        if size(traj_clean,1) >= max_total_points then break; end
    end
    if size(traj_clean,1) >= max_total_points then break; end
end

// ---- 6. Метод крутого восхождения С ПОМЕХАМИ ---------------------------------
sigma = 2;              // среднеквадратичное отклонение помехи N(0, sigma^2)
x1 = X1_start;
x2 = X2_start;
traj_noise = [x1, x2];
Y_noise = model(x1, x2) + rand(1,1,"normal")*sigma;  // первая точка с помехой

for cycle = 1:max_cycles
    g = gradient(x1, x2);
    norm_g = norm(g);
    if norm_g < 1e-6 then break; end
    
    step_x1 = delta * g(1) / norm_g;
    step_x2 = delta * g(2) / norm_g;
    
    for step = 1:max_steps_per_cycle
        x1 = x1 + step_x1;
        x2 = x2 + step_x2;
        traj_noise = [traj_noise; x1, x2];
        
        y_clean = model(x1, x2);
        y_noisy = y_clean + rand(1,1,"normal")*sigma;
        Y_noise = [Y_noise; y_noisy];
        
        if size(traj_noise,1) >= max_total_points then break; end
    end
    if size(traj_noise,1) >= max_total_points then break; end
end

// ---- 7. Вывод результатов в консоль -----------------------------------------
printf("\n======= Результаты оптимизации БЕЗ помех =======\n");
printf(" N     X1       X2         Y\n");
for i = 1:size(traj_clean,1)
    printf("%2d   %6.2f   %6.2f   %8.2f\n", i, traj_clean(i,1), traj_clean(i,2), Y_clean(i));
end

printf("\n======= Результаты оптимизации С помехами =======\n");
printf(" N     X1       X2         Y (с помехой)\n");
for i = 1:size(traj_noise,1)
    printf("%2d   %6.2f   %6.2f   %8.2f\n", i, traj_noise(i,1), traj_noise(i,2), Y_noise(i));
end

// ---- 8. Построение графиков -------------------------------------------------
figure(1);
clf;
subplot(2,2,1);
plot2d(traj_clean(:,1), traj_clean(:,2), style=-1);
plot2d(traj_clean(:,1), traj_clean(:,2), style=2, rect=[0,0,100,100]);
xlabel("X1");
ylabel("X2");
title("Траектория движения (без помех)");
legend("Точки", "Путь", 4);

subplot(2,2,2);
plot(1:size(Y_clean,1), Y_clean, 'b-o');
xlabel("Номер измерения");
ylabel("Y");
title("Изменение отклика (без помех)");
xgrid;

subplot(2,2,3);
plot2d(traj_noise(:,1), traj_noise(:,2), style=-1);
plot2d(traj_noise(:,1), traj_noise(:,2), style=5, rect=[0,0,100,100]);
xlabel("X1");
ylabel("X2");
title("Траектория движения (с помехами)");
legend("Точки", "Путь", 4);

subplot(2,2,4);
plot(1:size(Y_noise,1), Y_noise, 'r-s');
xlabel("Номер измерения");
ylabel("Y");
title("Изменение отклика (с помехами)");
xgrid;

// ---- 9. Сравнительный график траекторий -------------------------------------
figure(2);
clf;
plot2d(traj_clean(:,1), traj_clean(:,2), style=2, leg="Без помех");
plot2d(traj_noise(:,1), traj_noise(:,2), style=5, leg="С помехами");
xlabel("X1");
ylabel("X2");
title("Сравнение траекторий крутого восхождения");
legend("Без помех", "С помехами", 4);
xgrid();

// ---- 10. Вывод максимальных значений ----------------------------------------
printf("\n======= Анализ результатов =======\n");
[Ymax_clean, idx_clean] = max(Y_clean);
printf("Максимум без помех: Y = %.2f достигнут в точке X1=%.2f, X2=%.2f\n", ...
       Ymax_clean, traj_clean(idx_clean,1), traj_clean(idx_clean,2));

[Ymax_noise, idx_noise] = max(Y_noise);
printf("Максимум с помехами: Y = %.2f достигнут в точке X1=%.2f, X2=%.2f\n", ...
       Ymax_noise, traj_noise(idx_noise,1), traj_noise(idx_noise,2));

// ---- 11. Аналитический максимум (для сравнения) ----------------------------
// Решаем систему: dy/dx1 = 0, dy/dx2 = 0
// beta1 + beta12*x2 + 2*beta11*x1 = 0
// beta2 + beta12*x1 + 2*beta22*x2 = 0
A = [2*beta11, beta12; beta12, 2*beta22];
B = [-beta1; -beta2];
x_opt = A\B;
y_opt = model(x_opt(1), x_opt(2));
printf("\nАналитический максимум (теоретический):\n");
printf("X1_opt = %.4f, X2_opt = %.4f, Y_max = %.4f\n", x_opt(1), x_opt(2), y_opt);
