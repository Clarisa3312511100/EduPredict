# EduPredict - Sistem Cerdas Prediksi Kelulusan Mahasiswa Berbasis Machine Learning

Sistem pendukung keputusan (*Decision Support System*) dan *Early Warning System* berbasis Machine Learning untuk mendeteksi potensi risiko keterlambatan kelulusan mahasiswa sejak dini (Semester 1–4). Proyek ini dirancang sebagai pemenuhan **tugas/proyek akhir semester** di bidang Kecerdasan Buatan / Data Science.

---

## 📌 Ringkasan Masalah & Solusi
- **Masalah**: Keterlambatan kelulusan mahasiswa (> 8 semester) sering kali baru disadari saat mahasiswa berada di semester akhir (semester 7-8), sehingga ruang intervensi dosen wali/PA menjadi sangat terbatas.
- **Solusi**: Menganalisis riwayat nilai semester awal (IPS 1-4), SKS lulus vs gagal, kehadiran, dan variabel pendukung untuk memprediksi probabilitas keterlambatan serta memberikan rekomendasi perbaikan sebelum terlambat.

---

## 🚀 Fitur Utama Sistem

1. **Dataset Akademik Realistis**:
   - 1.500 sampel data mahasiswa dengan formula probabilitas berbasis aturan akademik perguruan tinggi di Indonesia.
2. **Multi-Model Machine Learning Benchmark**:
   - Membandingkan 3 algoritma: **Logistic Regression**, **Decision Tree**, dan **Random Forest**.
   - Evaluasi komprehensif: Akurasi, Presisi, Recall (Sensitivitas), F1-Score, dan ROC-AUC.
3. **Interpretasi & Feature Importance**:
   - Mengetahui faktor apa saja yang paling memicu risiko keterlambatan (misal: SKS gagal, penurunan drastis IPS, atau tingkat kehadiran).
4. **Interactive Web Dashboard (FastAPI)**:
   - **Dashboard Overview**: Ringkasan KPI dan grafik visualisasi status kelulusan.
   - **Simulasi Mandiri (What-if Analysis)**: Slider interaktif untuk menguji variasi nilai dan melihat hasil diagnosis langsung secara *real-time*.
   - **Prediksi Massal (Batch Upload)**: Mendukung upload file `.csv` atau `.xlsx` untuk memetakan seluruh mahasiswa satu angkatan/prodi sekaligus.

---

## 📂 Struktur Direktori

```text
Prediksi-kelulusan-mahasiswa/
│
├── data/
│   └── dataset_kelulusan.csv          # Dataset akademik mahasiswa (1.500 baris)
│
├── scripts/
│   ├── generate_data.py               # Generator data sintetis realistis
│   └── train_model.py                 # Script pelatihan, tuning, dan evaluasi model
│
├── models/
│   ├── best_model.joblib              # Pipeline model terlatih terbaik
│   ├── metrics_summary.json           # Rekap metrik akurasi, presisi, recall, F1
│   └── dataset_stats.json             # Statistik ringkasan data
│
├── app/
│   ├── main.py                        # REST API backend (FastAPI)
│   ├── predictor.py                   # Service inferensi & analisis faktor risiko
│   └── static/                        # Frontend Web Dashboard
│       ├── index.html                 # Halaman utama aplikasi
│       ├── css/style.css              # Styling modern, responsif & elegan
│       └── js/app.js                  # Logika interaksi UI & visualisasi Chart.js
│
├── requirements.txt                   # Daftar dependensi pustaka Python
└── README.md                          # Dokumentasi lengkap proyek
```

---

## 📊 Kamus Data (Feature Dictionary)

| Kolom | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `NIM` | String | Nomor Induk Mahasiswa (e.g. `2021000001`) |
| `Nama` | String | Nama lengkap mahasiswa |
| `Jenis_Kelamin` | Kategori | Laki-laki / Perempuan |
| `Jalur_Masuk` | Kategori | `SNBP`, `SNBT`, atau `Mandiri` |
| `IPS_Sem1` s.d `IPS_Sem4` | Float | Indeks Prestasi per semester (1.00 - 4.00) |
| `IPK_Kumulatif` | Float | IPK rata-rata tertimbang hingga Semester 4 |
| `SKS_Lulus` | Integer | Total SKS berhasil lulus (target ~80-88 SKS) |
| `SKS_Gagal` | Integer | Total SKS mata kuliah mengulang / bernilai D-E |
| `Persentase_Kehadiran` | Float | Rata-rata persentase presensi kuliah (60% - 100%) |
| `Status_Bekerja` | Biner | `0` = Tidak bekerja, `1` = Kuliah sambil bekerja |
| `Pernah_Cuti` | Biner | `0` = Tidak pernah, `1` = Pernah mengambil cuti kuliah |
| **`Status_Kelulusan`** | **Target** | **`Tepat Waktu`** ($\le$ 8 Semester) vs **`Terlambat`** (> 8 Semester) |

---

## 🛠️ Panduan Instalasi & Menjalankan Proyek

### 1. Prasyarat
- Python 3.10 atau versi yang lebih baru terpasang di komputer.

### 2. Instalasi Dependensi
Buka terminal pada direktori proyek dan jalankan:
```bash
pip install -r requirements.txt
```

### 3. Pembuatan Dataset (Opsional jika ingin regenerasi data)
```bash
python scripts/generate_data.py
```

### 4. Pelatihan Model Machine Learning
```bash
python scripts/train_model.py
```
*Skrip ini akan membandingkan performa model dan menyimpan model terbaik ke `models/best_model.joblib`.*

### 5. Menjalankan Aplikasi Web Dashboard
```bash
uvicorn app.main:app --reload --port 8000
```
Buka peramban (browser) dan akses:
👉 **`http://localhost:8000`**

Dokumentasi otomatis API (Swagger UI):
👉 **`http://localhost:8000/docs`**

---

## 📈 Metodologi Machine Learning

1. **Stratified Split**: Data dibagi 80% untuk data latih dan 20% untuk data uji dengan mempertahankan rasio kelas target.
2. **Preprocessing**:
   - `StandardScaler` untuk normalisasi fitur numerik.
   - `OneHotEncoder` untuk fitur kategorikal.
3. **Prioritas Metrik Evaluasi**:
   - Dalam sistem peringatan dini (*Early Warning System*), metrik **Recall** untuk kelas *"Terlambat"* adalah yang paling krusial, karena kegagalan mendeteksi mahasiswa yang sebenarnya berisiko (*False Negative*) jauh lebih berdampak buruk dibandingkan jika mahasiswa aman dicek ulang (*False Positive*).
