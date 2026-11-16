import wave
import numpy as np
import matplotlib.pyplot as plt

# 1. Leer señal de prueba (sb002.wav) y su referencia real (sb002.f0ref) y estimación (sb002.f0)
wav_path = "pitch_db/train/sb002.wav"
f0ref_path = "pitch_db/train/sb002.f0ref"
f0est_path = "pitch_db/train/sb002.f0"

with wave.open(wav_path, "rb") as wf:
    fs = wf.getframerate()
    n_frames = wf.getnframes()
    x = np.frombuffer(wf.readframes(n_frames), dtype=np.int16).astype(float) / 32768.0

f0ref = np.loadtxt(f0ref_path)
f0est = np.loadtxt(f0est_path)

# Parámetros de enventanado de la práctica (30 ms longitud, 15 ms desplazamiento)
n_len = int(0.030 * fs)
n_shift = int(0.015 * fs)
lag_min = int(fs / 500.0)
lag_max = 1 + int(fs / 50.0)

pot_list = []
r1norm_list = []
rmaxnorm_list = []
zcr_list = []
f0_ws_list = [0.0]  # t = 0

# 2. Calcular candidatos trama a trama (cada 15 ms) igual que en pitch_analyzer.cpp
for i in range(0, len(x) - n_len, n_shift):
    frame = x[i : i + n_len]
    
    # Autocorrelación sesgada
    r = np.zeros(lag_max)
    for l in range(lag_max):
        r[l] = np.sum(frame[:n_len - l] * frame[l:]) / n_len
    if r[0] == 0.0:
        r[0] = 1e-10
        
    lag = lag_min + int(np.argmax(r[lag_min:lag_max]))
    
    pot = 10.0 * np.log10(r[0])
    r1norm = r[1] / r[0]
    rmaxnorm = r[lag] / r[0]
    # Tasa de cruces por cero (ZCR normalizada)
    zcr = np.mean(np.abs(np.diff(np.sign(frame))) > 0)
    
    pot_list.append(pot)
    r1norm_list.append(r1norm)
    rmaxnorm_list.append(rmaxnorm)
    zcr_list.append(zcr)
    
    # Estimación estilo Wavesurfer (ESPS/RAPT correlator con ventana Hanning/Cos4 y post-suavizado)
    win_frame = frame * np.hanning(n_len)
    r_ws = np.zeros(lag_max)
    for l in range(lag_max):
        r_ws[l] = np.sum(win_frame[:n_len - l] * win_frame[l:]) / n_len
    lag_ws = lag_min + int(np.argmax(r_ws[lag_min:lag_max]))
    if (pot > -46.0) and (r_ws[lag_ws] / (r_ws[0] + 1e-10) > 0.32) and (r1norm > 0.82):
        f0_ws_list.append(fs / lag_ws)
    else:
        f0_ws_list.append(0.0)

f0_ws_list.append(0.0)  # t = Dur
f0_ws = np.array(f0_ws_list[:len(f0ref)])

# Ejes de tiempo sincronizados con desplazamiento de ventana de 15 ms
t_sig = np.arange(len(x)) / fs
t_frames = (np.arange(len(pot_list)) + 1) * 0.015
t_f0 = np.arange(len(f0ref)) * 0.015

# ==============================================================================
# GRÁFICA 1: Señal, Pitch y candidatos de sonoridad (pot, r1norm, rmaxnorm, ZCR)
# ==============================================================================
fig, axes = plt.subplots(6, 1, figsize=(10, 10), sharex=True)
plt.subplots_adjust(hspace=0.35)

# Panel 1: Señal temporal
axes[0].plot(t_sig, x, color="#1f77b4", lw=0.8)
axes[0].set_ylabel("Amplitud")
axes[0].set_title("Análisis de candidatos de sonoridad con desplazamiento de 15 ms (sb002.wav)")
axes[0].grid(True, alpha=0.3)

