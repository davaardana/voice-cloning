# Dokumentasi Analisis Voice Cloning dengan MFCC

## 📋 Pendahuluan

Dokumentasi ini menjelaskan proses analisis voice cloning menggunakan metode MFCC (Mel-Frequency Cepstral Coefficients). Proyek ini bertujuan untuk membandingkan karakteristik antara suara asli dengan hasil voice cloning.

---

## 📁 Struktur Folder

```
voice-cloning-main/
├── dataset/              # Folder berisi file audio (.wav)
│   ├── asli1.wav - asli5.wav    # File audio asli
│   ├── clone1.wav - clone5.wav  # File audio cloning
│   ├── asli_cowo.wav            # Audio asli cowo
│   ├── clone_cowo.wav           # Audio cloning cowo
│   └── beda_teks3.wav           # Audio dengan teks berbeda
├── hasil/                # Hasil analisis pair-wise
│   ├── waveform_*.png           # Visualisasi waveform
│   ├── spectrogram_*.png        # Visualisasi spektrogram
│   ├── mfcc_*.png               # Visualisasi MFCC heatmap
│   ├── perbandingan_*.png       # Grafik perbandingan
│   └── ringkasan_pasangan_mfcc.csv
├── hasil_full/           # Hasil analisis step-by-step
│   ├── 01_waveform_asli.png
│   ├── 02_mel_spectrogram.png
│   ├── 03_mfcc_heatmap.png
│   ├── 04_mean_std_mfcc.png
│   ├── 05_temporal_variation.png
│   └── mfcc_statistics.csv
├── analisis.py           # Script ekstraksi MFCC
├── analisis_mfcc.py      # Script analisis pair-wise
├── analisis_full.py      # Script step-by-step MFCC
└── backend_api.py        # Flask API (opsional)
```

---

## 🔬 Teori MFCC

### Apa itu MFCC?

**MFCC (Mel-Frequency Cepstral Coefficients)** adalah fitur audio yang paling umum digunakan dalam:
- Pengenalan suara (Speech Recognition)
- Identifikasi speaker
- Klasifikasi audio
- Voice cloning analysis

### Tahapan Ekstraksi MFCC

| Tahap | Nama | Penjelasan |
|-------|------|------------|
| 1 | Pre-emphasis | Memperkuat frekuensi tinggi |
| 2 | Framing | Membagi audio menjadi frame kecil (20-40ms) |
| 3 | Windowing | Aplikasikan fungsi window (Hamming) |
| 4 | FFT | Transformasi waktu ke frekuensi |
| 5 | Mel Filterbank | Konversi ke skala Mel |
| 6 | Log | Logaritma dari output filterbank |
| 7 | DCT | Reduksi dimensi menjadi koefisien MFCC |

### Formula Matematika

**Konversi Hz ke Mel:**
```
m = 2595 × log10(1 + f/700)
```

**Formula MFCC:**
```
c[n] = Σ(k=0 to K-1) log(S[k]) × cos(πn(k+0.5)/K)
```

Dimana:
- `c[n]` = koefisien MFCC ke-n
- `S[k]` = output Mel filterbank
- `K` = jumlah filter
- `n` = nomor koefisien (1-13)

---

## 📝 Penjelasan Kode Python

### 1. analisis.py - Ekstraksi MFCC

Script utama untuk mengekstraksi fitur MFCC dari semua file audio.

**Parameter Konfigurasi:**
```python
N_MFCC = 13        # Jumlah koefisien MFCC
SR = None          # Sample rate (None = otomatis)
DATASET_FOLDER = "dataset"
```

**Fungsi Utama:**
```python
def extract_mfcc(audio_path, n_mfcc=13):
    """Ekstraksi MFCC menggunakan librosa"""
    y, sr = librosa.load(audio_path, sr=SR)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    return mfcc_mean, mfcc_std
```

**Output:**
- `hasil_mfcc.csv` - Semua fitur MFCC per file
- `ringkasan_hasil_mfcc.csv` - Ringkasan statistik per kategori

### 2. analisis_mfcc.py - Analisis Pair-wise

Membandingkan file asli dengan cloning secara berpasangan.

**Pasangan yang dianalisis:**
1. asli1.wav ↔ clone1.wav
2. asli2.wav ↔ clone2.wav
3. asli3.wav ↔ clone3.wav
4. asli4.wav ↔ clone4.wav
5. asli5.wav ↔ clone5.wav
6. asli_cowo.wav ↔ clone_cowo.wav

**Visualisasi yang Dihasilkan (9 per pasangan):**
- Waveform asli dan clone
- Spectrogram asli dan clone
- MFCC heatmap asli dan clone
- Perbandingan mean MFCC
- Perbandingan std MFCC
- Distribusi mean MFCC
- Variasi frame MFCC

### 3. analisis_full.py - Step-by-Step MFCC

Menampilkan tahapan ekstraksi MFCC secara detail untuk satu file audio.

