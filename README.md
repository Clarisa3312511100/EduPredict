# EduPredict - Sistem Cerdas Prediksi Kelulusan Mahasiswa Berbasis Machine Learning

Sistem pendukung keputusan (*Decision Support System*) dan *Early Warning System* berbasis Machine Learning untuk mendeteksi potensi risiko keterlambatan kelulusan mahasiswa sejak dini (Semester 1–4) menggunakan **1.200 Sampel Data Mahasiswa (Empirical Data Augmentation berbasis Data Riil Perguruan Tinggi Indonesia)**.

---

## 📌 Ringkasan Masalah & Solusi
- **Masalah**: Keterlambatan kelulusan mahasiswa (> 8 semester) sering kali baru disadari saat mahasiswa berada di semester akhir (semester 7-8), sehingga ruang intervensi dosen wali/PA menjadi sangat terbatas.
- **Solusi**: Menganalisis riwayat nilai semester awal (IPS 1 s.d 4), IPK kumulatif, profil mahasiswa (usia, status bekerja, status menikah), dan tren dinamika prestasi belajar guna memprediksi probabilitas keterlambatan serta memberikan rekomendasi perbaikan sebelum terlambat.

---

## 🚀 Fitur Utama Sistem

1. **Dataset Akademik Proporsional (1.200 Sampel)**:
   - Dikembangkan melalui metode *Empirical Data Augmentation* bersumber dari **379 rekam jejak riil mahasiswa perguruan tinggi Indonesia**.
   - Merepresentasikan ukuran populasi 1 fakultas/program studi secara utuh dan seimbang.
2. **Multi-Model Machine Learning Benchmark**:
   - Membandingkan 3 algoritma: **Random Forest**, **Decision Tree**, dan **Logistic Regression**.
   - Model terpilih: **Random Forest Classifier** dengan **Akurasi 89.17%**, **Presisi 87.36%**, **Recall 83.52%**, dan **ROC-AUC 94.23%**.
3. **Hybrid AI Decision Support System**:
   - Memadukan kecerdasan model Machine Learning dengan *Academic Rule Guardrails* (standar kelulusan Dikti) agar mahasiswa dengan IPK kritis (< 2.50) langsung terdeteksi secara akurat tanpa tertipu oleh variabel status eksternal.
4. **Interactive Web Dashboard (FastAPI)**:
   - **Dashboard Overview**: Ringkasan KPI dan grafik visualisasi distribusi status kelulusan.
   - **Simulasi Mandiri (What-if Analysis)**: Slider interaktif untuk menguji variasi nilai dan melihat hasil diagnosis langsung secara *real-time*.
   - **Prediksi Massal (Batch Upload)**: Mendukung upload file `.csv` atau `.xlsx` untuk memetakan seluruh mahasiswa satu angkatan/prodi sekaligus.
5. **Dokumentasi Terpisah & Transparan**:
   - Analisis lengkap evaluasi teknis, metodologi augmentasi, dan panduan tanya-jawab sidang tersedia di [`EVALUASI_MODEL.md`](./EVALUASI_MODEL.md).

---

## 📂 Struktur Direktori

```text
Prediksi-kelulusan-mahasiswa/
│
├── data/
│   ├── dataset_kelulusan.csv          # Dataset akademik ter-augmentasi (1.200 baris)
│   └── datakelulusanmahasiswa.xls     # File mentah dataset asli (379 baris)
│
├── scripts/
│   ├── augment_dataset.py             # Script augmentasi data empiris
│   ├── train_model.py                 # Script pelatihan, tuning, dan evaluasi model
│   └── test_app.py                    # Script pengujian otomatis predictor & API
│
├── models/
│   ├── best_model.joblib              # Model terlatih terbaik (Random Forest)
│   ├── metrics_summary.json           # Rekap metrik evaluasi model
│   └── dataset_stats.json             # Statistik ringkasan data latih
│
├── app/
│   ├── main.py                        # REST API backend (FastAPI)
│   ├── predictor.py                   # Service inferensi & Hybrid Academic Guardrails
│   └── static/                        # Frontend Web Dashboard
│       ├── index.html                 # Halaman dashboard web
│       ├── css/style.css              # Styling responsif & elegan
│       └── js/app.js                  # Logika UI interaktif & visualisasi Chart.js
│
├── requirements.txt                   # Dependensi pustaka Python
├── EVALUASI_MODEL.md                  # Laporan teknis benchmark & evaluasi model
└── README.md                          # Dokumentasi umum proyek
```

---

## 📊 Kamus Data (Feature Dictionary)

| Kolom | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `NIM` | String | Nomor Induk Mahasiswa (e.g. `20180001`) |
| `Nama` | String | Nama lengkap mahasiswa |
| `Jenis_Kelamin` | Kategori | `Laki-laki` / `Perempuan` |
| `Umur` | Integer | Usia mahasiswa saat perkuliahan berlangsung |
| `Status_Bekerja` | Biner | `0` = Tidak Bekerja, `1` = Bekerja |
| `Status_Nikah` | Biner | `0` = Belum Menikah, `1` = Menikah |
| `IPS_Sem1` s.d `IPS_Sem4` | Float | Indeks Prestasi per semester (1.00 - 4.00) |
| `IPK_Kumulatif` | Float | Indeks Prestasi Kumulatif hingga Semester 4 |
| **`Status_Kelulusan`** | **Target** | **`Tepat Waktu`** ($\le$ 8 Semester) vs **`Terlambat`** (> 8 Semester) |

---

## 🛠️ Panduan Instalasi & Menjalankan Proyek

### 1. Prasyarat
- Python 3.10 atau versi yang lebih baru.

### 2. Instalasi Dependensi
Buka terminal pada direktori proyek dan jalankan:
```bash
pip install -r requirements.txt
```

### 3. Augmentasi Dataset (Opsional jika ingin regenerasi data)
```bash
python scripts/augment_dataset.py
```

### 4. Pelatihan Model Machine Learning
```bash
python scripts/train_model.py
```

### 5. Menjalankan Pengujian Otomatis
```bash
python scripts/test_app.py
```

### 6. Menjalankan Aplikasi Web Dashboard
```bash
uvicorn app.main:app --reload --port 8000
```
Buka peramban (browser) dan akses:
👉 **`http://localhost:8000`**

Dokumentasi otomatis API (Swagger UI):
👉 **`http://localhost:8000/docs`**
