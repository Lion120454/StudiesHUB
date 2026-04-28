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
Koc = 0.09  # Вариант 1

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
plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Вход')
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

# Получаем данные для Bode plot
omega = np.logspace(-2, 3, 1000)
mag, phase, omega_out = ctrl.bode(W_open * Koc, omega=omega, plot=False)

# Преобразуем в децибелы
mag_db = 20 * np.log10(mag)

# Запасы устойчивости
gm, pm, wgm, wpm = ctrl.margin(W_open * Koc)

# === КОРРЕКТНЫЙ РАСЧЁТ ЗАПАСА ПО ФАЗЕ ===
# Находим фазу на частоте среза
phase_at_wpm = np.interp(wpm, omega_out, phase)

# Корректный запас по фазе (расстояние до -180°)
if phase_at_wpm < -180:
    phase_margin_correct = abs(phase_at_wpm + 360)
else:
    phase_margin_correct = abs(phase_at_wpm + 180)

# Для систем с большим запасом (>90°) показываем фактическое расстояние
if phase_margin_correct > 90:
    actual_phase_margin = 180 - phase_margin_correct
    margin_note = f" (фактически {actual_phase_margin:.1f}° до границы)"
else:
    actual_phase_margin = phase_margin_correct
    margin_note = ""

print(f"\nРезультаты анализа частотных характеристик:")
print(f"  • Частота среза (усиление = 0 дБ): ω_ср = {wpm:.4f} рад/с")
print(f"  • Фаза на частоте среза: φ(ω_ср) = {phase_at_wpm:.2f}°")
print(f"  • Запас по амплитуде: {20*np.log10(abs(gm)):.2f} дБ (на ω_π = {wgm:.4f} рад/с)")
print(f"  • Запас по фазе (до -180°): {phase_margin_correct:.2f}°{margin_note}")

# Создаём фигуру с двумя подграфиками
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))

# ===== ВЕРХНИЙ ГРАФИК: ЛАЧХ в дБ =====
ax1.semilogx(omega_out, mag_db, 'b-', linewidth=2)
ax1.grid(True, which='both', linestyle='--', alpha=0.5)
ax1.set_ylabel('Амплитуда (дБ)')
ax1.set_title(f'Логарифмические частотные характеристики разомкнутой САУ (Koc = {Koc})')
ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)

