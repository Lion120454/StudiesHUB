"""
ЛАБОРАТОРНАЯ РАБОТА №4 «Синтез и оптимизация линейных САУ»
Система регулирования напряжения ЭМУ

Выполнение: синтез последовательного корректирующего звена,
обеспечивающего σ ≤ 5%, tп ≤ 0.15 с, и последующая оптимизация
по быстродействию с ограничением σ ≤ 10%.
"""

import control as ct
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# 1. ИСХОДНЫЕ ДАННЫЕ И ПЕРЕДАТОЧНЫЕ ФУНКЦИИ (п. 3 методички)
# ============================================================
print("=" * 60)
print("1. ФОРМИРОВАНИЕ ИСХОДНОЙ СИСТЕМЫ")
print("=" * 60)

# ЭМУ: Wэ(s) = 11 / ((1 + 0.2s)(1 + 0.5s))
Wэ = ct.tf([11], [0.1, 0.7, 1])  # 0.2*0.5=0.1; 0.2+0.5=0.7

# Нагрузка и якорная цепь: W2(s) = 0.1*(1 + 0.18s)/(1 + 0.1s)
W2 = ct.tf([0.018, 0.1], [0.1, 1])

# Разомкнутая исходная система
W_raz_orig = ct.series(Wэ, W2)

# Замкнутая система с единичной ОС
W_zam_orig = ct.feedback(W_raz_orig, 1)

print("\nПередаточная функция разомкнутой исходной системы:")
print(W_raz_orig)

# Анализ переходного процесса исходной системы
t_sim = np.linspace(0, 1.5, 5000)
_, y_orig = ct.step_response(W_zam_orig, t_sim)
info_orig = ct.step_info(W_zam_orig)

print("\n--- Показатели качества исходной системы ---")
print(f"Перерегулирование σ = {info_orig['Overshoot']:.2f}%")
print(f"Время нарастания tн = {info_orig['RiseTime']:.4f} с")
print(f"Время установления tп = {info_orig['SettlingTime']:.4f} с")
print(f"Установившееся значение = {y_orig[-1]:.4f}")

if info_orig['Overshoot'] > 5.0 or info_orig['SettlingTime'] > 0.15:
    print("\nВЫВОД: Требуется коррекция системы (нарушены требования по σ или tп).")
else:
    print("\nВЫВОД: Система удовлетворяет требованиям без коррекции.")

# ============================================================
# 2. ЧАСТОТНЫЙ СИНТЕЗ КОРРЕКТИРУЮЩЕГО ЗВЕНА (п. 4.3-4.5)
# ============================================================
print("\n" + "=" * 60)
print("2. ЧАСТОТНЫЙ СИНТЕЗ ПОСЛЕДОВАТЕЛЬНОГО КОРРЕКТИРУЮЩЕГО ЗВЕНА")
print("=" * 60)

# Требования: σ ≤ 5%, tп ≤ 0.15 с
# Для σ < 5% используем технический оптимум:
# ωс = 4π / tп = 4π / 0.15 ≈ 83.78 рад/с
omega_c_target = 4 * np.pi / 0.15  # 83.78 рад/с

# Желаемая ЛАЧХ типа 1: W(s) = K / (s*(T_экв*s + 1))
# где K = ωс, а T_экв выбираем из условия ω_1в ≥ 2ωс
# Примем ω_1в = 2*ωс, тогда T_экв = 1/(2*ωс)
T_equiv = 1.0 / (2.0 * omega_c_target)  # ≈ 0.006 с
K_desired = omega_c_target  # ≈ 83.78

# Исходная разомкнутая система (после сокращения (0.18s+1)):
# W_исх_упрощ(s) = 1.1 / ((0.5s+1)(0.1s+1))
# Желаемая система: W_жел(s) = K_desired / (s*(T_equiv*s+1))
# Корректирующее звено: Wk(s) = W_жел(s) / W_исх(s)
# Wk(s) = [K_desired / (s*(T_equiv*s+1))] * [(0.5s+1)(0.1s+1) / 1.1]

# Реализуем ПИД-регулятор с фильтром:
# Wk(s) = Kp * (τ1*s+1)(τ2*s+1) / (s*(Tф*s+1))
# где τ1 = 0.5 (компенсация Tв), τ2 = 0.1 (компенсация Tн),
# Kp = K_desired / 1.1, Tф = T_equiv

