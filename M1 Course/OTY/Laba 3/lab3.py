import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# ==========================
# 1. Параметры системы (вариант)
# ==========================
K = 25  # коэффициент регулятора скорости W1(s) = K (задаётся по варианту)

# Передаточные функции звеньев
W1 = ctrl.TransferFunction([K], [1])                     # K
W2 = ctrl.TransferFunction([0.1], [0.001, 1])           # 0.1/(1+0.001s)
W3 = ctrl.TransferFunction([10], [0.04, 1])             # 10/(1+0.04s)
W4 = ctrl.TransferFunction([1], [0.004, 0.376])         # 1/(0.004s + 0.376)
W5 = ctrl.TransferFunction([0.8], [1])                  # 0.8
W6 = ctrl.TransferFunction([1], [0.065, 0])             # 1/(0.065s) -> интегратор
W7 = ctrl.TransferFunction([0.8], [1])                  # 0.8
W8 = ctrl.TransferFunction([0.8], [1])                  # ДТ
W9 = ctrl.TransferFunction([0.14], [1])                 # ДС

# Построение модели двигателя с внутренней обратной связью по ЭДС
# Двигатель: напряжение -> ток -> момент -> скорость
# W4: ток/напряжение = 1/(R + Ls)
# W5: момент/ток = 0.8
# W6: скорость/момент = 1/(Js)
# W7: ЭДС/скорость = 0.8
# Обратная связь по ЭДС: Uп = U - W7*omega

# Прямая цепь двигателя: ток -> момент -> скорость
motor_forward = ctrl.series(W4, W5)  # напряжение -> момент
motor_forward = ctrl.series(motor_forward, W6)  # напряжение -> скорость
# Замкнутый двигатель с учётом ЭДС
motor = ctrl.feedback(motor_forward, W7, sign=-1)

# Разомкнутая система (без датчика скорости)
open_loop = ctrl.series(W1, W2)
open_loop = ctrl.series(open_loop, W3)
open_loop = ctrl.series(open_loop, motor)

# Замкнутая система с датчиком скорости
closed_loop = ctrl.feedback(open_loop, W9, sign=-1)

print("Передаточная функция замкнутой системы:")
print(closed_loop)

# ==========================
# 2. Прямые оценки качества по переходной характеристике
# ==========================
t, y = ctrl.step_response(closed_loop, T=np.linspace(0, 2, 5000))
y_final = y[-1]
delta = 0.05 * y_final  # 5% зона

# Время регулирования (последнее вхождение в 5% зону)
in_zone = np.abs(y - y_final) <= delta
t_reg_idx = np.where(in_zone)[0]
if len(t_reg_idx) > 0:
    # Находим последний выход из зоны
    changes = np.diff(in_zone.astype(int))
    last_exit = np.where(changes == -1)[0]
    if len(last_exit) > 0:
        t_reg_start = last_exit[-1] + 1
        t_reg = t[t_reg_idx[t_reg_idx >= t_reg_start][0]] if len(t_reg_idx[t_reg_idx >= t_reg_start]) > 0 else t[-1]
    else:
        t_reg = t[t_reg_idx[0]]
else:
    t_reg = t[-1]

# Перерегулирование
y_max = np.max(y)
overshoot = (y_max - y_final) / y_final * 100

# Время первого максимума
t_max = t[np.argmax(y)]

# Время нарастания (10% -> 90%)
y_10 = 0.1 * y_final
y_90 = 0.9 * y_final
idx_10 = np.where(y >= y_10)[0]
idx_90 = np.where(y >= y_90)[0]
if len(idx_10) > 0 and len(idx_90) > 0:
    t_rise = t[idx_90[0]] - t[idx_10[0]]
else:
    t_rise = 0

# Частота и число колебаний
peaks, _ = find_peaks(y)
if len(peaks) > 1:
    T0 = t[peaks[1]] - t[peaks[0]]
    omega = 2 * np.pi / T0
    # Число колебаний за время регулирования
    peaks_in_reg = peaks[t[peaks] <= t_reg]
    n_osc = len(peaks_in_reg)
else:
    omega = 0
    n_osc = 0

print("\n=== Прямые оценки качества ===")
print(f"Время регулирования (5%): {t_reg:.4f} с")
print(f"Перерегулирование: {overshoot:.2f} %")
print(f"Время первого максимума: {t_max:.4f} с")
print(f"Время нарастания (10-90%): {t_rise:.4f} с")
print(f"Частота колебаний: {omega:.2f} рад/с")
print(f"Число колебаний за t_reg: {n_osc}")

