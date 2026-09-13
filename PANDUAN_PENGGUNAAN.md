# Panduan Penggunaan Sistem EduPredict
*Dokumentasi Pengoperasian dan Pengujian Proyek Tugas Besar*

Dokumen ini berisi panduan pengoperasian aplikasi **EduPredict (Sistem Prediksi Kelulusan Mahasiswa Berbasis Machine Learning)** yang dikembangkan sebagai pemenuhan Tugas Besar. Panduan ini mencakup langkah instalasi, cara menjalankan server lokal, skenario demonstrasi aplikasi, peta file kode sumber, kamus data, serta ringkasan evaluasi model.

---

## 1. Ringkasan Proyek

- **Nama Aplikasi**: EduPredict
- **Tujuan**: Mendeteksi potensi keterlambatan kelulusan mahasiswa sejak semester awal (Semester 1–4) guna memberikan sinyal peringatan dini bagi Dosen Pembimbing Akademik (PA).
- **Komponen Utama**:
  - **Machine Learning**: Model klasifikasi Random Forest (Akurasi 89.17%, ROC-AUC 94.23%).
  - **Backend API**: Python FastAPI dan server Uvicorn.
  - **Frontend**: Web Dashboard (HTML5, CSS, JavaScript, dan Chart.js).
  - **Dataset**: 1.200 data rekam akademik mahasiswa hasil augmentasi empiris berbasis data perguruan tinggi Indonesia.

---

## 2. Langkah Menjalankan Aplikasi di Komputer Lokal

### Prasyarat
Pastikan komputer sudah terpasang **Python versi 3.10 atau yang lebih baru**.
Saat instalasi Python di Windows, pastikan opsi **"Add Python to PATH"** telah dicentang.

### Langkah 1: Membuka Folder Proyek di Terminal
Buka Command Prompt (CMD), PowerShell, atau terminal di editor (VS Code), lalu arahkan ke direktori proyek `Prediksi-kelulusan-mahasiswa`.

### Langkah 2: Memasang Dependensi
Jalankan perintah berikut untuk mengunduh seluruh pustaka yang diperlukan:
```bash
pip install -r requirements.txt
```

### Langkah 3: Menjalankan Server Lokal
Jalankan server aplikasi menggunakan Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
Jika server berhasil berjalan, terminal akan menampilkan informasi bahwa aplikasi aktif di `http://127.0.0.1:8000`.

### Langkah 4: Membuka Halaman Web
Buka browser (Google Chrome, Mozilla Firefox, atau Microsoft Edge), kemudian akses tautan:
**http://localhost:8000**

Untuk menghentikan server aplikasi, kembali ke jendela terminal lalu tekan kombinasi tombol **Ctrl + C**.

---

## 3. Penanganan Kendala (Troubleshooting)

| Kendala / Pesan Kesalahan | Kemungkinan Penyebab | Solusi |
| :--- | :--- | :--- |
| `pip is not recognized` atau `python is not recognized` | Python belum terdaftar pada variabel path sistem (*Environment Variables*). | Pasang ulang Python dan pastikan mencentang kotak "Add Python to PATH". |
| `Address already in use` (Port 8000 bentrok) | Port 8000 sedang digunakan oleh aplikasi lain. | Jalankan pada port alternatif, misalnya: `uvicorn app.main:app --reload --port 8080`, lalu buka `http://localhost:8080`. |
| Tampilan antarmuka tidak terbarui setelah edit kode | File cache pada browser masih memuat versi lama. | Tekan kombinasi **Ctrl + F5** pada browser untuk melakukan *hard refresh*. |

---

## 4. Alur Demonstrasi Aplikasi

Saat mempresentasikan demo aplikasi kepada dosen pengampu, urutan fitur yang dapat didemokan adalah sebagai berikut:

### Skenario 1: Halaman Ringkasan (Dashboard Overview)
- **Komponen yang ditampilkan**:
  - Tiga indikator utama: Total Sampel Data (1.200 baris), Rasio Kelulusan Tepat Waktu (62.3%), dan Akurasi Model (89.2%).
  - Diagram lingkaran (Donut Chart) sebaran status kelulusan.
  - Diagram batang Feature Importance (analisis fitur paling berpengaruh terhadap ketepatan kelulusan).
- **Penjelasan**:
  Menjelaskan bahwa halaman utama menyajikan ringkasan data historis angkatan mahasiswa, di mana variabel stabilitas IPK semester 1–4 dan tren nilai menjadi faktor paling menentukan.

### Skenario 2: Fitur Simulasi Prediksi Mandiri
- **Komponen yang didemokan**:
  - Masukkan data nilai melalui slider atau input angka:
    - Mahasiswa Kategori Aman: IPK 3.65, SKS 88, Tidak Bekerja. Hasil prediksi menunjukkan: **Tepat Waktu (Risiko Rendah)**.
    - Mahasiswa Kategori Berisiko: IPK 2.15, SKS 60, Bekerja. Hasil prediksi menunjukkan: **Terlambat (Risiko Tinggi)** beserta saran intervensi bimbingan akademik.
  - Fitur Cetak Rekomendasi: Menunjukkan lembar hasil diagnosis akademik yang siap dicetak untuk evaluasi bimbingan dosen wali/PA.

### Skenario 3: Fitur Prediksi Massal (Batch Upload CSV)
- **Komponen yang didemokan**:
  - Unggah file contoh dataset yang berada di `data/dataset_kelulusan.csv`.
  - Sistem akan langsung memproses seluruh data mahasiswa dalam file tersebut dan menampilkan tabel hasil klasifikasi secara otomatis.
  - Tunjukkan fitur pencarian berdasarkan NIM/Nama serta tombol ekspor hasil prediksi ke format CSV.

---

## 5. Peta Struktur File Proyek

Struktur file utama pada proyek ini dapat dijelaskan sebagai berikut:

| Bagian Sistem | Lokasi File | Fungsi |
| :--- | :--- | :--- |
| Pemodelan Machine Learning | `scripts/train_model.py` | Berisi tahapan pelatihan algoritma Random Forest, tuning hyperparameter, validasi silang (cross validation), dan kalkulasi metrik evaluasi. |
| Backend REST API | `app/main.py` | Berisi endpoint FastAPI untuk melayani permintaan data statistik, inferensi individu, dan proses batch upload file CSV. |
| Logika Prediksi & Aturan | `app/predictor.py` | Berisi fungsi pemanggilan model `.joblib`, inferensi probabilitas, dan penerapan aturan batas akademik (*Academic Guardrails*). |
| Antarmuka Web (Frontend) | `app/static/index.html`<br>`app/static/js/app.js` | `index.html` mengatur tata letak antarmuka, sedangkan `app.js` mengelola interaksi form, pemanggilan API, dan render grafik Chart.js. |
| Dataset | `data/dataset_kelulusan.csv` | File data akademik berisi 1.200 baris rekam jejak mahasiswa. |

---

## 6. Landasan Konseptual dan Pertanyaan Diskusi (FAQ)

Berikut rangkuman konsep dasar yang relevan saat sesi diskusi atau tanya-jawab proyek:

### 1. Mengapa memilih algoritma Random Forest?
Decision Tree tunggal memiliki kecenderungan mengalami overfitting dan sensitif terhadap fluktuasi data lokal. Random Forest menggunakan pendekatan ensemble yang menggabungkan hasil dari banyak pohon keputusan (100 estimators), sehingga menghasilkan varians yang lebih rendah, ketahanan terhadap noise, dan stabilitas prediksi yang lebih baik (akurasi 89.17% dan ROC-AUC 94.23%).

### 2. Dari mana sumber dataset dan berapa jumlah sampelnya?
Dataset berjumlah 1.200 sampel data mahasiswa. Data ini dikembangkan menggunakan metode Empirical Data Augmentation bersumber dari 379 rekam jejak riil mahasiswa di perguruan tinggi Indonesia, sehingga distribusi data dan korelasi antarvariabel tetap realistis untuk menggambarkan kondisi satu program studi/fakultas.