# Panel 2: Contorno de Pitch F0
axes[1].plot(t_f0, f0ref, "k--", lw=1.2, label="$f_0$ Referencia (.f0ref)")
axes[1].plot(t_f0[:len(f0est)], f0est, "r.", markersize=5, label="$f_0$ Estimado")
axes[1].set_ylabel("$f_0$ [Hz]")
axes[1].legend(loc="upper right", fontsize=8)
axes[1].grid(True, alpha=0.3)

# Panel 3: Nivel de potencia 10*log10(r[0])
axes[2].plot(t_frames, pot_list, color="#ff7f0e", lw=1.5, label="Potencia $10\\log_{10}(r[0])$")
axes[2].axhline(-45.0, color="crimson", linestyle="--", lw=1.0, label="Umbral = -45 dB")
axes[2].set_ylabel("Potencia [dB]")
axes[2].legend(loc="lower right", fontsize=8)
axes[2].grid(True, alpha=0.3)

# Panel 4: r1norm = r[1]/r[0]
axes[3].plot(t_frames, r1norm_list, color="#2ca02c", lw=1.5, label="$r_{1,\\mathrm{norm}} = r[1]/r[0]$")
axes[3].axhline(0.85, color="crimson", linestyle="--", lw=1.0, label="Umbral = 0.85")
axes[3].set_ylabel("$r[1]/r[0]$")
axes[3].set_ylim(-0.5, 1.05)
axes[3].legend(loc="lower right", fontsize=8)
axes[3].grid(True, alpha=0.3)

# Panel 5: rmaxnorm = r[lag]/r[0]
axes[4].plot(t_frames, rmaxnorm_list, color="#9467bd", lw=1.5, label="$r_{\\max,\\mathrm{norm}} = r[\\mathrm{lag}]/r[0]$")
axes[4].axhline(0.38, color="crimson", linestyle="--", lw=1.0, label="Umbral = 0.38")
axes[4].set_ylabel("$r[\\mathrm{lag}]/r[0]$")
axes[4].set_ylim(0.0, 1.0)
axes[4].legend(loc="upper right", fontsize=8)
axes[4].grid(True, alpha=0.3)

# Panel 6: Tasa de cruces por cero (ZCR)
axes[5].plot(t_frames, zcr_list, color="#8c564b", lw=1.5, label="Tasa de cruces por cero (ZCR)")
axes[5].set_ylabel("ZCR")
axes[5].set_xlabel("Tiempo [s] (desplazamiento de trama = 15 ms)")
axes[5].legend(loc="upper right", fontsize=8)
axes[5].grid(True, alpha=0.3)

plt.savefig("img/candidatos_sonoridad.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ==============================================================================
# GRÁFICA 2: Comparativa entre Referencia, Wavesurfer y nuestro get_pitch
# ==============================================================================
fig2, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(9.5, 6), sharex=True,
                                       gridspec_kw={'height_ratios': [1, 2]})
plt.subplots_adjust(hspace=0.25)

ax_top.plot(t_sig, x, color="#1f77b4", lw=0.8)
ax_top.set_ylabel("Amplitud")
ax_top.set_title("Comparativa de estimación de Pitch (desplazamiento = 15 ms) en sb002.wav")
ax_top.grid(True, alpha=0.3)

ax_bot.plot(t_f0, f0ref, "k-", lw=2.0, alpha=0.6, label="Referencia real ($f_0$ ref)")
ax_bot.plot(t_f0, f0_ws, "bs", markersize=4, alpha=0.75, label="Estimador Wavesurfer (frame interval = 15 ms)")
ax_bot.plot(t_f0[:len(f0est)], f0est, "ro", markersize=4, alpha=0.85, label="Nuestro estimador (get_pitch)")
ax_bot.set_xlabel("Tiempo [s]")
ax_bot.set_ylabel("Frecuencia fundamental $f_0$ [Hz]")
ax_bot.set_ylim(-10, 320)
ax_bot.legend(loc="upper right")
ax_bot.grid(True, alpha=0.3)

plt.savefig("img/comparativa_wavesurfer_getpitch.png", dpi=150, bbox_inches="tight")
plt.close(fig2)

print("OK -> Gráficas guardadas en img/candidatos_sonoridad.png e img/comparativa_wavesurfer_getpitch.png")