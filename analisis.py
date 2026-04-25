import os

import librosa
import numpy as np
import pandas as pd
from scipy.fftpack import dct

# =========================================
# CONFIG
# =========================================
DATASET_FOLDER = "dataset"
OUTPUT_CSV = "hasil_mfcc.csv"
SUMMARY_CSV = "ringkasan_hasil_mfcc.csv"
AUDIO_EXTENSIONS = (".wav", ".mp3")

# =========================================
# FUNGSI MFCC
# =========================================
def extract_mfcc(audio_path):
    signal, sr = librosa.load(audio_path, sr=None)

    # Pre-emphasis
    alpha = 0.97
    signal = np.append(signal[0], signal[1:] - alpha * signal[:-1])

    # Frame Blocking
    frame_size = 0.025
    frame_stride = 0.01

    frame_length = int(round(frame_size * sr))
    frame_step = int(round(frame_stride * sr))

    signal_length = len(signal)
    num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step)) + 1

    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - signal_length))
    pad_signal = np.append(signal, z)

    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T

    frames = pad_signal[indices.astype(np.int32, copy=False)]

    # Windowing
    frames *= np.hamming(frame_length)

    # FFT
    NFFT = 512
    mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))

    # Mel Filter Bank
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

    # DCT → MFCC
    num_ceps = 13
    mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, 1:(num_ceps + 1)]

    # Statistik
    mfcc_mean = np.mean(mfcc, axis=0)
    mfcc_std = np.std(mfcc, axis=0)

    return mfcc_mean, mfcc_std, mfcc.shape[0], sr


def infer_label(file_name):
    name = file_name.lower()
    if "asli" in name:
        return "asli"
    if "clone" in name or "cloning" in name:
        return "cloning"
    return "unknown"


# =========================================
# PROSES SEMUA FILE
# =========================================
results = []

if not os.path.isdir(DATASET_FOLDER):
    raise FileNotFoundError(f"Folder dataset tidak ditemukan: {DATASET_FOLDER}")

for file in sorted(os.listdir(DATASET_FOLDER)):
    if not file.lower().endswith(AUDIO_EXTENSIONS):
        continue

    path = os.path.join(DATASET_FOLDER, file)
    if not os.path.isfile(path):
        continue

    print(f"Processing: {file}")

    mfcc_mean, mfcc_std, frame_count, sr = extract_mfcc(path)
    label = infer_label(file)

    row = {
        "file": file,
        "label": label,
        "sample_rate": sr,
        "frame_count": frame_count,
        "source_platform": "whatsapp",
        "cloning_tool": "minimax.ai" if label == "cloning" else "n/a",
    }

    for i in range(len(mfcc_mean)):
        row[f"mean_{i+1}"] = mfcc_mean[i]
        row[f"std_{i+1}"] = mfcc_std[i]

    results.append(row)

if not results:
    raise RuntimeError("Tidak ada file audio WAV/MP3 yang berhasil diproses.")

# =========================================
# SIMPAN KE CSV
# =========================================
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

summary = df.groupby("label").mean(numeric_only=True)
summary.to_csv(SUMMARY_CSV)

unknown_count = int((df["label"] == "unknown").sum())

print("\n=== SELESAI ===")
print(f"Hasil disimpan di {OUTPUT_CSV}")
print(f"Ringkasan disimpan di {SUMMARY_CSV}")
if unknown_count:
    print(f"Peringatan: {unknown_count} file berlabel unknown. Periksa penamaan file.")