### 3. Variabel apa yang paling berpengaruh terhadap hasil prediksi?
Berdasarkan Feature Importance dari model Random Forest, variabel yang memiliki kontribusi terbesar adalah IPK Kumulatif semester 1–4, perolehan SKS tempuh, dan dinamika tren nilai semester. Faktor profil seperti status bekerja turut berpengaruh terhadap estimasi alokasi waktu studi mahasiswa.

### 4. Bagaimana sistem menangani mahasiswa dengan IPK rendah namun berstatus reguler (tidak bekerja)?
Sistem menerapkan pendekatan Hybrid Decision Support System. Selain mengandalkan probabilitas dari model Random Forest, terdapat aturan batas akademik (Academic Guardrails). Jika seorang mahasiswa memiliki IPK kumulatif di bawah batas standar kelulusan (< 2.50) atau mengalami tren penurunan nilai yang tajam, sistem otomatis menetapkan status risiko tinggi demi keandalan evaluasi akademik.

### 5. Apa saja metrik performa model yang dicapai?
Pengujian dilakukan pada 240 sampel data uji baru (unseen test data) dengan hasil:
- Akurasi: 89.17%
- Presisi: 87.36%
- Recall: 83.52% (mendeteksi 76 dari 91 mahasiswa berisiko terlambat)
- F1-Score: 85.39%
- ROC-AUC: 94.23%

---

## 7. Kamus Data (Data Dictionary)

Deskripsi kolom yang digunakan pada dataset dan form input:

| Nama Variabel | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `NIM` | Teks / Angka | Nomor Induk Mahasiswa. |
| `Nama` | Teks | Nama lengkap mahasiswa. |
| `Jenis_Kelamin` | Kategori | Laki-laki / Perempuan. |
| `Umur` | Numerik (Integer) | Usia mahasiswa (rentang 18 - 28 tahun). |
| `Status_Bekerja` | Biner (0 / 1) | 0 = Tidak Bekerja (Reguler), 1 = Bekerja. |
| `Status_Nikah` | Biner (0 / 1) | 0 = Belum Menikah, 1 = Sudah Menikah. |
| `IPS_Sem1` s.d `IPS_Sem4` | Numerik (Float) | Indeks Prestasi per semester (skala 0.00 - 4.00). |
| `IPK_Kumulatif` | Numerik (Float) | Indeks Prestasi Kumulatif hingga semester 4. |
| `Total_SKS` | Numerik (Integer) | Jumlah total SKS yang telah diselesaikan. |
| `Status_Kelulusan` | Target | Tepat Waktu (<= 8 semester) atau Terlambat (> 8 semester). |

---

## 8. Tabel Evaluasi dan Perbandingan Algoritma

Tabel perbandingan hasil pengujian performa algoritma yang dapat dicantumkan pada laporan tugas besar:

| Algoritma | Akurasi | Presisi | Recall | F1-Score | ROC-AUC | Catatan |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Random Forest Classifier** | **89.17%** | **87.36%** | **83.52%** | **85.39%** | **94.23%** | Model Terpilih (Kinerja Terbaik) |
| Decision Tree Classifier | 87.08% | 84.09% | 81.32% | 82.68% | 90.57% | Model Pembanding (Pohon Tunggal) |
| Logistic Regression | 85.00% | 83.95% | 74.73% | 79.07% | 93.24% | Model Pembanding (Linear) |

*Catatan: Seluruh metrik diuji menggunakan Stratified 5-Fold Cross Validation dan dievaluasi pada 240 sampel data uji.*

---

## 9. File Sampel untuk Uji Coba Unggah Massal

Untuk menguji fitur prediksi massal, dapat langsung menggunakan file sampel yang telah disediakan di:
`data/dataset_kelulusan.csv`

File tersebut telah disusun sesuai format kolom yang dipersyaratkan oleh sistem sehingga dapat langsung diproses tanpa modifikasi tambahan.
