import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

def format_poly(coeffs, var='s'):
    terms = []
    n = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        power = n - i
        if abs(c) < 1e-12:
            continue
        if power == 0:
            terms.append(f"{c:.2g}")
        elif power == 1:
            terms.append(f"{c:.2g}{var}")
        else:
            terms.append(f"{c:.2g}{var}^{power}")
    if not terms:
        return "0"
    return " + ".join(terms).replace("+ -", "- ")

def make_proper(num, den, tau=0.001):
    if len(num) <= len(den):
        return num, den
    den_new = np.convolve(den, [tau, 1])
    return num, den_new

def format_complex_array(arr, threshold=1e-12):
    """Форматирует массив комплексных чисел в строку вида 'a + bj' или 'a'."""
    if len(arr) == 0:
        return "нет"
    parts = []
    for val in arr:
        if abs(val) < threshold:
            parts.append("0")
        elif abs(val.imag) < threshold:
            parts.append(f"{val.real:.4f}")
        else:
            # Форматируем комплексное число
            real = val.real
            imag = val.imag
            if abs(real) < threshold:
                parts.append(f"{imag:.4f}j")
            else:
                sign = "+" if imag >= 0 else "-"
                parts.append(f"{real:.4f} {sign} {abs(imag):.4f}j")
    return ", ".join(parts)

