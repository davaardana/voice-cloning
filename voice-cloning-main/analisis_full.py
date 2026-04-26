import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import os

# =========================================
# KONFIGURASI
# =========================================
DATASET_FOLDER = "dataset"
OUTPUT_FOLDER = "hasil_full"
N_MFCC = 13
DPI = 300

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Cari file asli pertama untuk demonstrasi step-by-step
audio_files = [f for f in os.listdir(DATASET_FOLDER) 
               if f.lower().endswith(('.wav', '.mp3')) and 'asli' in f.lower()]

if not audio_files:
    raise FileNotFoundError(f"Tidak ada file 'asli' di {DATASET_FOLDER}")

audio_path = os.path.join(DATASET_FOLDER, audio_files[0])
print(f"File input: {audio_path}\n")

# =========================================
# 1. LOAD AUDIO
# =========================================
y, sr = librosa.load(audio_path, sr=None)
duration = len(y) / sr

print("=== INFORMASI AUDIO ===")
print(f"File               : {os.path.basename(audio_path)}")
print(f"Sampling rate      : {sr} Hz")
print(f"Jumlah sampel      : {len(y)}")
print(f"Durasi             : {duration:.2f} detik")

# =========================================
# 2. VISUALISASI WAVEFORM
# =========================================
print("\n[1/7] Membuat visualisasi Waveform...")
plt.figure(figsize=(12, 4))
librosa.display.waveshow(y, sr=sr, color='steelblue')
plt.title(f"Waveform Sinyal Asli - {os.path.basename(audio_path)}", fontsize=14, fontweight='bold')
plt.xlabel("Waktu (detik)", fontsize=11)
plt.ylabel("Amplitudo", fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "01_waveform_asli.png"), dpi=DPI)
plt.close()

# =========================================
# 3. POWER SPECTRUM
# =========================================
print("[2/7] Membuat Power Spectrum...")
X = np.abs(librosa.stft(y))
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
S_db = librosa.amplitude_to_db(S, ref=np.max)

plt.figure(figsize=(12, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='mel', cmap='viridis')
plt.colorbar(format='%+2.0f dB', label='Magnitude (dB)')
plt.title(f"Mel Spectrogram - {os.path.basename(audio_path)}", fontsize=14, fontweight='bold')
plt.xlabel("Waktu (detik)", fontsize=11)
plt.ylabel("Frekuensi (Mel)", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "02_mel_spectrogram.png"), dpi=DPI)
plt.close()

# =========================================
# 4. EKSTRAKSI MFCC MENGGUNAKAN LIBROSA
# =========================================
print("[3/7] Ekstraksi MFCC...")
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
mfcc_db = librosa.amplitude_to_db(np.abs(mfcc), ref=np.max)

print("\n=== HASIL EKSTRAKSI MFCC ===")
print(f"Shape MFCC         : {mfcc.shape}")
print(f"Jumlah frame       : {mfcc.shape[1]}")
print(f"Jumlah coefficient : {mfcc.shape[0]}")

# =========================================
# 5. VISUALISASI MFCC
# =========================================
print("[4/7] Membuat visualisasi MFCC Heatmap...")
plt.figure(figsize=(12, 6))
librosa.display.specshow(mfcc_db, sr=sr, x_axis='time', y_axis='mel', cmap='coolwarm')
plt.colorbar(format='%+2.0f dB', label='Magnitude (dB)')
plt.title(f"MFCC Heatmap - {os.path.basename(audio_path)}", fontsize=14, fontweight='bold')
plt.xlabel("Waktu (detik)", fontsize=11)
plt.ylabel("Koefisien MFCC", fontsize=11)
plt.yticks(range(N_MFCC), [f'MFCC-{i+1}' for i in range(N_MFCC)])
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "03_mfcc_heatmap.png"), dpi=DPI)
plt.close()

# =========================================
# 6. STATISTIK MFCC (Mean & Std)
# =========================================
print("[5/7] Menghitung statistik MFCC...")
mfcc_mean = np.mean(mfcc, axis=1)
mfcc_std = np.std(mfcc, axis=1)

print("\n=== STATISTIK KOEFISIEN MFCC ===")
print(f"{'MFCC':>8} | {'Mean':>10} | {'Std':>10}")
print("-" * 32)
for i in range(N_MFCC):
    print(f"MFCC-{i+1:>2} | {mfcc_mean[i]:>10.4f} | {mfcc_std[i]:>10.4f}")

# Visualisasi Mean MFCC
plt.figure(figsize=(12, 5))
plt.bar(range(1, N_MFCC + 1), mfcc_mean, color='steelblue', alpha=0.8, edgecolor='black')
plt.errorbar(range(1, N_MFCC + 1), mfcc_mean, yerr=mfcc_std, 
             fmt='none', ecolor='red', capsize=5, alpha=0.7, label='Std Dev')
plt.title(f"Mean dan Standar Deviasi Koefisien MFCC - {os.path.basename(audio_path)}", 
          fontsize=14, fontweight='bold')
plt.xlabel("Koefisien MFCC", fontsize=11)
plt.ylabel("Nilai", fontsize=11)
plt.xticks(range(1, N_MFCC + 1))
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "04_mean_std_mfcc.png"), dpi=DPI)
plt.close()

# =========================================
# 7. TEMPORAL VARIASI MFCC
# =========================================
print("[6/7] Membuat grafik variasi temporal...")
mfcc_var = np.var(mfcc, axis=0)

plt.figure(figsize=(12, 5))
plt.plot(mfcc_var, color='darkgreen', linewidth=2, label='Variasi antar Frame')
plt.fill_between(range(len(mfcc_var)), mfcc_var, alpha=0.3, color='lightgreen')
plt.title(f"Variasi MFCC antar Frame (Temporal) - {os.path.basename(audio_path)}", 
          fontsize=14, fontweight='bold')
plt.xlabel("Frame Index", fontsize=11)
plt.ylabel("Varians", fontsize=11)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "05_temporal_variation.png"), dpi=DPI)
plt.close()

# =========================================
# 8. SUMMARY STATISTICS TABLE
# =========================================
print("[7/7] Menyimpan summary statistik...")

summary_data = {
    'Koefisien': [f'MFCC-{i+1}' for i in range(N_MFCC)],
    'Mean': mfcc_mean.round(4),
    'Std Dev': mfcc_std.round(4),
    'Min': np.min(mfcc, axis=1).round(4),
    'Max': np.max(mfcc, axis=1).round(4),
    'Median': np.median(mfcc, axis=1).round(4),
}

import pandas as pd
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(os.path.join(OUTPUT_FOLDER, "mfcc_statistics.csv"), index=False)

print("\n" + "="*60)
print("✓ SEMUA VISUALISASI BERHASIL DIBUAT!")
print("="*60)
print(f"\nFile hasil tersimpan di folder: {OUTPUT_FOLDER}")
print("Daftar file yang dihasilkan:")
for i, f in enumerate(sorted(os.listdir(OUTPUT_FOLDER)), 1):
    print(f"  {i}. {f}")
print("\n=== SELESAI ===")
print("Tahapan MFCC berhasil diproses dari audio sampai hasil akhir.")
print(f"Semua visualisasi disimpan di folder: {OUTPUT_FOLDER}")