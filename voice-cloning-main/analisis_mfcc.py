import os
import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# KONFIGURASI & STYLING
# ============================================================
SOURCE_PLATFORM = "WhatsApp Voice Note"
CLONING_TOOL = "Minimax.AI"
OUTPUT_FOLDER = "hasil"
N_MFCC = 13
DPI = 300

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Matplotlib style configuration
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'

# ============================================================
# FUNGSI AUTO-DISCOVER PAIRS
# ============================================================
def discover_pairs(dataset_folder="dataset"):
    """
    Menemukan pasangan file asli dan clone berdasarkan naming convention.
    """
    asli_files = []
    clone_files = []
    
    if not os.path.exists(dataset_folder):
        raise FileNotFoundError(f"Folder '{dataset_folder}' tidak ditemukan")
    
    # Scan folder
    for file in os.listdir(dataset_folder):
        if file.lower().endswith(('.wav', '.mp3')):
            file_lower = file.lower()
            if 'asli' in file_lower and 'clone' not in file_lower:
                asli_files.append(os.path.join(dataset_folder, file))
            elif 'clone' in file_lower:
                clone_files.append(os.path.join(dataset_folder, file))
    
    # Pairing logic
    pairs = []
    for asli_file in sorted(asli_files):
        asli_basename = os.path.basename(asli_file)
        asli_id = asli_basename.replace('asli', '').replace('.wav', '').replace('.mp3', '').strip('_').lower()
        
        for clone_file in sorted(clone_files):
            clone_basename = os.path.basename(clone_file)
            clone_id = clone_basename.replace('clone', '').replace('.wav', '').replace('.mp3', '').strip('_').lower()
            
            if asli_id == clone_id:
                pairs.append((asli_file, clone_file))
                break
    
    return pairs

PAIRS = discover_pairs("dataset")
print(f"✓ Ditemukan {len(PAIRS)} pasangan asli-clone\n")

# ============================================================
# FUNGSI LOAD & EKSTRAKSI
# ============================================================
def load_audio(file_path):
    """Load audio file dengan error handling."""
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration = len(y) / sr
        return y, sr, duration
    except Exception as e:
        print(f"ERROR memuat {file_path}: {e}")
        return None, None, None

def extract_mfcc(y, sr, n_mfcc=N_MFCC):
    """Ekstraksi MFCC menggunakan librosa."""
    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        frame_var = np.var(mfcc, axis=0)
        return mfcc, mfcc_mean, mfcc_std, frame_var
    except Exception as e:
        print(f"ERROR ekstraksi MFCC: {e}")
        return None, None, None, None

