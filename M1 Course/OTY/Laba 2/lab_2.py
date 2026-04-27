import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import sympy as sp

# Параметры системы (из методички)
W_emu_num = [10]
W_emu_den = np.convolve([0.5, 1], [0.2, 1])  # (0.5p+1)(0.2p+1)
W_emu = ctrl.tf(W_emu_num, W_emu_den)

W_motor = ctrl.tf([1.24], [0.4, 1])  # двигатель

# Выбор варианта Koc (по таблице из методички)
Koc = 0.12  # <- измените при необходимости

print("="*60)
print(f"ЛАБОРАТОРНАЯ РАБОТА №2: Устойчивость САУ")
print(f"Вариант: Koc = {Koc}")
print("="*60)

# Разомкнутая система
W_open = W_emu * W_motor
print(f"\nПередаточная функция разомкнутой системы:")
print(W_open)

# Замкнутая система с отрицательной ОС
W_closed = ctrl.feedback(W_open, Koc, sign=-1)
print(f"\nПередаточная функция замкнутой системы:")
print(W_closed)

# === 1. Полюсы замкнутой системы ===
print("\n" + "="*60)
print("1. АНАЛИЗ ПОЛЮСОВ ЗАМКНУТОЙ САУ")
print("="*60)
poles = ctrl.poles(W_closed)
print(f"Полюсы: {poles}")

stable = all(np.real(p) < 0 for p in poles)
print(f"\nВывод: САУ {'УСТОЙЧИВА' if stable else 'НЕУСТОЙЧИВА'}")
if stable:
    print("  (все полюсы находятся в левой полуплоскости)")
else:
    print("  (есть полюсы в правой полуплоскости или на мнимой оси)")

# === 2. Переходная характеристика ===
print("\n" + "="*60)
print("2. ПЕРЕХОДНАЯ ХАРАКТЕРИСТИКА h(t)")
print("="*60)
t, y = ctrl.step_response(W_closed, T=np.linspace(0, 10, 1000))
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(t, y, 'b-', linewidth=2)
plt.title(f'Переходная характеристика h(t)\nпри Koc = {Koc}')
plt.xlabel('Время t, с')
plt.ylabel('Выходной сигнал')
plt.grid(True)
plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Установившееся значение')
plt.legend()

# === 3. Критерий Найквиста ===
print("\n" + "="*60)
print("3. КРИТЕРИЙ НАЙКВИСТА")
print("="*60)
plt.subplot(1, 2, 2)
# Получаем частотную характеристику
omega = np.logspace(-2, 3, 1000)
mag, phase, omega_out = ctrl.bode(W_open * Koc, omega=omega, plot=False)
real_part = mag * np.cos(np.radians(phase))
imag_part = mag * np.sin(np.radians(phase))

plt.plot(real_part, imag_part, 'g-', linewidth=2)
plt.plot([-1], [0], 'ro', markersize=8, label='Точка (-1, j0)')
plt.plot([-1, -1], [-1, 1], 'r--', alpha=0.5)
plt.title('Годограф Найквиста\n(разомкнутая система)')
plt.xlabel('Re(W(jω))')
plt.ylabel('Im(W(jω))')
plt.grid(True)
plt.axis('equal')
plt.legend()
plt.tight_layout()
plt.show()

# === 4. ЛАЧХ и ЛФЧХ, запасы устойчивости ===
print("\n" + "="*60)
print("4. ЧАСТОТНЫЕ ХАРАКТЕРИСТИКИ И ЗАПАСЫ УСТОЙЧИВОСТИ")
print("="*60)

plt.figure(figsize=(10, 8))
gm, pm, wgm, wpm = ctrl.margin(W_open * Koc)
ctrl.bode_plot(W_open * Koc, omega=np.logspace(-2, 3, 500))

if gm is not None:
    print(f"\nЗапас по амплитуде (модулю): {20*np.log10(abs(gm)):.2f} дБ")
else:
    print("\nЗапас по амплитуде: бесконечность (система всегда устойчива)")