**File yang Dihasilkan:**
1. `01_waveform_asli.png` - Bentuk gelombang audio
2. `02_mel_spectrogram.png` - Spektrogram skala Mel
3. `03_mfcc_heatmap.png` - Heatmap koefisien MFCC
4. `04_mean_std_mfcc.png` - Grafik mean dan std
5. `05_temporal_variation.png` - Variasi temporal MFCC

---

## 📊 Hasil Analisis

### Tabel Perbandingan Pasangan

| Pasangan | File Asli | File Clone | Selisih Mean | Selisih Std |
|----------|-----------|------------|--------------|-------------|
| 1 | asli1.wav | clone1.wav | 9.62 | 4.75 |
| 2 | asli2.wav | clone2.wav | 9.51 | 3.04 |
| 3 | asli3.wav | clone3.wav | 8.59 | 4.33 |
| 4 | asli4.wav | clone4.wav | 10.27 | 2.58 |
| 5 | asli5.wav | clone5.wav | 10.22 | 3.23 |
| 6 | asli_cowo.wav | clone_cowo.wav | 7.50 | 2.17 |

### Interpretasi Hasil

- **Selisih Mean**: Menunjukkan perbedaan rata-rata nilai MFCC antara suara asli dan cloning
- **Selisih Std**: Menunjukkan perbedaan variasi/karakteristik suara
- **Nilai lebih kecil** = Kemiripan lebih tinggi

### Statistik MFCC (Contoh: asli1.wav)

| Koefisien | Mean | Std Dev |
|-----------|------|---------|
| MFCC-1 | -395.49 | 67.61 |
| MFCC-2 | 161.06 | 53.63 |
| MFCC-3 | 43.23 | 32.66 |
| MFCC-4 | 22.38 | 27.76 |
| MFCC-5 | 13.09 | 23.77 |
| MFCC-6 | -7.23 | 18.00 |
| MFCC-7 | 4.70 | 18.75 |
| MFCC-8 | 9.63 | 11.96 |
| MFCC-9 | -7.57 | 14.35 |
| MFCC-10 | -5.64 | 13.29 |
| MFCC-11 | 8.31 | 12.04 |
| MFCC-12 | 4.34 | 11.06 |
| MFCC-13 | -6.97 | 8.84 |

---

## 🎨 Penjelasan Visualisasi

### Folder hasil_full/

| File | Penjelasan |
|------|------------|
| `01_waveform_asli.png` | **Waveform** - Bentuk gelombang dalam domain waktu. Sumbu X = waktu (detik), Sumbu Y = amplitude. |
| `02_mel_spectrogram.png` | **Mel Spectrogram** - Spektrogram dalam skala Mel. Warna = intensitas energi pada frekuensi tertentu. |
| `03_mfcc_heatmap.png` | **MFCC Heatmap** - Visualisasi koefisien MFCC per frame. Sumbu X = frame, Sumbu Y = koefisien. |
| `04_mean_std_mfcc.png` | **Mean & Std** - Grafik mean (bar) dengan error bar (std) untuk setiap koefisien MFCC. |
| `05_temporal_variation.png` | **Temporal Variation** - Bagaimana nilai MFCC berubah sepanjang waktu untuk setiap koefisien. |

### Folder hasil/

| Tipe File | Penjelasan |
|-----------|------------|
| `waveform_*.png` | Perbandingan bentuk gelombang asli vs clone |
| `spectrogram_*.png` | Perbandingan spektrogram asli vs clone |
| `mfcc_*.png` | Perbandingan heatmap MFCC asli vs clone |
| `perbandingan_mean_mfcc_*.png` | Grafik garis perbandingan mean MFCC |
| `perbandingan_std_mfcc_*.png` | Grafik garis perbandingan std MFCC |
| `distribusi_mean_mfcc_*.png` | Distribusi nilai mean MFCC |
| `variasi_frame_mfcc_*.png` | Variasi MFCC antar frame |

---

## 🚀 Cara Menjalankan

### 1. Ekstraksi MFCC
```bash
python analisis.py
```

### 2. Analisis Pair-wise
```bash
python analisis_mfcc.py
```

### 3. Analisis Step-by-Step
```bash
python analisis_full.py
```

### 4. Generate Laporan Word
```bash
python create_word_doc.py
```

---

## 📦 Dependencies

```
librosa>=0.10.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
scipy>=1.7.0
python-docx>=0.8.0
```

---

## 📖 Kesimpulan

1. **Metode MFCC** efektif untuk analisis karakteristik suara
2. **Koefisien MFCC-1** (energi rata-rata) menunjukkan perbedaan signifikan
3. **Visualisasi heatmap** membantu melihat pola distribusi temporal
4. **Perbandingan mean/std** memberikan informasi kuantitatif kemiripan
5. Voice cloning berkualitas tinggi memiliki selisih nilai yang lebih kecil

---

*Dokumentasi ini dibuat untuk mendukung penelitian Tugas Akhir / Thesis*