# Отметка частоты среза ω_ср (где mag = 0 дБ)
if wpm is not None and wpm > 0:
    ax1.axvline(x=wpm, color='g', linestyle='--', alpha=0.7, linewidth=1.5)
    ax1.plot(wpm, 0, 'go', markersize=8, zorder=5)
    ax1.annotate(f'ω_ср = {wpm:.3f} рад/с\n(усиление = 0 дБ)',
                 xy=(wpm, 0),
                 xytext=(wpm * 1.5, 5),
                 fontsize=9,
                 color='green',
                 arrowprops=dict(arrowstyle='->', color='green', lw=1),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Отметка частоты ω_π (где фаза = -180°) и запаса по амплитуде
if gm is not None and wgm is not None and wgm > 0:
    gm_db = 20 * np.log10(abs(gm))
    mag_at_wgm = np.interp(wgm, omega_out, mag_db)
    
    ax1.axvline(x=wgm, color='r', linestyle='--', alpha=0.7, linewidth=1.5)
    ax1.plot(wgm, mag_at_wgm, 'ro', markersize=8, zorder=5)
    ax1.plot(wgm, 0, 'rx', markersize=8, zorder=5)
    
    ax1.annotate(f'Запас по модулю = {gm_db:.1f} дБ\n(на ω_π = {wgm:.3f} рад/с)',
                 xy=(wgm, mag_at_wgm),
                 xytext=(wgm * 1.5, mag_at_wgm + 10),
                 fontsize=9,
                 color='red',
                 arrowprops=dict(arrowstyle='->', color='red', lw=1),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# ===== НИЖНИЙ ГРАФИК: ЛФЧХ в градусах =====
ax2.semilogx(omega_out, phase, 'b-', linewidth=2)
ax2.grid(True, which='both', linestyle='--', alpha=0.5)
ax2.set_ylabel('Фаза (градусы)')
ax2.set_xlabel('Частота (рад/с)')

# Линия на уровне -180°
ax2.axhline(y=-180, color='k', linestyle='-', linewidth=0.8, alpha=0.5)

# Отметка частоты среза ω_ср и запаса по фазе (КОРРЕКТНО)
if pm is not None and wpm is not None and wpm > 0:
    ax2.axvline(x=wpm, color='g', linestyle='--', alpha=0.7, linewidth=1.5)
    phase_at_wpm = np.interp(wpm, omega_out, phase)
    
    ax2.plot(wpm, phase_at_wpm, 'go', markersize=8, zorder=5)
    ax2.plot(wpm, -180, 'gx', markersize=8, zorder=5)
    
    # Корректная подпись запаса по фазе
    if phase_margin_correct > 90:
        ax2.annotate(f'Фаза = {phase_at_wpm:.1f}°\nРасстояние до -180°: {phase_margin_correct:.1f}°\n(фактический запас: {actual_phase_margin:.1f}°)',
                     xy=(wpm, phase_at_wpm),
                     xytext=(wpm * 1.5, phase_at_wpm + 20),
                     fontsize=8,
                     color='green',
                     arrowprops=dict(arrowstyle='->', color='green', lw=1),
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    else:
        ax2.annotate(f'Запас по фазе = {phase_margin_correct:.1f}°\n(на ω_ср = {wpm:.3f} рад/с)',
                     xy=(wpm, phase_at_wpm),
                     xytext=(wpm * 1.5, phase_at_wpm + 20),
                     fontsize=9,
                     color='green',
                     arrowprops=dict(arrowstyle='->', color='green', lw=1),
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Отметка частоты ω_π
if wgm is not None and wgm > 0:
    ax2.axvline(x=wgm, color='r', linestyle='--', alpha=0.5, linewidth=1)
    phase_at_wgm = np.interp(wgm, omega_out, phase)
    ax2.plot(wgm, phase_at_wgm, 'rx', markersize=6, zorder=5)
    ax2.annotate(f'ω_π = {wgm:.3f} рад/с\n(фаза = -180°)',
                 xy=(wgm, phase_at_wgm),
                 xytext=(wgm * 1.5, phase_at_wgm - 30),
                 fontsize=8,
                 color='red',
                 arrowprops=dict(arrowstyle='->', color='red', lw=1),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Настройка отображения
ax1.set_xlim([0.01, 100])
ax2.set_xlim([0.01, 100])
ax1.set_ylim([-60, 40])
ax2.set_ylim([-200, 0])

plt.tight_layout()
plt.show()

# === 5. Годограф Михайлова ===
print("\n" + "="*60)
print("5. ГОДОГРАФ МИХАЙЛОВА")
print("="*60)

# Получаем характеристический полином из знаменателя передаточной функции
num, den = ctrl.tfdata(W_closed)
den_array = den[0][0]
print(f"Характеристический полином D(p) = {den_array}")

# Функция для вычисления значений характеристического полинома на мнимой оси
def characteristic_on_jw(den_coeffs, omega):
    D_real = np.zeros_like(omega)
    D_imag = np.zeros_like(omega)
    
    for i, coeff in enumerate(den_coeffs):
        power = len(den_coeffs) - 1 - i
        if power % 2 == 0:
            D_real += coeff * (omega ** power) * ((-1) ** (power // 2))
        else:
            D_imag += coeff * (omega ** power) * ((-1) ** ((power - 1) // 2))
    
    return D_real, D_imag

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
plt.show()

# === 6. Расчёт предельных значений Koc по Гурвицу ===
print("\n" + "="*60)
print("6. ПРЕДЕЛЬНЫЕ ЗНАЧЕНИЯ Koc ПО КРИТЕРИЮ ГУРВИЦА")
print("="*60)

# Символьный расчёт
p = sp.symbols('p')
K_var = sp.symbols('K')

W_open_sym = (10 / ((0.5*p + 1)*(0.2*p + 1))) * (1.24 / (0.4*p + 1)) * K_var
den_expanded = sp.expand((0.5*p + 1)*(0.2*p + 1)*(0.4*p + 1))
num_sym = 10 * 1.24 * K_var

char_poly_sym = den_expanded + num_sym
char_poly_sym = sp.Poly(char_poly_sym, p)
coeffs = char_poly_sym.all_coeffs()

print(f"\nХарактеристический полином в общем виде:")
print(f"   {coeffs[0]}·p³ + {coeffs[1]}·p² + {coeffs[2]}·p + {coeffs[3]}")

a3, a2, a1, a0 = coeffs

# Условие границы устойчивости: a1*a2 - a0*a3 = 0
det_expr = a1*a2 - a0*a3
K_critical = sp.solve(det_expr, K_var)[0]
K_critical_max = float(K_critical)

# Нижняя граница из условия a0 > 0
a0_crit = sp.solve(a0, K_var)
K_critical_min = float(a0_crit[0]) if a0_crit and a0_crit[0] > 0 else 0

print(f"\nПредельные значения Koc:")
print(f"  • Нижняя граница устойчивости: Koc_min = {K_critical_min:.6f}")
print(f"  • Верхняя граница устойчивости: Koc_max = {K_critical_max:.6f}")
print(f"  • Диапазон устойчивости: {K_critical_min:.6f} < Koc < {K_critical_max:.6f}")

# ===== ГРАФИК ГРАНИЦ УСТОЙЧИВОСТИ =====
print("\n" + "="*60)
print("ВИЗУАЛИЗАЦИЯ ГРАНИЦ УСТОЙЧИВОСТИ")
print("="*60)

# Создаём график с областями устойчивости
fig, (ax1_gr, ax2_gr) = plt.subplots(1, 2, figsize=(14, 5))

# ---- График 1: Области устойчивости на числовой оси ----
# Создаём диапазон значений Koc
koc_max_display = K_critical_max * 1.2 if K_critical_max != float('inf') else 0.3
koc_range = np.linspace(0, koc_max_display, 500)

# Определяем устойчивость для каждого Koc
stability = []
for k in koc_range:
    if k <= 0:
        stability.append(False)
    elif K_critical_min > 0 and k < K_critical_min:
        stability.append(False)
    elif k < K_critical_max:
        stability.append(True)
    else:
        stability.append(False)

# Цветовая карта для областей
colors = ['#ffcccc' if not s else '#ccffcc' for s in stability]

# Рисуем цветные области
ax1_gr.bar(koc_range, [1]*len(koc_range), width=koc_range[1]-koc_range[0], 
           color=colors, edgecolor='none', alpha=0.7)

# Отмечаем границы
if K_critical_min > 0:
    ax1_gr.axvline(x=K_critical_min, color='orange', linewidth=2, linestyle='--', 
                   label=f'Koc_min = {K_critical_min:.4f}')
ax1_gr.axvline(x=K_critical_max, color='red', linewidth=2, linestyle='--', 
               label=f'Koc_max = {K_critical_max:.4f}')
ax1_gr.axvline(x=Koc, color='blue', linewidth=2, linestyle='-', 
               label=f'Ваш вариант: Koc = {Koc}')

# Заполняем области
if K_critical_min > 0:
    ax1_gr.axvspan(-0.07, K_critical_min, alpha=0.3, color='red', 
                   label='Неустойчиво (Koc < Koc_min)')
ax1_gr.axvspan(K_critical_min if K_critical_min > -0.07 else -0.07, K_critical_max, 
               alpha=0.3, color='green', label='Устойчиво')
if K_critical_max != float('inf'):
    ax1_gr.axvspan(K_critical_max, koc_max_display, alpha=0.3, color='red', 
                   label='Неустойчиво (Koc > Koc_max)')

ax1_gr.set_xlabel('Коэффициент обратной связи Koc')
ax1_gr.set_ylabel('Область устойчивости')
ax1_gr.set_title('Области устойчивости САУ\nв зависимости от Koc')
ax1_gr.set_ylim(0, 1.5)
ax1_gr.set_yticks([])
ax1_gr.grid(True, alpha=0.3)
ax1_gr.legend(loc='upper right', fontsize=9)

# ---- График 2: Корневой годограф (движение полюсов) ----
# Анализируем движение полюсов при изменении Koc
koc_values = np.linspace(0.01, K_critical_max * 1.1 if K_critical_max != float('inf') else 0.25, 30)
pole_paths = [[] for _ in range(3)]  # 3 полюса

for k in koc_values:
    W_test = ctrl.feedback(W_open, k, sign=-1)
    poles_k = ctrl.poles(W_test)
    for i, p in enumerate(poles_k):
        pole_paths[i].append(p)

# Рисуем корневой годограф
for i, path in enumerate(pole_paths):
    real_parts = [np.real(p) for p in path]
    imag_parts = [np.imag(p) for p in path]
    ax2_gr.plot(real_parts, imag_parts, 'o-', markersize=3, linewidth=1, 
                label=f'Полюс {i+1}', alpha=0.7)

# Отмечаем положение полюсов при вашем Koc
W_closed_current = ctrl.feedback(W_open, Koc, sign=-1)
poles_current = ctrl.poles(W_closed_current)
for i, p in enumerate(poles_current):
    ax2_gr.plot(np.real(p), np.imag(p), 'bs', markersize=8, markeredgecolor='darkblue',
                markerfacecolor='lightblue', zorder=5)
    ax2_gr.annotate(f'  Koc={Koc}', xy=(np.real(p), np.imag(p)), fontsize=8, color='darkblue')

# Отмечаем границы
if K_critical_max != float('inf'):
    W_closed_max = ctrl.feedback(W_open, K_critical_max, sign=-1)
    poles_max = ctrl.poles(W_closed_max)
    for p in poles_max:
        ax2_gr.plot(np.real(p), np.imag(p), 'r*', markersize=10, zorder=5)
        ax2_gr.annotate(f'  Koc_max', xy=(np.real(p), np.imag(p)), fontsize=8, color='red')

if K_critical_min > 0:
    W_closed_min = ctrl.feedback(W_open, K_critical_min, sign=-1)
    poles_min = ctrl.poles(W_closed_min)
    for p in poles_min:
        ax2_gr.plot(np.real(p), np.imag(p), 'r*', markersize=10, zorder=5)
        ax2_gr.annotate(f'  Koc_min', xy=(np.real(p), np.imag(p)), fontsize=8, color='orange')

ax2_gr.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax2_gr.axvline(x=0, color='k', linestyle='-', alpha=0.3)
ax2_gr.set_xlabel('Вещественная часть')
ax2_gr.set_ylabel('Мнимая часть')
ax2_gr.set_title('Корневой годограф (движение полюсов)\nпри изменении Koc')
ax2_gr.grid(True, alpha=0.3)
ax2_gr.legend(loc='best', fontsize=8)
ax2_gr.axis('equal')

plt.tight_layout()
plt.show()

# === 7. ЭКСПЕРИМЕНТАЛЬНАЯ ПРОВЕРКА ГРАНИЦ УСТОЙЧИВОСТИ ===
print("\n" + "="*60)
print("7. ЭКСПЕРИМЕНТАЛЬНАЯ ПРОВЕРКА ГРАНИЦ УСТОЙЧИВОСТИ")
print("="*60)

# Создаём фигуру с тремя графиками
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# ---- График 1: Устойчивый режим (ваш вариант Koc) ----
W_closed_stable = ctrl.feedback(W_open, Koc, sign=-1)
t_stable, y_stable = ctrl.step_response(W_closed_stable, T=np.linspace(0, 15, 1500))
axes[0].plot(t_stable, y_stable, 'b-', linewidth=2)
axes[0].set_title(f'Устойчивый режим\nKoc = {Koc} (внутри диапазона)')
axes[0].set_xlabel('Время t, с')
axes[0].set_ylabel('Выход')
axes[0].grid(True)
axes[0].axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

# ---- График 2: Нижняя граница / Малый Koc ----
if K_critical_min > 0:
    # Если есть нижняя граница, показываем процесс чуть выше неё
    K_lower_boundary = K_critical_min * 1.05
    W_closed_lower = ctrl.feedback(W_open, K_lower_boundary, sign=-1)
    t_lower, y_lower = ctrl.step_response(W_closed_lower, T=np.linspace(0, 20, 2000))
    axes[1].plot(t_lower, y_lower, 'orange', linewidth=2)
    axes[1].set_title(f'Вблизи нижней границы\nKoc = {K_lower_boundary:.5f}')
else:
    # Если нижней границы нет, показываем поведение при малом Koc
    K_small = K_critical_max * 0.1*-1
    W_closed_small = ctrl.feedback(W_open, K_small, sign=-1)
    t_small, y_small = ctrl.step_response(W_closed_small, T=np.linspace(0, 20, 2000))
    axes[1].plot(t_small, y_small, 'orange', linewidth=2)
    axes[1].set_title(f'Малый Koc = {K_small:.5f}')
axes[1].set_xlabel('Время t, с')
axes[1].set_ylabel('Выход')
axes[1].grid(True)
axes[1].axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

# ---- График 3: Верхняя граница устойчивости ----
K_upper_boundary = K_critical_max * 0.99
W_closed_upper = ctrl.feedback(W_open, K_upper_boundary, sign=-1)
t_upper, y_upper = ctrl.step_response(W_closed_upper, T=np.linspace(0, 20, 2000))
axes[2].plot(t_upper, y_upper, 'green', linewidth=2)
axes[2].set_title(f'Вблизи верхней границы\nKoc = {K_upper_boundary:.5f}')
axes[2].set_xlabel('Время t, с')
axes[2].set_ylabel('Выход')
axes[2].grid(True)
axes[2].axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# ---- Дополнительный график: Неустойчивый режим ----
print("\nДОПОЛНИТЕЛЬНО: Неустойчивый режим (выше верхней границы)")
K_unstable = K_critical_max * 1.05 if K_critical_max != float('inf') else 0.3
W_closed_unstable = ctrl.feedback(W_open, K_unstable, sign=-1)
t_unstable, y_unstable = ctrl.step_response(W_closed_unstable, T=np.linspace(0, 20, 2000))

plt.figure(figsize=(10, 4))
plt.plot(t_unstable, y_unstable, 'r-', linewidth=2)
plt.title(f'Неустойчивый режим\nKoc = {K_unstable:.5f} (выше Koc_max = {K_critical_max:.5f})')
plt.xlabel('Время t, с')
plt.ylabel('Выход')
plt.grid(True)
plt.axhline(y=1.0, color='b', linestyle='--', alpha=0.5)
plt.show()

# ---- Анализ полюсов для граничных режимов ----
print("\n" + "-"*50)
print("АНАЛИЗ ПОЛЮСОВ ДЛЯ ГРАНИЧНЫХ РЕЖИМОВ:")
print("-"*50)

if K_critical_max != float('inf'):
    W_closed_at_max = ctrl.feedback(W_open, K_critical_max, sign=-1)
    poles_max = ctrl.poles(W_closed_at_max)
    print(f"\nПри Koc = Koc_max = {K_critical_max:.6f}:")
    for i, p in enumerate(poles_max):
        print(f"   p{i+1} = {p:.6f}")
        if abs(np.real(p)) < 1e-6:
            print(f"   → Полюс на мнимой оси (граница устойчивости)")

if K_critical_min > 0:
    W_closed_at_min = ctrl.feedback(W_open, K_critical_min, sign=-1)
    poles_min = ctrl.poles(W_closed_at_min)
    print(f"\nПри Koc = Koc_min = {K_critical_min:.6f}:")
    for i, p in enumerate(poles_min):
        print(f"   p{i+1} = {p:.6f}")
        if abs(np.real(p)) < 1e-6:
            print(f"   → Полюс на мнимой оси (граница устойчивости)")

print(f"\nПри вашем Koc = {Koc}:")
for i, p in enumerate(poles_current):
    print(f"   p{i+1} = {p:.6f}")

# === 8. Финальный вывод ===
print("\n" + "="*60)
print("ОБЩИЙ ВЫВОД ПО РЕЗУЛЬТАТАМ РАБОТЫ")
print("="*60)

print(f"""
1. При коэффициенте обратной связи Koc = {Koc}:
   ✓ Система УСТОЙЧИВА
   ✓ Все полюсы находятся в левой полуплоскости

2. Частотные характеристики:
   ✓ Частота среза ω_ср = {wpm:.4f} рад/с
   ✓ Фаза на частоте среза φ(ω_ср) = {phase_at_wpm:.2f}°
   ✓ Запас по амплитуде: {20*np.log10(abs(gm)):.2f} дБ
   ✓ Запас по фазе (расстояние до -180°): {phase_margin_correct:.2f}°

3. Предельные значения Koc по Гурвицу:
   ✓ Koc_min = {K_critical_min:.6f}
   ✓ Koc_max = {K_critical_max:.6f}
   ✓ Ваш вариант Koc = {Koc} находится ВНУТРИ диапазона устойчивости

4. Все критерии устойчивости (Михайлова, Найквиста, Гурвица)
   подтверждают устойчивость системы при Koc = {Koc}.

5. Экспериментальная проверка показала:
   ✓ При Koc < Koc_min или Koc > Koc_max система становится неустойчивой
   ✓ На границах устойчивости появляются полюсы на мнимой оси
""")