def analyze_system(num, den, title, is_inertial=True, tau=0.001, w_extended=False, ideal_diff=False):
    num_prop, den_prop = make_proper(num, den, tau)
    if (num_prop is not num) or (den_prop is not den):
        print(f"   (Используется аппроксимация с tau={tau:.0e})")

    sys1 = signal.TransferFunction(num_prop, den_prop)
    num2 = [2 * c for c in num_prop]
    sys2 = signal.TransferFunction(num2, den_prop)

    sys_orig = signal.TransferFunction(num, den)
    zeros = sys_orig.zeros
    poles = sys_orig.poles

    # Форматированный вывод
    print("=" * 60)
    print(title)
    print("-" * 60)
    print(f"Передаточная функция: W(s) = ({format_poly(num)}) / ({format_poly(den)})")
    print(f"Операторное уравнение: ({format_poly(den)}) y(t) = ({format_poly(num)}) x(t)")
    print(f"Нули: {format_complex_array(zeros)}")
    print(f"Полюса: {format_complex_array(poles)}")

    if len(poles) > 0 and np.any(np.real(poles) > 0):
        stability = "неустойчивое"
    else:
        stability = "устойчивое"
    print(f"Характер переходного процесса: {stability}", end="")
    if np.iscomplexobj(poles) and np.any(np.imag(poles) != 0):
        print(" (колебательный)")
    else:
        print()
    if len(zeros) > 0:
        print("   - наличие нулей может ускорять реакцию и влиять на выбросы")

    if is_inertial:
        corner_freqs = []
        for p in poles:
            if abs(p) > 1e-6:
                corner_freqs.append(abs(p))
        for z in zeros:
            if abs(z) > 1e-6:
                corner_freqs.append(abs(z))
        corner_freqs = sorted(set(corner_freqs))
        if corner_freqs:
            cf_str = ", ".join([f"{cf:.4f}" for cf in corner_freqs])
            print(f"Частоты сопряжения (рад/с): {cf_str}")
        else:
            print("Частоты сопряжения не выражены")

        # Поиск частоты среза
        def mag_db(w):
            _, H = signal.freqresp(sys1, w=[w])
            return 20 * np.log10(abs(H[0]))
        try:
            w_log = np.logspace(-2, 3, 1000)
            mags = [mag_db(w) for w in w_log]
            idx = np.where(np.diff(np.sign(mags)))[0]
            if len(idx) > 0:
                w_c_est = w_log[idx[0]]
                w_c = fsolve(lambda w: mag_db(w), w_c_est)[0]
                print(f"Частота среза (рад/с): {w_c:.4f}")
            else:
                print("Частота среза не определена (ЛАЧХ не пересекает 0 дБ)")
        except:
            print("Ошибка при определении частоты среза")

    # --- Построение графиков (без изменений) ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title)

    t = np.linspace(0, 10, 1000)
    t1, y1 = signal.step(sys1, T=t)
    t2, y2 = signal.step(sys2, T=t)
    axes[0,0].plot(t1, y1, 'b-', label='k=1')
    axes[0,0].plot(t2, y2, 'r--', label='k=2')
    axes[0,0].set_title('Переходная характеристика')
    axes[0,0].set_xlabel('Время (с)')
    axes[0,0].set_ylabel('y(t)')
    axes[0,0].grid(True)
    axes[0,0].legend()

    if w_extended:
        w = np.logspace(-2, 5, 1000)   # до 10^5 рад/с
    else:
        w = np.logspace(-2, 2, 1000)   # до 100 рад/с

    w_bode, mag, phase = signal.bode(sys1, w)
    axes[0,1].semilogx(w_bode, mag, 'b-')
    axes[0,1].set_title('ЛАЧХ')
    axes[0,1].set_xlabel('Частота (рад/с)')
    axes[0,1].set_ylabel('Модуль (дБ)')
    axes[0,1].grid(True)
    if is_inertial and 'corner_freqs' in locals():
        for cf in corner_freqs:
            axes[0,1].axvline(cf, color='gray', linestyle=':', alpha=0.7)
    if 'w_c' in locals():
        axes[0,1].axvline(w_c, color='r', linestyle='--', label=f'срез = {w_c:.2f}')
        axes[0,1].legend()

    axes[1,1].semilogx(w_bode, phase, 'b-')
    axes[1,1].set_title('ФЧХ')
    axes[1,1].set_xlabel('Частота (рад/с)')
    axes[1,1].set_ylabel('Фаза (град)')
    axes[1,1].grid(True)

    # АФХ
    if ideal_diff:
        re_theor = np.zeros_like(w)
        im_theor = w
        axes[1,0].plot(re_theor, im_theor, 'b-', label='АФХ (теоретическая)')
        axes[1,0].plot(0, 0, 'go', label='ω→0')
        axes[1,0].plot(0, w[-1], 'ro', label='ω→∞')
    else:
        _, H = signal.freqresp(sys1, w)
        axes[1,0].plot(H.real, H.imag, 'b-', label='АФХ')
        axes[1,0].plot(H.real[0], H.imag[0], 'go', label='ω→0')
        axes[1,0].plot(H.real[-1], H.imag[-1], 'ro', label='ω→∞')
    axes[1,0].set_title('АФХ (Найквист)')
    axes[1,0].set_xlabel('Re')
    axes[1,0].set_ylabel('Im')
    axes[1,0].grid(True)
    axes[1,0].legend()
    axes[1,0].axis('equal')

    plt.tight_layout()
    plt.show()
    print("=" * 60)

# ------------------------------------------------------------
# Звено 1
analyze_system([1], [1], "1. Безынерционное (пропорциональное)", is_inertial=False)

# Звено 2
analyze_system([1], [1, 1], "2. Инерционное 1-го порядка (апериодическое)", is_inertial=True)

# Звено 3
analyze_system([1], [0.25, 1, 1], "3. Инерционное 2-го порядка (апериодическое)", is_inertial=True)

# Звено 4
analyze_system([1], [1, 0.5, 1], "4. Инерционное 2-го порядка (колебательное)", is_inertial=True)

# Звено 5
analyze_system([1], [1, 0], "5. Идеальное интегрирующее", is_inertial=False)

# Звено 6
analyze_system([1], [1, 1, 0], "6. Реальное интегрирующее", is_inertial=True)

# Звено 7 (идеальное дифференцирующее) – используем очень малый tau и расширенный диапазон, но АФХ строим теоретическую
analyze_system([1, 0], [1], "7. Идеальное дифференцирующее", is_inertial=False,
               tau=1e-6, w_extended=True, ideal_diff=True)

# Звено 8
analyze_system([1, 0], [1, 1], "8. Реальное дифференцирующее", is_inertial=True)