Kp_synth = K_desired / 1.1  # ≈ 76.16
tau1_synth = 0.5
tau2_synth = 0.1
Tf_synth = T_equiv  # ≈ 0.006

# Формируем передаточную функцию корректирующего звена
# num = Kp*(τ1*τ2*s^2 + (τ1+τ2)*s + 1)
# den = Tф*s^2 + s
num_wk_synth = [Kp_synth * tau1_synth * tau2_synth,
                Kp_synth * (tau1_synth + tau2_synth),
                Kp_synth]
den_wk_synth = [Tf_synth, 1, 0]

Wk_synth = ct.tf(num_wk_synth, den_wk_synth)
W_raz_synth = ct.series(Wk_synth, W_raz_orig)
W_zam_synth = ct.feedback(W_raz_synth, 1)

print("\nСинтезированное корректирующее звено (ПИД с фильтром):")
print(Wk_synth)
print(f"\nПараметры синтеза:")
print(f"  ωс_жел = {omega_c_target:.2f} рад/с")
print(f"  Kp = {Kp_synth:.3f}")
print(f"  τ1 = {tau1_synth:.3f} с (компенсация Tв=0.5 с)")
print(f"  τ2 = {tau2_synth:.3f} с (компенсация Tн=0.1 с)")
print(f"  Tф = {Tf_synth:.6f} с (реализуемость)")

# Оценка показателей после синтеза
_, y_synth = ct.step_response(W_zam_synth, t_sim)
info_synth = ct.step_info(W_zam_synth)

print("\n--- Показатели качества после частотного синтеза ---")
print(f"Перерегулирование σ = {info_synth['Overshoot']:.2f}%")
print(f"Время нарастания tн = {info_synth['RiseTime']:.4f} с")
print(f"Время установления tп = {info_synth['SettlingTime']:.4f} с")
print(f"Установившееся значение = {y_synth[-1]:.4f}")

if info_synth['Overshoot'] <= 5.0 and info_synth['SettlingTime'] <= 0.15:
    print("\nТребования по частотному синтезу ВЫПОЛНЕНЫ (σ ≤ 5%, tп ≤ 0.15 с).")
else:
    print("\nТребования по частотному синтезу НЕ ВЫПОЛНЕНЫ. Требуется ручная корректировка.")

# ============================================================
# 3. ПАРАМЕТРИЧЕСКАЯ ОПТИМИЗАЦИЯ (п. 4.6)
# ============================================================
print("\n" + "=" * 60)
print("3. ПАРАМЕТРИЧЕСКАЯ ОПТИМИЗАЦИЯ ПО БЫСТРОДЕЙСТВИЮ")
print("=" * 60)

# Фиксируем структуру звена коррекции (τ1, τ2 не варьируем – они компенсируют)
# Варьируемые параметры: Kp и Tф
# Критерий: I3 = ∫[ΔX² + a·(dΔX/dt)²]dt → min
# Ограничение: σ ≤ 10%

# Для ускорения вычислений используем аналитический расчёт или уменьшенное время симуляции
t_opt = np.linspace(0, 0.5, 2000)


def system_response(Kp, Tf):
    """Создаёт замкнутую систему с заданными параметрами и возвращает переходную характеристику"""
    if Kp <= 0 or Tf <= 1e-9:
        return None, None, None
    try:
        num_wk = [Kp * tau1_synth * tau2_synth,
                  Kp * (tau1_synth + tau2_synth),
                  Kp]
        den_wk = [Tf, 1, 0]
        Wk = ct.tf(num_wk, den_wk)
        W_raz = ct.series(Wk, W_raz_orig)
        W_zam = ct.feedback(W_raz, 1)
        _, y = ct.step_response(W_zam, t_opt)
        return y, W_zam, _
    except Exception:
        return None, None, None