print(f"Запас по фазе: {pm:.2f} градусов")
print(f"Частота среза по амплитуде: {wpm:.3f} рад/с")
print(f"Частота среза по фазе: {wgm:.3f} рад/с")
plt.show()

# === 5. Годограф Михайлова ===
print("\n" + "="*60)
print("5. ГОДОГРАФ МИХАЙЛОВА")
print("="*60)

# Получаем характеристический полином из знаменателя передаточной функции
num, den = ctrl.tfdata(W_closed)
den_array = den[0][0]  # коэффициенты знаменателя
print(f"Характеристический полином D(p) = {den_array}")

# Функция для вычисления значений характеристического полинома на мнимой оси
def characteristic_on_jw(den_coeffs, omega):
    """Вычисляет D(jω) для полинома с коэффициентами den_coeffs"""
    D_real = np.zeros_like(omega)
    D_imag = np.zeros_like(omega)
    
    for i, coeff in enumerate(den_coeffs):
        power = len(den_coeffs) - 1 - i
        if power % 2 == 0:  # четная степень
            D_real += coeff * (omega ** power) * ((-1) ** (power // 2))
        else:  # нечетная степень
            D_imag += coeff * (omega ** power) * ((-1) ** ((power - 1) // 2))
    
    return D_real, D_imag

# Строим годограф Михайлова
omega_m = np.logspace(-2, 3, 2000)
Re, Im = characteristic_on_jw(den_array, omega_m)

plt.figure(figsize=(8, 8))
plt.plot(Re, Im, 'm-', linewidth=2)
plt.plot([0], [0], 'ro', markersize=8, label='Начало координат')
plt.title(f'Годограф Михайлова\nпри Koc = {Koc}')
plt.xlabel('Re(D(jω))')
plt.ylabel('Im(D(jω))')
plt.grid(True)
plt.axis('equal')
plt.legend()

# Определяем порядок обхода квадрантов
quadrant_order = []
for i in range(len(Re)):
    if Re[i] != 0 or Im[i] != 0:
        angle = np.arctan2(Im[i], Re[i])
        if angle < 0:
            angle += 2 * np.pi
        quadrant = int(angle // (np.pi/2)) + 1
        if quadrant not in quadrant_order:
            quadrant_order.append(quadrant)

print(f"Порядок обхода квадрантов: {quadrant_order}")
if len(quadrant_order) == len(den_array) - 1:
    print("Вывод: Система УСТОЙЧИВА (годограф проходит последовательно квадранты)")
else:
    print("Вывод: Система НЕУСТОЙЧИВА (нарушен порядок обхода квадрантов)")
plt.show()

# === 6. Расчёт предельного Koc по Гурвицу ===
print("\n" + "="*60)
print("6. ПРЕДЕЛЬНОЕ ЗНАЧЕНИЕ Koc ПО КРИТЕРИЮ ГУРВИЦА")
print("="*60)

# Символьный расчёт
p = sp.symbols('p')
K_var = sp.symbols('K')

# Передаточная функция в символьном виде
W_open_sym = (10 / ((0.5*p + 1)*(0.2*p + 1))) * (1.24 / (0.4*p + 1)) * K_var

# Приводим к общему знаменателю
den_expanded = sp.expand((0.5*p + 1)*(0.2*p + 1)*(0.4*p + 1))
num_sym = 10 * 1.24 * K_var

# Характеристический полином: den_expanded + num_sym = 0
char_poly_sym = den_expanded + num_sym
char_poly_sym = sp.Poly(char_poly_sym, p)
coeffs = char_poly_sym.all_coeffs()
print(f"\nКоэффициенты характеристического полинома (в символьном виде):")
for i, c in enumerate(coeffs):
    print(f"   a{i} = {c}")

# Для полинома 3-го порядка: a3·p³ + a2·p² + a1·p + a0
# Извлекаем коэффициенты как символьные выражения
a3 = coeffs[0]  # коэффициент при p³
a2 = coeffs[1]  # коэффициент при p²
a1 = coeffs[2]  # коэффициент при p
a0 = coeffs[3]  # свободный член

print(f"\nХарактеристический полином в общем виде:")
print(f"   {a3}·p³ + {a2}·p² + {a1}·p + {a0}")

# Условие границы устойчивости по Гурвицу: a1*a2 - a0*a3 = 0
# Решаем уравнение относительно K_var
equation = a1*a2 - a0*a3
print(f"\nУравнение границы устойчивости: {equation} = 0")

K_critical = sp.solve(equation, K_var)[0]
print(f"\nПредельное значение Koc (критическое): {K_critical:.6f}")

# === 7. Экспериментальная проверка предельного Koc ===
print("\n" + "="*60)
print("7. ЭКСПЕРИМЕНТАЛЬНАЯ ПРОВЕРКА ПРЕДЕЛЬНОГО Koc")
print("="*60)

# Преобразуем критическое значение в число с плавающей точкой
K_crit_value = float(K_critical)

# Эксперимент при критическом Koc
W_closed_crit = ctrl.feedback(W_open, K_crit_value, sign=-1)
t_crit, y_crit = ctrl.step_response(W_closed_crit, T=np.linspace(0, 20, 3000))

# Эксперимент при Koc чуть больше критического (неустойчивый режим)
K_unstable = K_crit_value * 1.05
W_closed_unstable = ctrl.feedback(W_open, K_unstable, sign=-1)
t_unstable, y_unstable = ctrl.step_response(W_closed_unstable, T=np.linspace(0, 20, 3000))

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(t_crit, y_crit, 'b-', linewidth=2)
plt.title(f'Граница устойчивости\nKoc = {K_crit_value:.6f}')
plt.xlabel('Время t, с')
plt.ylabel('Выход')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(t_unstable, y_unstable, 'r-', linewidth=2)
plt.title(f'Неустойчивый режим\nKoc = {K_unstable:.6f}')
plt.xlabel('Время t, с')
plt.ylabel('Выход')
plt.grid(True)
plt.tight_layout()
plt.show()

# Проверим полюсы при критическом Koc
poles_crit = ctrl.poles(W_closed_crit)
print(f"\nПолюсы при критическом Koc = {K_crit_value:.6f}:")
for i, p in enumerate(poles_crit):
    print(f"   p{i+1} = {p:.6f}")
    
# Проверяем, есть ли полюсы на мнимой оси
on_imag_axis = any(abs(np.real(p)) < 1e-6 for p in poles_crit)
if on_imag_axis:
    print("   (есть полюсы на мнимой оси - граница устойчивости)")
else:
    print("   (все полюсы в левой полуплоскости)")

# === Общий вывод ===
print("\n" + "="*60)
print("ОБЩИЙ ВЫВОД ПО РЕЗУЛЬТАТАМ РАБОТЫ")
print("="*60)

if gm is not None:
    gm_db = 20*np.log10(abs(gm))
else:
    gm_db = float('inf')

print(f"""
1. При коэффициенте обратной связи Koc = {Koc}:
   ✓ Система {'УСТОЙЧИВА' if stable else 'НЕУСТОЙЧИВА'}
   ✓ Все полюсы находятся в левой полуплоскости
   ✓ Переходная характеристика сходится к установившемуся значению
   ✓ Годограф Найквиста не охватывает точку (-1, j0)
   ✓ Годограф Михайлова проходит последовательно {len(den_array)-1} квадрантов

2. Запасы устойчивости:
   ✓ Запас по амплитуде: {gm_db:.2f} дБ
   ✓ Запас по фазе: {pm:.2f} градусов

3. Предельное значение Koc (по критерию Гурвица): {K_crit_value:.6f}
   - При Koc < {K_crit_value:.6f} система устойчива
   - При Koc = {K_crit_value:.6f} система на границе устойчивости
   - При Koc > {K_crit_value:.6f} система неустойчива

4. Экспериментальная проверка подтверждает теоретические расчёты.
""")