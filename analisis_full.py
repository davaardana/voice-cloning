import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import os
from scipy.fftpack import dct

# =========================================
# 1. LOAD AUDIO
# =========================================
audio_path = "asli2.wav"
output_folder = "hasil_full"
os.makedirs(output_folder, exist_ok=True)

if not os.path.isfile(audio_path):
    raise FileNotFoundError(f"File audio tidak ditemukan: {audio_path}")

signal, sr = librosa.load(audio_path, sr=None)
duration = len(signal) / sr

print("=== INFORMASI AUDIO ===")
print(f"Sampling rate : {sr} Hz")
print(f"Jumlah sampel : {len(signal)}")
print(f"Durasi        : {duration:.2f} detik")

# =========================================
# 2. PRE-EMPHASIS
# y[n] = x[n] - alpha * x[n-1]
# =========================================
alpha = 0.97
pre_emphasis_signal = np.append(signal[0], signal[1:] - alpha * signal[:-1])

print("\n=== PRE-EMPHASIS ===")
print(f"Panjang sinyal setelah pre-emphasis: {len(pre_emphasis_signal)}")

# =========================================
# 3. FRAME BLOCKING
# =========================================
frame_size = 0.025   # 25 ms
frame_stride = 0.01  # 10 ms

frame_length = int(round(frame_size * sr))
frame_step = int(round(frame_stride * sr))

signal_length = len(pre_emphasis_signal)
num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step)) + 1

pad_signal_length = num_frames * frame_step + frame_length
z = np.zeros((pad_signal_length - signal_length))
pad_signal = np.append(pre_emphasis_signal, z)

indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
          np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T

frames = pad_signal[indices.astype(np.int32, copy=False)]

print("\n=== FRAME BLOCKING ===")
print(f"Panjang frame : {frame_length} sampel")
print(f"Step frame    : {frame_step} sampel")
print(f"Jumlah frame  : {num_frames}")

# =========================================
# 4. WINDOWING (HAMMING WINDOW)
# =========================================
frames *= np.hamming(frame_length)

print("\n=== WINDOWING ===")
print("Windowing menggunakan Hamming window selesai.")

# =========================================
# 5. FFT DAN POWER SPECTRUM
# =========================================
NFFT = 512
mag_frames = np.absolute(np.fft.rfft(frames, NFFT))      # magnitudo FFT
pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))          # power spectrum

print("\n=== FFT ===")
print(f"Bentuk magnitude spectrum : {mag_frames.shape}")
print(f"Bentuk power spectrum     : {pow_frames.shape}")

# =========================================
# 6. MEL FILTER BANK
# =========================================
nfilt = 26

low_freq_mel = 0
high_freq_mel = 2595 * np.log10(1 + (sr / 2) / 700)

mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
hz_points = 700 * (10**(mel_points / 2595) - 1)
bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)

fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))

for m in range(1, nfilt + 1):
    f_m_minus = bin_points[m - 1]
    f_m = bin_points[m]
    f_m_plus = bin_points[m + 1]

    for k in range(f_m_minus, f_m):
        fbank[m - 1, k] = (k - bin_points[m - 1]) / (bin_points[m] - bin_points[m - 1] + 1e-8)
    for k in range(f_m, f_m_plus):
        fbank[m - 1, k] = (bin_points[m + 1] - k) / (bin_points[m + 1] - bin_points[m] + 1e-8)

filter_banks = np.dot(pow_frames, fbank.T)
filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
filter_banks = 20 * np.log10(filter_banks)

print("\n=== MEL FILTER BANK ===")
print(f"Bentuk filter bank output : {filter_banks.shape}")

# =========================================
# 7. DCT -> MFCC
# =========================================
num_ceps = 13
mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, 1:(num_ceps + 1)]

print("\n=== DCT / MFCC ===")
print(f"Bentuk matriks MFCC : {mfcc.shape}")
print("Artinya:")
print(f"- {mfcc.shape[0]} frame")
print(f"- {mfcc.shape[1]} koefisien MFCC")

# =========================================
# 8. HITUNG MEAN DAN STANDAR DEVIASI
# =========================================
mfcc_mean = np.mean(mfcc, axis=0)
mfcc_std = np.std(mfcc, axis=0)

print("\n=== STATISTIK MFCC ===")
for i, (mean, std) in enumerate(zip(mfcc_mean, mfcc_std), start=1):
    print(f"MFCC-{i:02d} | Mean = {mean:8.3f} | Std = {std:8.3f}")

# =========================================
# 9. VISUALISASI
# =========================================

# Waveform asli
plt.figure(figsize=(10, 4))
librosa.display.waveshow(signal, sr=sr)
plt.title("Waveform Sinyal Asli")
plt.xlabel("Waktu (detik)")
plt.ylabel("Amplitudo")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "01_waveform_asli.png"), dpi=300)
plt.close()

# Waveform hasil pre-emphasis
plt.figure(figsize=(10, 4))
plt.plot(pre_emphasis_signal)
plt.title("Sinyal Setelah Pre-Emphasis")
plt.xlabel("Sampel")
plt.ylabel("Amplitudo")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "02_preemphasis.png"), dpi=300)
plt.close()

# Power spectrum frame pertama
plt.figure(figsize=(10, 4))
plt.plot(pow_frames[0])
plt.title("Power Spectrum (Frame Pertama)")
plt.xlabel("Frekuensi Bin")
plt.ylabel("Energi")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "03_power_spectrum_frame_1.png"), dpi=300)
plt.close()

# Mel filter bank
plt.figure(figsize=(10, 4))
for i in range(nfilt):
    plt.plot(fbank[i])
plt.title("Mel Filter Bank")
plt.xlabel("Frekuensi Bin")
plt.ylabel("Amplitudo")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "04_mel_filter_bank.png"), dpi=300)
plt.close()

# Heatmap MFCC
plt.figure(figsize=(10, 5))
plt.imshow(mfcc.T, aspect='auto', origin='lower')
plt.title("Heatmap MFCC")
plt.xlabel("Frame")
plt.ylabel("Koefisien MFCC")
plt.colorbar()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "05_heatmap_mfcc.png"), dpi=300)
plt.close()

# Grafik mean MFCC
plt.figure(figsize=(10, 4))
plt.plot(range(1, num_ceps + 1), mfcc_mean, marker='o')
plt.title("Mean Koefisien MFCC")
plt.xlabel("Koefisien MFCC")
plt.ylabel("Nilai Mean")
plt.xticks(range(1, num_ceps + 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "06_mean_mfcc.png"), dpi=300)
plt.close()

# Grafik standar deviasi MFCC
plt.figure(figsize=(10, 4))
plt.plot(range(1, num_ceps + 1), mfcc_std, marker='s')
plt.title("Standar Deviasi Koefisien MFCC")
plt.xlabel("Koefisien MFCC")
plt.ylabel("Nilai Std")
plt.xticks(range(1, num_ceps + 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "07_std_mfcc.png"), dpi=300)
plt.close()

print("\n=== SELESAI ===")
print("Tahapan MFCC berhasil diproses dari audio sampai hasil akhir.")
print(f"Semua visualisasi disimpan di folder: {output_folder}")