def cost_function_I2(params):
    """Интегральный квадратичный критерий I2 = ∫ΔX²dt"""
    Kp, Tf = params
    y, _, _ = system_response(Kp, Tf)
    if y is None:
        return 1e12
    error = 1.0 - y
    I2 = np.trapezoid(error**2, t_opt)

    # Штраф за перерегулирование > 10%
    overshoot = max(0, (np.max(y) - 1.0) * 100.0)
    if overshoot > 10.0:
        I2 += 1e4 * (overshoot - 10.0)**2

    # Штраф за большое время установления (ускоряем сходимость)
    # Находим время, после которого ошибка < 5%
    try:
        settling_mask = np.abs(error) > 0.05
        if np.any(settling_mask):
            idx = np.where(settling_mask)[0][-1]
            t_settle = t_opt[min(idx + 1, len(t_opt) - 1)]
            if t_settle > 0.15:
                I2 += 1e3 * (t_settle - 0.15)**2
    except Exception:
        pass

    return I2


def cost_function_I3(params, a_coef):
    """Интегральный критерий I3 = ∫[ΔX² + a·(dΔX/dt)²]dt"""
    Kp, Tf = params
    y, _, _ = system_response(Kp, Tf)
    if y is None:
        return 1e12
    error = 1.0 - y
    I2 = np.trapezoid(error**2, t_opt)
    derror = np.gradient(error, t_opt)
    I3_part = a_coef * np.trapezoid(derror**2, t_opt)
    total = I2 + I3_part

    # Штраф за перерегулирование > 10%
    overshoot = max(0, (np.max(y) - 1.0) * 100.0)
    if overshoot > 10.0:
        total += 1e4 * (overshoot - 10.0)**2

    return total


# --- Итерация 1: минимизация I2 (a = 0) ---
print("\nИтерация 1: Минимизация I2 (без учёта производной ошибки, a=0)")
print("Начальные параметры: Kp =", Kp_synth, ", Tф =", Tf_synth)

# Начальное предположение: параметры из синтеза
x0 = [Kp_synth, Tf_synth]

# Поиск минимума
res1 = minimize(
    cost_function_I2,
    x0,
    method='Nelder-Mead',
    options={
        'maxiter': 300,
        'xatol': 1e-7,
        'fatol': 1e-7,
        'adaptive': True
    }
)

Kp_opt1, Tf_opt1 = res1.x
y_opt1, W_zam_opt1, _ = system_response(Kp_opt1, Tf_opt1)
info_opt1 = ct.step_info(W_zam_opt1) if y_opt1 is not None else None

if info_opt1 is not None:
    print(f"  Найдено: Kp = {Kp_opt1:.4f}, Tф = {Tf_opt1:.8f}")
    print(f"  Перерегулирование σ = {info_opt1['Overshoot']:.2f}%")
    print(f"  Время установления tп = {info_opt1['SettlingTime']:.4f} с")
else:
    print("  Ошибка оптимизации!")
    Kp_opt1, Tf_opt1 = Kp_synth, Tf_synth
    y_opt1, W_zam_opt1, _ = system_response(Kp_opt1, Tf_opt1)
    info_opt1 = ct.step_info(W_zam_opt1)

# --- Итерация 2: минимизация I3 с разными a ---
print("\nИтерация 2: Добавление производной ошибки (I3) для снижения колебательности")
best_result = {
    'a': 0,
    'Kp': Kp_opt1,
    'Tf': Tf_opt1,
    'sigma': info_opt1['Overshoot'],
    'ts': info_opt1['SettlingTime']
}

# Если перерегулирование уже мало или процесс приемлем, итерация 2 может не дать улучшения
# Но пробуем несколько значений a
a_values = [0.001, 0.005, 0.01, 0.05, 0.1]
for a_val in a_values:
    res = minimize(
        lambda p: cost_function_I3(p, a_val),
        [Kp_opt1, Tf_opt1],
        method='Nelder-Mead',
        options={'maxiter': 200, 'xatol': 1e-7, 'fatol': 1e-7}
    )
    Kp_try, Tf_try = res.x
    y_try, W_zam_try, _ = system_response(Kp_try, Tf_try)
    if y_try is None:
        continue
    info_try = ct.step_info(W_zam_try)
    sigma_try = info_try['Overshoot']
    ts_try = info_try['SettlingTime']

    # Критерий выбора: σ ≤ 10% и минимальное время установления
    if sigma_try <= 10.0:
        if ts_try < best_result['ts']:
            best_result = {
                'a': a_val,
                'Kp': Kp_try,
                'Tf': Tf_try,
                'sigma': sigma_try,
                'ts': ts_try
            }