# График переходной характеристики
plt.figure(figsize=(12, 6))
plt.plot(t, y, 'b-', linewidth=1.5, label='h(t)')
plt.axhline(y=y_final, color='k', linestyle='--', linewidth=1, label='Установившееся значение')
plt.axhline(y=y_final+delta, color='r', linestyle=':', linewidth=1, label='±5% зона')
plt.axhline(y=y_final-delta, color='r', linestyle=':', linewidth=1)
plt.axvline(x=t_reg, color='g', linestyle='--', linewidth=1, label=f't_reg = {t_reg:.3f} с')
plt.xlabel('Время, с', fontsize=12)
plt.ylabel('Скорость (отн. ед.)', fontsize=12)
plt.title('Переходная характеристика замкнутой САУ', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# ==========================
# 3. Корневые оценки качества
# ==========================
# Получение полюсов и нулей
poles = ctrl.poles(closed_loop)
zeros = ctrl.zeros(closed_loop)

# Степень устойчивости αmin
stable_poles = [p for p in poles if np.real(p) < 0]
if stable_poles:
    alpha_min = min(-np.real(p) for p in stable_poles)
    t_peq = 3 / alpha_min if alpha_min > 0 else np.inf
    
    # Колебательность μ = max(|Im/Re|)
    mu_vals = [abs(np.imag(p)/np.real(p)) for p in stable_poles if np.real(p) < 0 and np.imag(p) != 0]
    mu = max(mu_vals) if mu_vals else 0
else:
    alpha_min = 0
    t_peq = np.inf
    mu = 0

print("\n=== Корневые оценки качества ===")
print(f"Степень устойчивости αmin: {alpha_min:.4f}")
print(f"Время переходного процесса (3/αmin): {t_peq:.4f} с")
print(f"Колебательность μ: {mu:.4f}")
print(f"\nВсе полюсы системы:")
for i, p in enumerate(poles):
    print(f"  p{i+1} = {p:.4f}")

# Построение расположения полюсов
plt.figure(figsize=(10, 8))
plt.plot(np.real(poles), np.imag(poles), 'rx', markersize=10, linewidth=2, label='Полюсы')
if len(zeros) > 0:
    plt.plot(np.real(zeros), np.imag(zeros), 'bo', markersize=8, fillstyle='none', linewidth=2, label='Нули')
plt.axhline(0, color='k', linewidth=0.5)
plt.axvline(0, color='k', linewidth=0.5)
plt.xlabel('Re', fontsize=12)
plt.ylabel('Im', fontsize=12)
plt.title('Распределение полюсов и нулей замкнутой САУ на комплексной плоскости', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend()
plt.axis('equal')
plt.tight_layout()
plt.show()

# ==========================
# 4. Запасы устойчивости разомкнутой системы
# ==========================
# Разомкнутая система (без датчика скорости в цепи ОС)
# Используем ту же open_loop, что и ранее

# Расчёт запасов устойчивости
try:
    gm, pm, wgm, wpm = ctrl.margin(open_loop)
    print("\n=== Запасы устойчивости разомкнутой САУ ===")
    print(f"Запас по фазе: {pm:.2f} град (на частоте {wpm:.4f} рад/с)")
    print(f"Запас по модулю: {20*np.log10(gm):.2f} дБ (на частоте {wgm:.4f} рад/с)")
except:
    print("\n=== Запасы устойчивости разомкнутой САУ ===")
    print("Не удалось автоматически рассчитать запасы устойчивости")
    gm, pm, wgm, wpm = np.inf, np.inf, 0, 0

# Построение ЛАЧХ и ЛФЧХ
plt.figure(figsize=(12, 8))
ctrl.bode(open_loop, dB=True, deg=True, margins=True)
plt.suptitle("Логарифмические частотные характеристики разомкнутой САУ", fontsize=14)
plt.tight_layout()
plt.show()

# Дополнительно: годограф Найквиста
plt.figure(figsize=(8, 8))
ctrl.nyquist(open_loop)
plt.title('Годограф Найквиста разомкнутой системы', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ==========================
# 5. Вывод всех ТФ для отчёта
# ==========================
print("\n=== Передаточные функции звеньев ===")
print(f"W1 (регулятор скорости): {W1}")
print(f"W2 (регулятор тока): {W2}")
print(f"W3 (ТП): {W3}")
print(f"W4 (R+Lp): {W4}")
print(f"W5 (момент/ток): {W5}")
print(f"W6 (механика): {W6}")
print(f"W7 (ЭДС/скорость): {W7}")
print(f"W8 (ДТ): {W8}")
print(f"W9 (ДС): {W9}")
print(f"\nПФ разомкнутой системы (без датчика в ОС):")
print(open_loop)
print(f"\nПФ замкнутой системы (с датчиком скорости в ОС):")
print(closed_loop)

# Проверка устойчивости
if all(np.real(p) < 0 for p in poles):
    print("\n✓ Система устойчива")
else:
    print("\n✗ Система неустойчива!")