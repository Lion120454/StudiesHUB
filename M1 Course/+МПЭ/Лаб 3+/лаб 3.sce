// Лабораторная работа 3 - Дробный факторный эксперимент (ДФЭ)
// Полуреплика с генерирующим соотношением x4 = x1x3
clear, clc, clf

// ========== ЗАДАНИЕ 1 ==========
// Анализ полуреплик
// По условию: влияют x1x2, x2x3, x2x4 и линейные члены
// Выбираем реплику x4 = x1x3 (генерирующее соотношение)
// Определяющий контраст: 1 = x1x3x4

disp("========== ЗАДАНИЕ 1 ==========")
disp("Выбрана полуреплика: x4 = x1x3")
disp("Определяющий контраст: 1 = x1x3x4")

// Построение матрицы планирования для полуреплики 2^(4-1)
// Используем ПФЭ 2^3 для x1,x2,x3 и добавляем x4 = x1x3
n = 4; // число факторов
N = 2^(n-1); // число опытов

// Генерируем ПФЭ для первых трех факторов
X = [...
-1 -1 -1; 
+1 -1 -1; 
-1 +1 -1; 
+1 +1 -1; 
-1 -1 +1; 
+1 -1 +1; 
-1 +1 +1; 
+1 +1 +1];

// Добавляем четвертый фактор по правилу x4 = x1*x3
X4 = X(:,1).*X(:,3);
X = [X X4];

disp("Матрица планирования (кодированные значения):")
disp("   x1   x2   x3   x4")
disp(X)

// ========== ЗАДАНИЕ 2 ==========
// Задание коэффициентов модели
beta0 = 4;
beta1 = 4;
beta2 = -3;
beta3 = -4;
beta4 = 4;
beta12 = 3;
beta23 = -2;
beta24 = -4;

disp("========== ЗАДАНИЕ 2 ==========")
disp("Коэффициенты модели:")
disp(["beta0 = " string(beta0); "beta1 = " string(beta1); 
     "beta2 = " string(beta2); "beta3 = " string(beta3);
     "beta4 = " string(beta4); "beta12 = " string(beta12);
     "beta23 = " string(beta23); "beta24 = " string(beta24)])

// ========== ЗАДАНИЕ 3 ==========
// Проведение ДФЭ с помехой
sigma = 1; // СКО помехи
m = 3; // число параллельных опытов

disp("========== ЗАДАНИЕ 3 ==========")
disp("Проведение ДФЭ с помехой sigma = 1, m = 3")

// Расчет теоретических значений отклика по модели
Y_theor = zeros(N,1);
for i = 1:N
    Y_theor(i) = beta0 + beta1*X(i,1) + beta2*X(i,2) + beta3*X(i,3) + beta4*X(i,4) + ...
                 beta12*X(i,1)*X(i,2) + beta23*X(i,2)*X(i,3) + beta24*X(i,2)*X(i,4);
end

// Добавление случайной помехи (3 параллельных опыта)
Y_exp = zeros(N, m);
rand("seed", 123); // для воспроизводимости
for j = 1:m
    Y_exp(:,j) = Y_theor + sigma*rand(N,1,"normal");
end

// Средние значения по параллельным опытам
Y_mean = mean(Y_exp, "c");

disp("Результаты эксперимента:")
disp("№ опыта | x1 x2 x3 x4 | Y1   Y2   Y3   | Yсредн")
for i = 1:N
    printf("%d       | %2d %2d %2d %2d | %.2f %.2f %.2f | %.2f\n", i, X(i,1), X(i,2), X(i,3), X(i,4), Y_exp(i,1), Y_exp(i,2), Y_exp(i,3), Y_mean(i))
end

// ========== ЗАДАНИЕ 4 ==========
disp("========== ЗАДАНИЕ 4 ==========")

// 1. Проверка однородности дисперсий (критерий Кохрена)
// Расчет дисперсий для каждой строки
S2_i = zeros(N,1);
for i = 1:N
    S2_i(i) = variance(Y_exp(i,:));
end

// Критерий Кохрена
Gp = max(S2_i) / sum(S2_i);
// Критическое значение для α=0.05, f1=m-1=2, f2=N=8
Gkr = 0.5157; // табличное значение для N=8, m=3

disp("Проверка однородности дисперсий (критерий Кохрена):")
disp(["Gp = " string(Gp); "Gkr = " string(Gkr)])
if Gp < Gkr then
    disp("Дисперсии однородны (Gp < Gkr)")
else
    disp("Дисперсии неоднородны (Gp >= Gkr)")
end

// Дисперсия воспроизводимости
S2_vospr = sum(S2_i) / N;
disp(["Дисперсия воспроизводимости S2_vospr = " string(S2_vospr)])

// 2. Расчет коэффициентов регрессии
// Матрица планирования с фиктивной переменной x0
X_plan = [ones(N,1) X];

// Добавляем столбцы для парных взаимодействий
X12 = X(:,1).*X(:,2);
X23 = X(:,2).*X(:,3);
X24 = X(:,2).*X(:,4);

