import os
import librosa
import numpy as np
import pandas as pd

# Folder dataset
folder_dataset = "dataset"
audio_extensions = (".wav", ".mp3")

# List untuk simpan hasil
data = []

# Fungsi ekstraksi MFCC
def extract_mfcc(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    mean_mfcc = np.mean(mfcc)
    std_mfcc = np.std(mfcc)
    
    return mean_mfcc, std_mfcc


def infer_label(file_name):
    name = file_name.lower()
    if "asli" in name:
        return "Asli"
    if "clone" in name or "cloning" in name:
        return "Cloning"
    return "Unknown"

if not os.path.isdir(folder_dataset):
    raise FileNotFoundError(f"Folder dataset tidak ditemukan: {folder_dataset}")

for file in sorted(os.listdir(folder_dataset)):
    if not file.lower().endswith(audio_extensions):
        continue

    path = os.path.join(folder_dataset, file)
    if not os.path.isfile(path):
        continue

    mean, std = extract_mfcc(path)

    data.append({
        "Jenis Suara": infer_label(file),
        "Kode Audio": file,
        "Mean MFCC": round(mean, 2),
        "Std MFCC": round(std, 2)
    })

# ======================
# BUAT DATAFRAME
# ======================
df = pd.DataFrame(data)

if df.empty:
    raise RuntimeError("Tidak ada audio WAV/MP3 yang diproses dari folder dataset.")

# Urutkan biar rapi
df = df.sort_values(by=["Jenis Suara"])

# Tampilkan tabel
print("\n=== HASIL MFCC ===\n")
print(df)

# ======================
# HITUNG RATA-RATA PER KATEGORI
# ======================
summary = df.groupby("Jenis Suara").mean(numeric_only=True)

print("\n=== RATA-RATA PER KATEGORI ===\n")
print(summary)

# ======================
# SIMPAN KE FILE EXCEL
# ======================
df.to_excel("hasil_mfcc.xlsx", index=False)
summary.to_excel("summary_mfcc.xlsx")

print("\nFile berhasil disimpan:")
print("hasil_mfcc.xlsx")
print("summary_mfcc.xlsx")