import wave
import numpy as np
import matplotlib.pyplot as plt

# 1. Leer archivo de voz (sb002.wav)
with wave.open("pitch_db/train/sb002.wav", "rb") as wf:
    fs = wf.getframerate()
    n_frames = wf.getnframes()
    raw_data = wf.readframes(n_frames)
    x = np.frombuffer(raw_data, dtype=np.int16).astype(float) / 32768.0

# 2. Buscar automáticamente una trama de 30 ms con alta energía (claramente sonora)
N = int(0.030 * fs)
shift = int(0.015 * fs)
energies = [np.sum(x[i : i + N]**2) for i in range(0, len(x) - N, shift)]
best_frame_idx = int(np.argmax(energies))
n_start = best_frame_idx * shift
t_start = n_start / fs

frame = x[n_start : n_start + N]
t_ms = np.arange(N) * 1000.0 / fs

# 3. Calcular autocorrelación sesgada r[l] hasta f0_min = 50 Hz
lag_min = int(fs / 500.0)
lag_max = int(fs / 50.0)
r = np.zeros(lag_max)
for l in range(lag_max):
    r[l] = np.sum(frame[:N - l] * frame[l:]) / N

# 4. Localizar el primer máximo secundario fuera del lóbulo principal
peak_lag = lag_min + int(np.argmax(r[lag_min:lag_max]))
T0_ms = peak_lag * 1000.0 / fs
f0_hz = fs / peak_lag

# 5. Graficar los dos subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.2))
plt.subplots_adjust(hspace=0.45)

# Subplot 1: Señal temporal (30 ms) y periodo de pitch T0
ax1.plot(t_ms, frame, color="#1f77b4", lw=1.5, label="Señal temporal $x[n]$")
# Buscamos el primer gran pico positivo para marcar T0 con claridad
p1_idx = int(np.argmax(frame[:peak_lag]))
p2_idx = p1_idx + np.argmax(frame[p1_idx + int(0.8*peak_lag) : p1_idx + int(1.2*peak_lag)]) + int(0.8*peak_lag)
p1_t = t_ms[p1_idx]
p2_t = p1_t + T0_ms

y_top = max(frame) * 1.18
ax1.set_ylim(min(frame) * 1.15, y_top * 1.08)
ax1.axvline(p1_t, color="crimson", linestyle="--", lw=1.2)
ax1.axvline(p2_t, color="crimson", linestyle="--", lw=1.2)
ax1.annotate("", xy=(p2_t, max(frame)*0.95), xytext=(p1_t, max(frame)*0.95),
             arrowprops=dict(arrowstyle="<->", color="crimson", lw=1.5))
ax1.text((p1_t + p2_t)/2, max(frame)*1.03, f"$T_0 = {T0_ms:.2f}$ ms ($f_0 = {f0_hz:.1f}$ Hz)",
         color="crimson", ha="center", fontweight="bold")
ax1.set_title(f"Segmento temporal de 30 ms de un fonema sonoro (sb002.wav, t = {t_start:.2f} s)")
ax1.set_xlabel("Tiempo [ms]")
ax1.set_ylabel("Amplitud")
ax1.grid(True, alpha=0.3)
ax1.legend(loc="lower right")

# Subplot 2: Autocorrelación y primer máximo secundario
lags = np.arange(lag_max)
ax2.plot(lags, r, color="#2ca02c", lw=1.5, label="Autocorrelación $r[l]$")
ax2.plot(peak_lag, r[peak_lag], "ro", markersize=7,
         label=f"1er máximo secundario: lag = {peak_lag} muestras ({T0_ms:.2f} ms)")
ax2.axvline(peak_lag, color="crimson", linestyle=":", lw=1.2)
ax2.axhline(0, color="black", lw=0.8, alpha=0.5)
ax2.set_title("Autocorrelación sesgada $r[l]$ y detección del primer máximo secundario")
ax2.set_xlabel("Retardo (lag $l$) [muestras]")
ax2.set_ylabel("$r[l]$")
ax2.grid(True, alpha=0.3)
ax2.legend(loc="upper right")

plt.savefig("img/autocorrelacion_pitch.png", dpi=150, bbox_inches="tight")
print(f"OK -> t_start = {t_start:.2f} s | lag = {peak_lag} muestras | T0 = {T0_ms:.2f} ms | f0 = {f0_hz:.2f} Hz")