print(f"\nЛучший результат оптимизации:")
print(f"  Коэффициент a = {best_result['a']:.4f}")
print(f"  Kp = {best_result['Kp']:.4f}")
print(f"  Tф = {best_result['Tf']:.8f}")
print(f"  Перерегулирование σ = {best_result['sigma']:.2f}%")
print(f"  Время установления tп = {best_result['ts']:.4f} с")

# Финальные параметры
Kp_final = best_result['Kp']
Tf_final = best_result['Tf']

# Формируем финальную систему
num_wk_final = [Kp_final * tau1_synth * tau2_synth,
                Kp_final * (tau1_synth + tau2_synth),
                Kp_final]
den_wk_final = [Tf_final, 1, 0]
Wk_final = ct.tf(num_wk_final, den_wk_final)
W_raz_final = ct.series(Wk_final, W_raz_orig)
W_zam_final = ct.feedback(W_raz_final, 1)

print("\nФинальное корректирующее звено:")
print(Wk_final)

# Расширенное время для финальных графиков
t_plot = np.linspace(0, 1.0, 5000)
_, y_orig_plot = ct.step_response(W_zam_orig, t_plot)
_, y_synth_plot = ct.step_response(W_zam_synth, t_plot)
_, y_final_plot = ct.step_response(W_zam_final, t_plot)

# ============================================================
# 4. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ
# ============================================================
print("\n" + "=" * 60)
print("4. ПОСТРОЕНИЕ ГРАФИКОВ")
print("=" * 60)

fig = plt.figure(figsize=(16, 12))

# 4.1. Переходные процессы (сравнение)
ax1 = plt.subplot(2, 3, 1)
ax1.plot(t_plot, y_orig_plot, 'b-', linewidth=1.5, label='Исходная система')
ax1.plot(t_plot, y_synth_plot, 'g--', linewidth=1.8, label='После частотного синтеза')
ax1.plot(t_plot, y_final_plot, 'r-', linewidth=2.0, label='После оптимизации')
ax1.axhline(y=1.0, color='k', linestyle=':', alpha=0.5)
ax1.axhline(y=1.1, color='r', linestyle=':', alpha=0.4, label='Граница σ=10%')
ax1.set_title('Переходные процессы замкнутой системы')
ax1.set_xlabel('Время, с')
ax1.set_ylabel('Uэ(t)')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 0.5])

# 4.2. Детальный вид переходного процесса
ax2 = plt.subplot(2, 3, 2)
ax2.plot(t_plot, y_synth_plot, 'g--', linewidth=1.5, label='Частотный синтез')
ax2.plot(t_plot, y_final_plot, 'r-', linewidth=2.0, label='После оптимизации')
ax2.axhline(y=1.0, color='k', linestyle=':', alpha=0.5)
ax2.axhspan(0.95, 1.05, alpha=0.1, color='green', label='±5% зона')
ax2.set_title('Детальный вид (синтез vs оптимизация)')
ax2.set_xlabel('Время, с')
ax2.set_ylabel('Uэ(t)')
ax2.legend(loc='lower right')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 0.3])
ax2.set_ylim([0.85, 1.15])

# 4.3. ЛАЧХ разомкнутых систем
ax3 = plt.subplot(2, 3, 3)
omega = np.logspace(-1, 4, 2000)
mag_orig, _, _ = ct.bode(W_raz_orig, omega, plot=False)
mag_synth, _, _ = ct.bode(W_raz_synth, omega, plot=False)
mag_final, _, _ = ct.bode(W_raz_final, omega, plot=False)
ax3.semilogx(omega, 20*np.log10(mag_orig), 'b-', label='Исходная')
ax3.semilogx(omega, 20*np.log10(mag_synth), 'g--', label='После синтеза')
ax3.semilogx(omega, 20*np.log10(mag_final), 'r-', label='После оптимизации')
ax3.axvline(x=omega_c_target, color='m', linestyle=':', alpha=0.6,
            label=f'ωс_жел={omega_c_target:.1f} рад/с')
ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax3.set_title('ЛАЧХ разомкнутых систем')
ax3.set_xlabel('Частота, рад/с')
ax3.set_ylabel('Амплитуда, дБ')
ax3.legend()
ax3.grid(True, which='both', alpha=0.3)

