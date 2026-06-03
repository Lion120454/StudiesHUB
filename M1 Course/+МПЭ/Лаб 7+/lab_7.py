import numpy as np
import pandas as pd
from scipy.stats import f

# Данные из таблицы 7.1 (время в часах)
data = {
    ('I', 1): ('A', 3.5), ('I', 2): ('B', 2.1), ('I', 3): ('C', 2.5), ('I', 4): ('D', 3.5), ('I', 5): ('E', 2.4),
    ('II', 1): ('E', 2.6), ('II', 2): ('A', 3.3), ('II', 3): ('B', 2.1), ('II', 4): ('C', 2.5), ('II', 5): ('D', 2.7),
    ('III', 1): ('D', 2.9), ('III', 2): ('E', 2.6), ('III', 3): ('A', 3.5), ('III', 4): ('B', 2.7), ('III', 5): ('C', 2.9),
    ('IV', 1): ('C', 2.5), ('IV', 2): ('D', 2.9), ('IV', 3): ('E', 3.0), ('IV', 4): ('A', 3.3), ('IV', 5): ('B', 2.3),
    ('V', 1): ('B', 2.1), ('V', 2): ('C', 2.3), ('V', 3): ('D', 3.7), ('V', 4): ('E', 3.2), ('V', 5): ('A', 3.5)
}

# Преобразуем в DataFrame
rows = ['I', 'II', 'III', 'IV', 'V']
cols = [1, 2, 3, 4, 5]
df_list = []
for r in rows:
    for c in cols:
        form, time = data[(r, c)]
        df_list.append([r, c, form, time])

df = pd.DataFrame(df_list, columns=['Полоса', 'Положение', 'Форма', 'Время'])

# Общее среднее
grand_mean = df['Время'].mean()
N = len(df)

# 1. Общая сумма квадратов
SStotal = np.sum((df['Время'] - grand_mean) ** 2)

# 2. Сумма квадратов для полос (строки)
row_means = df.groupby('Полоса')['Время'].mean().values
SStreat_rows = len(cols) * np.sum((row_means - grand_mean) ** 2)

# 3. Сумма квадратов для формы электрода (латинская буква)
form_means = df.groupby('Форма')['Время'].mean().values
SStreat_forms = len(rows) * np.sum((form_means - grand_mean) ** 2)

# 4. Сумма квадратов для положения (столбцы)
col_means = df.groupby('Положение')['Время'].mean().values
SStreat_cols = len(rows) * np.sum((col_means - grand_mean) ** 2)

# 5. Сумма квадратов для ошибки
SSerror = SStotal - SStreat_rows - SStreat_forms - SStreat_cols

# Степени свободы
df_total = N - 1
df_rows = len(rows) - 1
df_forms = len(df['Форма'].unique()) - 1
df_cols = len(cols) - 1
df_error = df_total - df_rows - df_forms - df_cols

# Дисперсии (средние квадраты)
MS_rows = SStreat_rows / df_rows
MS_forms = SStreat_forms / df_forms
MS_cols = SStreat_cols / df_cols
MS_error = SSerror / df_error

# F-статистики
F_rows = MS_rows / MS_error
F_forms = MS_forms / MS_error
F_cols = MS_cols / MS_error

# Критические значения F при alpha=0.05
alpha = 0.05
F_crit_rows = f.ppf(1 - alpha, df_rows, df_error)
F_crit_forms = f.ppf(1 - alpha, df_forms, df_error)
F_crit_cols = f.ppf(1 - alpha, df_cols, df_error)

# Таблица 7.2 – Дисперсионный анализ
anova_table = pd.DataFrame({
    'Источник изменчивости': ['Полоса', 'Форма электрода', 'Положение отверстий', 'Ошибка', 'Сумма'],
    'Число степеней свободы': [df_rows, df_forms, df_cols, df_error, df_total],
    'Сумма квадратов': [SStreat_rows, SStreat_forms, SStreat_cols, SSerror, SStotal],
    'Дисперсии': [MS_rows, MS_forms, MS_cols, MS_error, ''],
    'F-отношение': [F_rows, F_forms, F_cols, '', ''],
    'F крит (0.05)': [F_crit_rows, F_crit_forms, F_crit_cols, '', '']
})

print("Таблица 7.2 – Дисперсионный анализ латинского квадрата")
print(anova_table.round(3))

# Проверка значимости
print("\nПроверка значимости факторов при alpha = 0.05:")
print(f"Полоса: F = {F_rows:.3f} > F_crit = {F_crit_rows:.3f} -> {'Значимо' if F_rows > F_crit_rows else 'Не значимо'}")
print(f"Форма электрода: F = {F_forms:.3f} > F_crit = {F_crit_forms:.3f} -> {'Значимо' if F_forms > F_crit_forms else 'Не значимо'}")
print(f"Положение: F = {F_cols:.3f} > F_crit = {F_crit_cols:.3f} -> {'Значимо' if F_cols > F_crit_cols else 'Не значимо'}")

# ---- Ранговый критерий Дункана ----
# Средние для каждой формы электрода
form_means_dict = df.groupby('Форма')['Время'].mean().sort_values()
forms_sorted = form_means_dict.index.tolist()
means_sorted = form_means_dict.values

# Число средних для сравнения
k = len(forms_sorted)

# Таблица ранговых диапазонов (Дункан) для alpha=0.05, df_error
# Значения из стандартной таблицы (усечённый вариант)
# Для df_error=12 (в нашем случае) и alpha=0.05
duncan_table = {
    2: 3.08,
    3: 3.23,
    4: 3.33,
    5: 3.36
}

# Стандартная ошибка среднего
SE = np.sqrt(MS_error / len(rows))  # n=5 наблюдений на форму

# Ранговые диапазоны
ranges = [duncan_table[p] * SE for p in range(2, k+1)]

# Сравнение средних
print("\nРанговый критерий Дункана (alpha = 0.05):")
print(f"Средние по формам (от меньшего к большему):")
for form, mean_val in zip(forms_sorted, means_sorted):
    print(f"  {form}: {mean_val:.3f}")

print(f"\nСтандартная ошибка среднего = {SE:.4f}")
print("Критические ранговые диапазоны:")
for p, rng in zip(range(2, k+1), ranges):
    print(f"  p={p}: {rng:.4f}")

# Находим лучшую форму (минимальное время)
best_form = forms_sorted[0]
print(f"\nЛучшая форма электрода (минимальное время): {best_form} со средним {means_sorted[0]:.3f} часов")

# Определим, какие формы значимо отличаются от лучшей
print("\nПроверка значимости различий с лучшей формой:")
for i in range(1, k):
    diff = means_sorted[i] - means_sorted[0]
    p_val = i + 1  # ранговое расстояние
    crit_diff = ranges[p_val - 2]  # для p
    print(f"{forms_sorted[i]} vs {best_form}: разность = {diff:.3f}, критическая разность = {crit_diff:.3f} -> {'Значимо' if diff > crit_diff else 'Не значимо'}")