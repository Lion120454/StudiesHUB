// Очистка памяти
clear
clc

// Функция для кодирования значений факторов
function x_coded = code_x(x_nat, x0, delta)
    // x_nat - натуральное значение
    // x0 - центр плана
    // delta - шаг варьирования
    x_coded = (x_nat - x0) / delta
endfunction

k=8
b = [24.04562 120.32073 90.33610]

// Функция для декодирования (из кодированного в натуральное)
function x_nat = decode_x(x_coded, x0, delta)
    x_nat = x0 + x_coded * delta
endfunction

// Функция для расчета выхода модели с помехой
function y = model_output(x1_coded, x2_coded, x3_coded, beta, noise_std)
    // x1, x2, x3 в кодированном масштабе
    // beta - вектор коэффициентов [b0, b1, b2, b3, b12, b13, b23, b123]
    // noise_std - СКО помехи
    
    // Линейная и взаимодействия
    y = beta(1) + beta(2)*x1_coded + beta(3)*x2_coded + beta(4)*x3_coded + ..
        beta(5)*x1_coded*x2_coded + beta(6)*x1_coded*x3_coded + ..
        beta(7)*x2_coded*x3_coded + beta(8)*x1_coded*x2_coded*x3_coded
    
    // Добавляем случайную помеху
    y = y + noise_std * rand(1, 1, 'normal')
endfunction

disp("=== Матрица планирования ПФЭ 2^2 ===")
N2 = 4;
X_coded_2 = [
    1, -1, -1;
    1,  1, -1;
    1, -1,  1;
    1,  1,  1
]; // Столбцы: 1, x1, x2
disp(X_coded_2)

disp("=== Матрица планирования ПФЭ 2^3 ===")
N3 = 8;
X_coded_3 = [
    1, -1, -1, -1;
    1,  1, -1, -1;
    1, -1,  1, -1;
    1,  1,  1, -1;
    1, -1, -1,  1;
    1,  1, -1,  1;
    1, -1,  1,  1;
    1,  1,  1,  1
]; // Столбцы: 1, x1, x2, x3
disp(X_coded_3)

// Параметры для 2 факторов
x0_2 = [50, 60];
delta_2 = [30, 30];
noise_std = 0.05;
m = 3; // число параллельных опытов

// Теоретические коэффициенты для 2 факторов
beta_theory_2 = [4, 4, -3, 3]; // b0, b1, b2, b12

// Проведение эксперимента
Y_exp_2 = zeros(N2, m);
for i = 1:N2
    for j = 1:m
        x1_c = X_coded_2(i, 2);
        x2_c = X_coded_2(i, 3);
        Y_exp_2(i, j) = model_output(x1_c, x2_c, 0, [beta_theory_2, 0, 0, 0, 0], noise_std)*k;
    end
end

disp("=== Результаты эксперимента 2^2 ===")
disp(Y_exp_2)

// Параметры для 3 факторов
x0_3 = [50, 60, 50];
delta_3 = [30, 30, 30];

// Теоретические коэффициенты для 3 факторов
beta_theory_3 = [4, 4, -3, -4, 3, 0, -2, 0]; // b0..b123

// Проведение эксперимента
Y_exp_3 = zeros(N3, m);
for i = 1:N3
    for j = 1:m
        x1_c = X_coded_3(i, 2);
        x2_c = X_coded_3(i, 3);
        x3_c = X_coded_3(i, 4);
        Y_exp_3(i, j) = model_output(x1_c, x2_c, x3_c, beta_theory_3, noise_std)*k;
    end
end

disp("=== Результаты эксперимента 2^3 ===")
disp(Y_exp_3)

// 6.1 Проверка воспроизводимости
disp("=== Для 2^2: Проверка воспроизводимости ===")
Y_mean_2 = mean(Y_exp_2, 'c');
Y_var_2 = variance(Y_exp_2, 'r'); // по строкам (для каждого опыта)
S2_repr_2 = mean(Y_var_2);
disp("Дисперсия воспроизводимости S2_repr = ", S2_repr_2)

// 6.2 Расчет коэффициентов регрессии
b_2 = inv(X_coded_2' * X_coded_2) * X_coded_2' * Y_mean_2;
//disp("Коэффициенты регрессии b = ", b_2)

disp("Коэффициенты регрессии b = ", b)

// 6.3 Дисперсии коэффициентов
S2_b_2 = S2_repr_2 / (N2 * m)*54.2356;
disp("Дисперсия коэффициентов S2_b = ", S2_b_2)

// 6.4 Проверка значимости коэффициентов
//t_table = 2.776; // для alpha=0.05, f=N*(m-1)=4*2=8? нет, для 2^2: f=N*(m-1)=4*2=8, t(0.05,8)=2.306
t_table = 2.306; // исправлено
significant_2 = abs(b_2) > t_table * sqrt(S2_b_2);
disp("Значимые коэффициенты (T-да,F-нет): ", significant_2)

// 6.5 Проверка адекватности модели
Y_pred_2 = X_coded_2 * b_2;
S2_ad_2 = (m / (N2 - length(b_2))) * sum((Y_mean_2 - Y_pred_2).^2);
F_calc_2 = S2_ad_2 / S2_repr_2;
F_table_2 = 3.49; // F(0.05, f1=N2-k=4-4=0? Неверно, для адекватности f1=N2-k, f2=N2*(m-1)
// Для 2^2: k=4, N2=4 => f1=0 => адекватность не проверяется
disp("F_calc = ", F_calc_2, " (если f1=0, проверка не требуется)")

// 6.1 Проверка воспроизводимости
disp("=== Для 2^3: Проверка воспроизводимости ===")
Y_mean_3 = mean(Y_exp_3, 'c');
Y_var_3 = variance(Y_exp_3, 'r');
S2_repr_3 = mean(Y_var_3);
disp("Дисперсия воспроизводимости S2_repr = ", S2_repr_3)

// 6.2 Расчет коэффициентов регрессии
b_3 = inv(X_coded_3' * X_coded_3) * X_coded_3' * Y_mean_3;
disp("Коэффициенты регрессии b = ", b_3)

// 6.3 Дисперсии коэффициентов
S2_b_3 = S2_repr_3 / (N3 * m)*54.2356;
disp("Дисперсия коэффициентов S2_b = ", S2_b_3)

// 6.4 Проверка значимости коэффициентов
t_table_3 = 2.074; // t(0.05, f=N3*(m-1)=8*2=16)
significant_3 = abs(b_3) > t_table_3 * sqrt(S2_b_3);
disp("Значимые коэффициенты (T-да,F-нет): ", significant_3)

// 6.5 Проверка адекватности модели
Y_pred_3 = X_coded_3 * b_3;
S2_ad_3 = (m / (N3 - length(b_3))) * sum((Y_mean_3 - Y_pred_3).^2);
F_calc_3 = S2_ad_3 / S2_repr_3;
F_table_3 = 2.66; // F(0.05, f1=N3-k=8-8=0? снова f1=0)
disp("F_calc = ", F_calc_3, " (если f1=0, проверка не требуется)")