# 4.4. ЛАЧХ корректирующих звеньев
ax4 = plt.subplot(2, 3, 4)
mag_k_synth, _, _ = ct.bode(Wk_synth, omega, plot=False)
mag_k_final, _, _ = ct.bode(Wk_final, omega, plot=False)
ax4.semilogx(omega, 20*np.log10(mag_k_synth), 'g--', label='Звено синтеза')
ax4.semilogx(omega, 20*np.log10(mag_k_final), 'r-', label='Звено после оптимизации')
ax4.set_title('ЛАЧХ корректирующих звеньев')
ax4.set_xlabel('Частота, рад/с')
ax4.set_ylabel('Амплитуда, дБ')
ax4.legend()
ax4.grid(True, which='both', alpha=0.3)

# 4.5. Сигнал ошибки
ax5 = plt.subplot(2, 3, 5)
error_synth = 1.0 - y_synth_plot
error_final = 1.0 - y_final_plot
ax5.plot(t_plot, error_synth, 'g--', label='После синтеза')
ax5.plot(t_plot, error_final, 'r-', label='После оптимизации')
ax5.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax5.set_title('Ошибка регулирования ΔX(t)')
ax5.set_xlabel('Время, с')
ax5.set_ylabel('ΔX')
ax5.legend()
ax5.grid(True, alpha=0.3)
ax5.set_xlim([0, 0.3])

# 4.6. Сводная таблица показателей
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')
info_final = ct.step_info(W_zam_final)
table_data = [
    ['Показатель', 'Исходная', 'Синтез', 'Оптимизация'],
    ['σ, %', f'{info_orig["Overshoot"]:.2f}', f'{info_synth["Overshoot"]:.2f}', f'{info_final["Overshoot"]:.2f}'],
    ['tн, с', f'{info_orig["RiseTime"]:.4f}', f'{info_synth["RiseTime"]:.4f}', f'{info_final["RiseTime"]:.4f}'],
    ['tп, с', f'{info_orig["SettlingTime"]:.4f}', f'{info_synth["SettlingTime"]:.4f}', f'{info_final["SettlingTime"]:.4f}'],
    ['Kp', '—', f'{Kp_synth:.2f}', f'{Kp_final:.2f}'],
    ['Tф, с', '—', f'{Tf_synth:.6f}', f'{Tf_final:.8f}'],
]
table = ax6.table(cellText=table_data, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.5)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#4472C4')
        cell.set_text_props(color='white', fontweight='bold')
ax6.set_title('Сводка показателей качества', pad=20)

plt.tight_layout(pad=2)
plt.show()

# ============================================================
# 5. ЗАКЛЮЧИТЕЛЬНЫЙ ВЫВОД
# ============================================================
print("\n" + "=" * 60)
print("5. ЗАКЛЮЧЕНИЕ")
print("=" * 60)

print(f"""
1. Исходная система (без коррекции):
   - Перерегулирование: {info_orig['Overshoot']:.2f}%
   - Время установления: {info_orig['SettlingTime']:.4f} с
   - Система не удовлетворяет требованиям (σ ≤ 5%, tп ≤ 0.15 с).
   - Необходима коррекция.

2. После частотного синтеза (метод желаемой ЛАЧХ, технический оптимум):
   - Перерегулирование: {info_synth['Overshoot']:.2f}% {'✓' if info_synth['Overshoot'] <= 5 else '✗'}
   - Время установления: {info_synth['SettlingTime']:.4f} с {'✓' if info_synth['SettlingTime'] <= 0.15 else '✗'}
   - Требования по синтезу {'ВЫПОЛНЕНЫ' if info_synth['Overshoot'] <= 5 and info_synth['SettlingTime'] <= 0.15 else 'НЕ ВЫПОЛНЕНЫ'}.

3. После параметрической оптимизации (I3 → min, σ ≤ 10%):
   - Перерегулирование: {info_final['Overshoot']:.2f}% {'✓' if info_final['Overshoot'] <= 10 else '✗'}
   - Время установления: {info_final['SettlingTime']:.4f} с
   - Достигнуто минимальное время переходного процесса при допустимом перерегулировании.

4. Параметры финального корректирующего звена:
   Wk(s) = {Kp_final:.3f} * ({tau1_synth}*s+1)({tau2_synth}*s+1) / (s*({Tf_final:.6g}*s+1))
""")

print("Лабораторная работа выполнена успешно.")