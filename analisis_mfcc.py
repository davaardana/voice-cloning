import os
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib.pyplot as plt

# =========================
# KONFIGURASI FILE AUDIO
# =========================
PAIRS = [
    ("asli1.wav", "clone1.wav"),
    ("asli2.wav", "clone2.wav"),
    ("asli3.wav", "clone3.wav"),
    ("asli4.wav", "clone4.wav"),
]
SOURCE_PLATFORM = "WhatsApp Voice Note"
CLONING_TOOL = "Minimax.AI"

# Folder output
output_folder = "hasil"
os.makedirs(output_folder, exist_ok=True)

# =========================
# FUNGSI LOAD AUDIO
# =========================
def load_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    duration = len(y) / sr
    return y, sr, duration

# =========================
# FUNGSI EKSTRAKSI MFCC
# =========================
def extract_mfcc(y, sr, n_mfcc=13):
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    frame_var = np.var(mfcc, axis=0)
    return mfcc, mfcc_mean, mfcc_std, frame_var

# =========================
# FUNGSI WAVEFORM
# =========================
def plot_waveform(y, sr, title, save_path):
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.xlabel("Waktu (detik)")
    plt.ylabel("Amplitudo")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

# =========================
# FUNGSI SPECTROGRAM
# =========================
def plot_spectrogram(y, sr, title, save_path):
    X = librosa.stft(y)
    X_db = librosa.amplitude_to_db(np.abs(X), ref=np.max)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(X_db, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title(title)
    plt.xlabel("Waktu (detik)")
    plt.ylabel("Frekuensi (Hz)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

# =========================
# FUNGSI VISUALISASI MFCC
# =========================
def plot_mfcc(mfcc, sr, title, save_path):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mfcc, x_axis='time', sr=sr)
    plt.colorbar()
    plt.title(title)
    plt.xlabel("Waktu")
    plt.ylabel("Koefisien MFCC")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_distribution(mean_asli, mean_clone, title, save_path):
    plt.figure(figsize=(10, 5))
    plt.hist(mean_asli, bins=8, alpha=0.55, label="Mean Asli")
    plt.hist(mean_clone, bins=8, alpha=0.55, label="Mean Clone")
    plt.title(title)
    plt.xlabel("Nilai Mean Koefisien MFCC")
    plt.ylabel("Frekuensi")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_frame_variation(frame_var_asli, frame_var_clone, title, save_path):
    n = min(len(frame_var_asli), len(frame_var_clone), 250)
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, n + 1), frame_var_asli[:n], label="Variasi Frame Asli")
    plt.plot(range(1, n + 1), frame_var_clone[:n], label="Variasi Frame Clone")
    plt.title(title)
    plt.xlabel("Frame")
    plt.ylabel("Variasi MFCC antar Frame")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def analyze_pair(file_asli, file_clone):
    if not os.path.isfile(file_asli) or not os.path.isfile(file_clone):
        print(f"Lewati pasangan karena file tidak ditemukan: {file_asli}, {file_clone}")
        return None

    y_asli, sr_asli, dur_asli = load_audio(file_asli)
    y_clone, sr_clone, dur_clone = load_audio(file_clone)

    mfcc_asli, mean_asli, std_asli, frame_var_asli = extract_mfcc(y_asli, sr_asli)
    mfcc_clone, mean_clone, std_clone, frame_var_clone = extract_mfcc(y_clone, sr_clone)

    pair_tag = f"{os.path.splitext(os.path.basename(file_asli))[0]}__{os.path.splitext(os.path.basename(file_clone))[0]}"

    print("===== INFORMASI AUDIO =====")
    print(f"Pair       : {pair_tag}")
    print(f"Platform   : {SOURCE_PLATFORM}")
    print(f"Tool Clone : {CLONING_TOOL}")
    print(f"Asli       : {file_asli} | SR={sr_asli} | Durasi={dur_asli:.2f} detik")
    print(f"Clone      : {file_clone} | SR={sr_clone} | Durasi={dur_clone:.2f} detik")

    print("===== SHAPE MFCC =====")
    print("MFCC Asli  :", mfcc_asli.shape)
    print("MFCC Clone :", mfcc_clone.shape)

    df = pd.DataFrame({
        "Koefisien_MFCC": [f"MFCC_{i}" for i in range(1, 14)],
        "Mean_Asli": mean_asli,
        "Std_Asli": std_asli,
        "Mean_Clone": mean_clone,
        "Std_Clone": std_clone,
    })

    csv_path = os.path.join(output_folder, f"hasil_perbandingan_mfcc_{pair_tag}.csv")
    df.to_csv(csv_path, index=False)

    plot_waveform(y_asli, sr_asli, f"Waveform Asli - {pair_tag}", os.path.join(output_folder, f"waveform_asli_{pair_tag}.png"))
    plot_waveform(y_clone, sr_clone, f"Waveform Cloning - {pair_tag}", os.path.join(output_folder, f"waveform_clone_{pair_tag}.png"))

    plot_spectrogram(y_asli, sr_asli, f"Spectrogram Asli - {pair_tag}", os.path.join(output_folder, f"spectrogram_asli_{pair_tag}.png"))
    plot_spectrogram(y_clone, sr_clone, f"Spectrogram Cloning - {pair_tag}", os.path.join(output_folder, f"spectrogram_clone_{pair_tag}.png"))

    plot_mfcc(mfcc_asli, sr_asli, f"MFCC Asli - {pair_tag}", os.path.join(output_folder, f"mfcc_asli_{pair_tag}.png"))
    plot_mfcc(mfcc_clone, sr_clone, f"MFCC Cloning - {pair_tag}", os.path.join(output_folder, f"mfcc_clone_{pair_tag}.png"))

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, 14), mean_asli, marker="o", label="Suara Asli")
    plt.plot(range(1, 14), mean_clone, marker="s", label="Voice Cloning")
    plt.title(f"Perbandingan Mean Koefisien MFCC - {pair_tag}")
    plt.xlabel("Koefisien MFCC")
    plt.ylabel("Nilai Mean")
    plt.xticks(range(1, 14))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"perbandingan_mean_mfcc_{pair_tag}.png"), dpi=300)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, 14), std_asli, marker="o", label="Std Suara Asli")
    plt.plot(range(1, 14), std_clone, marker="s", label="Std Voice Cloning")
    plt.title(f"Perbandingan Standar Deviasi Koefisien MFCC - {pair_tag}")
    plt.xlabel("Koefisien MFCC")
    plt.ylabel("Nilai Standar Deviasi")
    plt.xticks(range(1, 14))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"perbandingan_std_mfcc_{pair_tag}.png"), dpi=300)
    plt.close()

    plot_distribution(
        mean_asli,
        mean_clone,
        f"Distribusi Mean MFCC - {pair_tag}",
        os.path.join(output_folder, f"distribusi_mean_mfcc_{pair_tag}.png"),
    )

    plot_frame_variation(
        frame_var_asli,
        frame_var_clone,
        f"Variasi MFCC antar Frame - {pair_tag}",
        os.path.join(output_folder, f"variasi_frame_mfcc_{pair_tag}.png"),
    )

    return {
        "pair": pair_tag,
        "file_asli": file_asli,
        "file_clone": file_clone,
        "mean_gap_abs": float(np.mean(np.abs(mean_asli - mean_clone))),
        "std_gap_abs": float(np.mean(np.abs(std_asli - std_clone))),
        "durasi_asli": dur_asli,
        "durasi_clone": dur_clone,
        "sr_asli": sr_asli,
        "sr_clone": sr_clone,
    }

all_summary = []
for file_asli, file_clone in PAIRS:
    result = analyze_pair(file_asli, file_clone)
    if result is not None:
        all_summary.append(result)

if all_summary:
    summary_df = pd.DataFrame(all_summary)
    summary_path = os.path.join(output_folder, "ringkasan_pasangan_mfcc.csv")
    summary_df.to_csv(summary_path, index=False)
    print("\n===== SELESAI =====")
    print(f"Ringkasan antar pasangan disimpan di: {summary_path}")
    print("Semua hasil analisis tersimpan di folder 'hasil'")
else:
    raise RuntimeError("Tidak ada pasangan file yang valid untuk dianalisis.")