# ============================================================
# FUNGSI VISUALISASI
# ============================================================
def plot_waveform(y, sr, title, save_path):
    """Plot waveform dengan styling profesional."""
    plt.figure(figsize=(12, 4))
    librosa.display.waveshow(y, sr=sr, color='steelblue', linewidth=0.5)
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Waktu (detik)", fontsize=11)
    plt.ylabel("Amplitudo", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_spectrogram(y, sr, title, save_path):
    """Plot spectrogram dengan colormap yang baik."""
    X = librosa.stft(y)
    X_db = librosa.amplitude_to_db(np.abs(X), ref=np.max)

    plt.figure(figsize=(12, 5))
    librosa.display.specshow(X_db, sr=sr, x_axis='time', y_axis='log', cmap='viridis')
    plt.colorbar(format='%+2.0f dB', label='Magnitude (dB)')
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Waktu (detik)", fontsize=11)
    plt.ylabel("Frekuensi (Hz)", fontsize=11)
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_mfcc(mfcc, sr, title, save_path):
    """Plot MFCC heatmap."""
    mfcc_db = librosa.amplitude_to_db(np.abs(mfcc), ref=np.max)
    
    plt.figure(figsize=(12, 5))
    librosa.display.specshow(mfcc_db, sr=sr, x_axis='time', y_axis='mel', cmap='coolwarm')
    plt.colorbar(format='%+2.0f dB', label='Magnitude (dB)')
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Waktu (detik)", fontsize=11)
    plt.ylabel("Koefisien MFCC", fontsize=11)
    plt.yticks(range(N_MFCC), [f'MFCC-{i+1}' for i in range(N_MFCC)], fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_mean_comparison(mean_asli, mean_clone, title, save_path):
    """Plot perbandingan mean MFCC coefficients."""
    x = np.arange(1, N_MFCC + 1)
    width = 0.35
    
    plt.figure(figsize=(12, 5))
    plt.bar(x - width/2, mean_asli, width, label='Suara Asli', color='steelblue', alpha=0.8, edgecolor='black')
    plt.bar(x + width/2, mean_clone, width, label='Voice Cloning', color='coral', alpha=0.8, edgecolor='black')
    
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Koefisien MFCC", fontsize=11)
    plt.ylabel("Nilai Mean", fontsize=11)
    plt.xticks(x, [f'MFCC-{i}' for i in x], fontsize=9)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_std_comparison(std_asli, std_clone, title, save_path):
    """Plot perbandingan standar deviasi."""
    x = np.arange(1, N_MFCC + 1)
    width = 0.35
    
    plt.figure(figsize=(12, 5))
    plt.bar(x - width/2, std_asli, width, label='Std Asli', color='seagreen', alpha=0.8, edgecolor='black')
    plt.bar(x + width/2, std_clone, width, label='Std Cloning', color='crimson', alpha=0.8, edgecolor='black')
    
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Koefisien MFCC", fontsize=11)
    plt.ylabel("Nilai Standar Deviasi", fontsize=11)
    plt.xticks(x, [f'MFCC-{i}' for i in x], fontsize=9)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_distribution(mean_asli, mean_clone, title, save_path):
    """Plot distribusi histogram mean MFCC."""
    plt.figure(figsize=(12, 5))
    plt.hist(mean_asli, bins=7, alpha=0.6, label="Mean Asli", color='steelblue', edgecolor='black')
    plt.hist(mean_clone, bins=7, alpha=0.6, label="Mean Clone", color='coral', edgecolor='black')
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Nilai Mean Koefisien MFCC", fontsize=11)
    plt.ylabel("Frekuensi", fontsize=11)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

def plot_frame_variation(frame_var_asli, frame_var_clone, title, save_path):
    """Plot variasi frame temporal MFCC."""
    n = min(len(frame_var_asli), len(frame_var_clone), 300)
    
    plt.figure(figsize=(12, 5))
    plt.plot(range(n), frame_var_asli[:n], label="Variasi Frame Asli", linewidth=2, color='steelblue', marker='o', markersize=3)
    plt.plot(range(n), frame_var_clone[:n], label="Variasi Frame Clone", linewidth=2, color='coral', marker='s', markersize=3)
    plt.title(title, fontsize=13, fontweight='bold')
    plt.xlabel("Frame Index", fontsize=11)
    plt.ylabel("Varians MFCC", fontsize=11)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()

# ============================================================
# ANALISIS PAIR-WISE
# ============================================================
def analyze_pair(file_asli, file_clone, idx):
    """Analisis pasangan file asli dan clone."""
    print(f"[{idx}/{len(PAIRS)}] Processing: {os.path.basename(file_asli)} ↔ {os.path.basename(file_clone)}")
    
    # Load audio
    y_asli, sr_asli, dur_asli = load_audio(file_asli)
    y_clone, sr_clone, dur_clone = load_audio(file_clone)
    
    if y_asli is None or y_clone is None:
        return None
    
    # Ekstraksi MFCC
    mfcc_asli, mean_asli, std_asli, frame_var_asli = extract_mfcc(y_asli, sr_asli)
    mfcc_clone, mean_clone, std_clone, frame_var_clone = extract_mfcc(y_clone, sr_clone)
    
    if mfcc_asli is None:
        return None
    
    pair_tag = f"{os.path.splitext(os.path.basename(file_asli))[0]}__{os.path.splitext(os.path.basename(file_clone))[0]}"
    
    # Simpan CSV
    df = pd.DataFrame({
        "Koefisien_MFCC": [f"MFCC_{i}" for i in range(1, N_MFCC + 1)],
        "Mean_Asli": mean_asli.round(6),
        "Std_Asli": std_asli.round(6),
        "Mean_Clone": mean_clone.round(6),
        "Std_Clone": std_clone.round(6),
        "Mean_Diff": (np.abs(mean_asli - mean_clone)).round(6),
        "Std_Diff": (np.abs(std_asli - std_clone)).round(6),
    })
    
    csv_path = os.path.join(OUTPUT_FOLDER, f"hasil_perbandingan_mfcc_{pair_tag}.csv")
    df.to_csv(csv_path, index=False)
    
    # Visualisasi
    plot_waveform(y_asli, sr_asli, f"Waveform Asli - {pair_tag}", 
                  os.path.join(OUTPUT_FOLDER, f"waveform_asli_{pair_tag}.png"))
    plot_waveform(y_clone, sr_clone, f"Waveform Cloning - {pair_tag}", 
                  os.path.join(OUTPUT_FOLDER, f"waveform_clone_{pair_tag}.png"))
    
    plot_spectrogram(y_asli, sr_asli, f"Spectrogram Asli - {pair_tag}", 
                     os.path.join(OUTPUT_FOLDER, f"spectrogram_asli_{pair_tag}.png"))
    plot_spectrogram(y_clone, sr_clone, f"Spectrogram Cloning - {pair_tag}", 
                     os.path.join(OUTPUT_FOLDER, f"spectrogram_clone_{pair_tag}.png"))
    
    plot_mfcc(mfcc_asli, sr_asli, f"MFCC Asli - {pair_tag}", 
              os.path.join(OUTPUT_FOLDER, f"mfcc_asli_{pair_tag}.png"))
    plot_mfcc(mfcc_clone, sr_clone, f"MFCC Cloning - {pair_tag}", 
              os.path.join(OUTPUT_FOLDER, f"mfcc_clone_{pair_tag}.png"))
    
    plot_mean_comparison(mean_asli, mean_clone, f"Perbandingan Mean MFCC - {pair_tag}",
                        os.path.join(OUTPUT_FOLDER, f"perbandingan_mean_mfcc_{pair_tag}.png"))
    
    plot_std_comparison(std_asli, std_clone, f"Perbandingan Std MFCC - {pair_tag}",
                       os.path.join(OUTPUT_FOLDER, f"perbandingan_std_mfcc_{pair_tag}.png"))
    
    plot_distribution(mean_asli, mean_clone, f"Distribusi Mean MFCC - {pair_tag}",
                     os.path.join(OUTPUT_FOLDER, f"distribusi_mean_mfcc_{pair_tag}.png"))
    
    plot_frame_variation(frame_var_asli, frame_var_clone, f"Variasi Frame MFCC - {pair_tag}",
                        os.path.join(OUTPUT_FOLDER, f"variasi_frame_mfcc_{pair_tag}.png"))
    
    # Summary metrics
    return {
        "pair": pair_tag,
        "file_asli": os.path.basename(file_asli),
        "file_clone": os.path.basename(file_clone),
        "sr_asli": sr_asli,
        "sr_clone": sr_clone,
        "durasi_asli_sec": round(dur_asli, 3),
        "durasi_clone_sec": round(dur_clone, 3),
        "mean_diff_avg": round(float(np.mean(np.abs(mean_asli - mean_clone))), 6),
        "std_diff_avg": round(float(np.mean(np.abs(std_asli - std_clone))), 6),
    }

# ============================================================
# MAIN EXECUTION
# ============================================================
if not PAIRS:
    raise RuntimeError("Tidak ada pasangan file asli-clone yang ditemukan!")

all_summary = []
for idx, (file_asli, file_clone) in enumerate(PAIRS, 1):
    result = analyze_pair(file_asli, file_clone, idx)
    if result is not None:
        all_summary.append(result)

# Simpan summary
summary_df = pd.DataFrame(all_summary)
summary_path = os.path.join(OUTPUT_FOLDER, "ringkasan_pasangan_mfcc.csv")
summary_df.to_csv(summary_path, index=False)

print("\n" + "="*70)
print("✓ ANALISIS PAIR-WISE SELESAI")
print("="*70)
print(f"Total pasangan dianalisis: {len(all_summary)}")
print(f"Hasil tersimpan di folder: {OUTPUT_FOLDER}")
print("="*70)
