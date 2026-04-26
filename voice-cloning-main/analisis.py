import os

import librosa
import numpy as np
import pandas as pd

# =========================================
# CONFIG PARAMETER MFCC
# =========================================
DATASET_FOLDER = "dataset"
OUTPUT_CSV = "hasil_mfcc.csv"
SUMMARY_CSV = "ringkasan_hasil_mfcc.csv"
AUDIO_EXTENSIONS = (".wav", ".mp3")

N_MFCC = 13  # Jumlah koefisien MFCC
SR = None    # Sample rate (None = detect otomatis)

# =========================================
# FUNGSI EKSTRAKSI MFCC MENGGUNAKAN LIBROSA
# =========================================
def extract_mfcc(audio_path, n_mfcc=N_MFCC):
    """
    Ekstraksi MFCC dari file audio menggunakan librosa.
    
    Parameters:
    -----------
    audio_path : str
        Path ke file audio (.wav atau .mp3)
    n_mfcc : int
        Jumlah koefisien MFCC (default: 13)
    
    Returns:
    --------
    mfcc_mean : np.ndarray
        Rata-rata setiap koefisien MFCC
    mfcc_std : np.ndarray
        Standar deviasi setiap koefisien MFCC
    num_frames : int
        Jumlah frame yang diproses
    sr : int
        Sample rate dari audio
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=SR)
        
        # Ekstraksi MFCC menggunakan librosa
        # Formula: MFCC = DCT(log(Mel-scale spectrogram))
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        
        # Statistik per koefisien
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        num_frames = mfcc.shape[1]
        
        return mfcc_mean, mfcc_std, num_frames, sr
        
    except Exception as e:
        print(f"ERROR pada {audio_path}: {str(e)}")
        return None, None, None, None


def infer_label(file_name):
    """Identifikasi label file berdasarkan naming convention."""
    name = file_name.lower()
    if "asli" in name:
        return "asli"
    if "clone" in name or "cloning" in name:
        return "cloning"
    return "unknown"


# =========================================
# PROSES SEMUA FILE AUDIO DI DATASET
# =========================================
results = []

if not os.path.isdir(DATASET_FOLDER):
    raise FileNotFoundError(f"Folder dataset tidak ditemukan: {DATASET_FOLDER}")

audio_files = sorted([f for f in os.listdir(DATASET_FOLDER) 
                     if f.lower().endswith(AUDIO_EXTENSIONS)])

if not audio_files:
    raise RuntimeError(f"Tidak ada file audio ditemukan di {DATASET_FOLDER}")

print(f"Menemukan {len(audio_files)} file audio. Memproses...\n")

for file in audio_files:
    path = os.path.join(DATASET_FOLDER, file)
    
    if not os.path.isfile(path):
        continue
    
    print(f"[▶] Memproses: {file}")
    
    mfcc_mean, mfcc_std, frame_count, sr = extract_mfcc(path)
    
    # Skip jika error
    if mfcc_mean is None:
        continue
    
    label = infer_label(file)
    
    row = {
        "file": file,
        "label": label,
        "sample_rate": sr,
        "frame_count": frame_count,
        "duration_sec": round(frame_count * 0.01, 3),  # ~10ms per frame
        "source_platform": "WhatsApp",
        "cloning_tool": "Minimax.AI" if label == "cloning" else "N/A",
    }
    
    # Tambah semua MFCC coefficients
    for i in range(len(mfcc_mean)):
        row[f"mean_{i+1}"] = round(float(mfcc_mean[i]), 6)
        row[f"std_{i+1}"] = round(float(mfcc_std[i]), 6)
    
    results.append(row)

print(f"\n✓ Berhasil memproses {len(results)} file audio\n")

if not results:
    raise RuntimeError("Tidak ada file audio WAV/MP3 yang berhasil diproses.")

# =========================================
# SIMPAN KE CSV
# =========================================
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

# Ringkasan statistik per kategori
summary = df.groupby("label")[
    [f"mean_{i}" for i in range(1, N_MFCC + 1)]
].mean()
summary.to_csv(SUMMARY_CSV)

print("=== HASIL EKSTRAKSI ===")
print(f"Total file       : {len(results)}")
print(f"Asli             : {sum(1 for r in results if r['label'] == 'asli')}")
print(f"Cloning          : {sum(1 for r in results if r['label'] == 'cloning')}")
unknown_count = sum(1 for r in results if r['label'] == 'unknown')
print(f"Unknown          : {unknown_count}")
print(f"\nFile hasil disimpan: {OUTPUT_CSV}")
print(f"File summary      : {SUMMARY_CSV}")
if unknown_count > 0:
    print(f"Peringatan: {unknown_count} file berlabel unknown. Periksa penamaan file.")