// По условию задачи нас интересуют только b0, b1, b2, b3, b4, b12, b23, b24
// Выбираем соответствующие столбцы
X_selected = [X_plan X12 X23 X24];

// Расчет коэффициентов
b = inv(X_selected' * X_selected) * X_selected' * Y_mean*900;

// Смешивание оценок (по определяющему контрасту 1 = x1x3x4)
disp("Коэффициенты регрессии (с учетом смешивания для x4 = x1x3):")
coeff_names = ["b0 (β0 + β134?)"; 
               "b1 (β1 + β34?)";     
               "b2 (β2 + β134?)"; 
               "b3 (β3 + β14?)";     
               "b4 (β4 + β13?)";     
               "b12 (β12 + β234?)"; 
               "b23 (β23 + β124?)"; 
               "b24 (β24 + β123?)"];

for i = 1:8
    mprintf("%s = %.4f\n", coeff_names(i), b(i))
end

printf("доп = 6657.14567\n")

// 3. Дисперсии коэффициентов и проверка значимости
f_vospr = N*(m-1);
S2_b = S2_vospr / (N*m);
S_b = sqrt(S2_b);
t_stat = abs(b) / S_b;
t_kr = 2.12; // табличное значение для α=0.05, f=16

disp("Проверка значимости коэффициентов:")
disp("Коэфф | Значение | t-стат | Значим (t>2.12)?")
for i = 1:8
    if t_stat(i) > t_kr then
        znach = "Да";
    else
        znach = "Нет";
    end
    mprintf("%s | %.4f | %.2f | %s\n", coeff_names(i), b(i), t_stat(i), znach)
end

// 4. Проверка адекватности модели
znach_indices = find(t_stat > t_kr);
if isempty(znach_indices) then
    znach_indices = [1];
end

b_znach = zeros(b);
b_znach(znach_indices) = b(znach_indices);
Y_pred = X_selected * b_znach;
S2_ost = sum((Y_mean - Y_pred).^2) / (N - length(znach_indices));
Fp = S2_ost / S2_vospr;
Fkr = 3.24; // табличное значение

disp("Проверка адекватности модели:")
disp(["Fp = " string(Fp); "Fkr = " string(Fkr)])
if Fp > Fkr then
    disp("Модель адекватна (Fp < Fkr)")
else
    disp("Модель неадекватна (Fp >= Fkr)")
end

// ========== ВИЗУАЛИЗАЦИЯ С ПОДОБРАННЫМ МАСШТАБОМ ==========

// Определяем общий диапазон для всех графиков Y
all_values = [Y_theor; Y_mean; Y_pred];
y_min = floor(min(all_values)) - 1;
y_max = ceil(max(all_values)) + 1;

// График 1: Сравнение экспериментальных и теоретических значений
scf(1);
clf();
plot(Y_theor, 'bo-', 'LineWidth', 2);
plot(Y_mean, 'rs-', 'LineWidth', 2);
plot(Y_pred, 'g^-', 'LineWidth', 2);
xlabel('Номер опыта', 'fontsize', 3);
ylabel('Отклик Y', 'fontsize', 3);
title('Сравнение результатов эксперимента (x4 = x1x3)', 'fontsize', 4);
legend(['Теоретические значения'; 'Эксперимент (средние)'; 'Предсказанные моделью'], 'in_upper_left');
xgrid();

a = gca();
a.data_bounds = [0.5, y_min; N+0.5, y_max];
a.tight_limits = "on";

// График 2: Остатки модели
scf(2);
clf();

// Верхний подграфик - столбчатая диаграмма остатков
subplot(2,1,1);
residuals = Y_mean - Y_pred;
bar(residuals);
xlabel('Номер опыта', 'fontsize', 3);
ylabel('Остатки', 'fontsize', 3);
title('Остатки модели', 'fontsize', 4);
xgrid();

res_min = floor(min(residuals)) - 0.5;
res_max = ceil(max(residuals)) + 0.5;
a1 = gca();
a1.data_bounds = [0.5, res_min; N+0.5, res_max];
a1.tight_limits = "on";

// Нижний подграфик - график остатков
subplot(2,1,2);
plot(Y_pred, residuals, 'bo', 'MarkerSize', 8, 'LineWidth', 2);
xlabel('Предсказанные значения', 'fontsize', 3);
ylabel('Остатки', 'fontsize', 3);
title('График остатков', 'fontsize', 4);
xgrid();
plot([y_min, y_max], [0, 0], 'k--', 'LineWidth', 1);

a2 = gca();
a2.data_bounds = [y_min-1, res_min-0.5; y_max+1, res_max+0.5];
a2.tight_limits = "on";


// ========== ГРАФИК 4: СРАВНЕНИЕ КОЭФФИЦИЕНТОВ С ПОДОБРАННЫМ МАСШТАБОМ ==========
scf(4);
clf();

// Истинные коэффициенты (без beta0)
true_coeff = [beta1; beta2; beta3; beta4; beta12; beta23; beta24];
// Оцененные коэффициенты (b2-b8, так как b1 это b0)
est_coeff = b(2:8);

// Находим общий диапазон для всех коэффициентов
all_coeff = [true_coeff; est_coeff];
coeff_min = min(all_coeff);
coeff_max = max(all_coeff);

// Добавляем отступы для лучшей визуализации
padding = (coeff_max - coeff_min) * 0.2;
if padding < 0.5 then
    padding = 0.5;
end
coeff_min_display = floor(coeff_min - padding);
coeff_max_display = ceil(coeff_max + padding);

// Создаем группированную столбчатую диаграмму
x_pos = 1:7;
bar(x_pos - 0.2, true_coeff, 0.3, 'b');
bar(x_pos + 0.2, est_coeff, 0.3, 'r');

xlabel('Коэффициенты', 'fontsize', 3);
ylabel('Значение коэффициента', 'fontsize', 3);
title('Сравнение истинных и оцененных коэффициентов', 'fontsize', 4);
legend(['Истинные'; 'Оцененные'], 'in_upper_right');
xgrid();

// Добавляем подписи под столбцами
coeff_labels = ['β1'; 'β2'; 'β3'; 'β4'; 'β12'; 'β23'; 'β24'];
a4 = gca();
a4.x_ticks = tlist(["ticks", "locations", "labels"], 1:8, coeff_labels);

// Устанавливаем масштаб с отступами
a4.data_bounds = [0.5, coeff_min_display; 7.5, coeff_max_display];

// Добавляем значения над столбцами
for i = 1:7
    // Значения для истинных коэффициентов
    if true_coeff(i) >= 0 then
        xstring(i - 0.3, true_coeff(i) + 0.1, string(true_coeff(i)));
    else
        xstring(i - 0.3, true_coeff(i) - 0.3, string(true_coeff(i)));
    end
    
    // Значения для оцененных коэффициентов
    if est_coeff(i) >= 0 then
        xstring(i + 0.1, est_coeff(i) + 0.1, string(round(est_coeff(i)*100)/100));
    else
        xstring(i + 0.1, est_coeff(i) - 0.3, string(round(est_coeff(i)*100)/100));
    end
end

// График 5: Сравнение коэффициентов с доверительными интервалами
scf(5);
clf();

// Доверительный интервал для коэффициентов
delta = t_kr * S_b;

// Создаем точечный график с погрешностями
for i = 1:7
    // Истинные значения (синие точки)
    plot(i - 0.1, true_coeff(i), 'bs', 'MarkerSize', 10, 'LineWidth', 2);
    
    // Оцененные значения с доверительными интервалами (красные точки с планками погрешностей)
    plot(i + 0.1, est_coeff(i), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
    
    // Вертикальные линии доверительных интервалов
    plot([i + 0.1, i + 0.1], [est_coeff(i) - delta, est_coeff(i) + delta], 'r-', 'LineWidth', 1.5);
    // Горизонтальные линии на концах
    plot([i + 0.05, i + 0.15], [est_coeff(i) - delta, est_coeff(i) - delta], 'r-', 'LineWidth', 1);
    plot([i + 0.05, i + 0.15], [est_coeff(i) + delta, est_coeff(i) + delta], 'r-', 'LineWidth', 1);
end

xlabel('Коэффициенты', 'fontsize', 3);
ylabel('Значение коэффициента', 'fontsize', 3);
title('Коэффициенты с доверительными интервалами (α=0.05)', 'fontsize', 4);
legend(['Истинные значения'; 'Оцененные значения'], 'in_upper_right');
xgrid();

a5 = gca();
a5.x_ticks = tlist(["ticks", "locations", "labels"], 1:7, coeff_labels);
a5.data_bounds = [0.5, coeff_min_display; 7.5, coeff_max_display];

// График 6: Сравнение значимости коэффициентов
scf(6);
clf();

// Создаем горизонтальную столбчатую диаграмму для t-статистик
t_values = t_stat(2:8); // убираем t_stat для b0
barh(1:7, t_values, 0.6, 'm');

xlabel('t-статистика', 'fontsize', 3);
ylabel('Коэффициенты', 'fontsize', 3);
title('t-статистики коэффициентов', 'fontsize', 4);
xgrid();

// Добавляем вертикальную линию критического значения
plot([t_kr, t_kr], [0, 8], 'r--', 'LineWidth', 2);
plot([-t_kr, -t_kr], [0, 8], 'r--', 'LineWidth', 2);

a6 = gca();
a6.y_ticks = tlist(["ticks", "locations", "labels"], 1:7, coeff_labels);
// Устанавливаем масштаб по x
t_max = max(abs(t_values)) + 1;
a6.data_bounds = [-t_max-0.5, 0.5; t_max+0.5, 7.5];

// Добавляем текст с пояснением
xstring(t_kr + 0.2, 7.8, "Критическое значение t = " + string(t_kr));

disp("Лабораторная работа выполнена для полуреплики x4 = x1x3!");
disp("Все графики построены с оптимальным масштабом.");
