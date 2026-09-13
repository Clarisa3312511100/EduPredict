# 📘 BUKU PANDUAN PENGGUNAAN SISTEM EDUPREDICT
*(Pedoman Operasional, Pengujian Sistem & Simulasi Prediksi)*

Selamat datang di buku panduan **EduPredict (Sistem Cerdas Prediksi Kelulusan Mahasiswa Berbasis Machine Learning)**. Sistem ini telah selesai dikembangkan secara menyeluruh, mencakup pipeline Machine Learning, RESTful API backend, hingga dashboard web interaktif modern.

Dokumen ini disusun secara terstruktur sebagai acuan operasional untuk:
1. Menjalankan dan menguji aplikasi secara mandiri di lingkungan lokal.
2. Melakukan skenario demonstrasi dan simulasi evaluasi akademik.
3. Memahami arsitektur teknis, kamus data, serta dasar pemodelan Machine Learning.

---

## 📌 1. Ringkasan Singkat Proyek

- **Nama Aplikasi**: **EduPredict**
- **Fungsi Utama**: Mendeteksi sedini mungkin (Semester 1–4) potensi keterlambatan kelulusan mahasiswa agar Dosen Pembimbing Akademik (PA) dapat memberikan bimbingan intervensi sebelum terlambat.
- **Teknologi yang Digunakan**:
  - **Machine Learning**: Random Forest Classifier (Akurasi **89.17%**, ROC-AUC **94.23%**).
  - **Backend API**: Python FastAPI & Uvicorn (ringan, cepat, dan modern).
  - **Frontend / Tampilan**: Web Dashboard responsif (HTML5, CSS modern, Vanilla JS, dan Chart.js).
  - **Dataset**: 1.200 sampel data akademik mahasiswa berbasis data riil perguruan tinggi di Indonesia.

---

## 💻 2. Cara Menjalankan Aplikasi di Laptop (Langkah demi Langkah)

Ikuti 3 langkah mudah berikut untuk menjalankan aplikasi:

### Prasyarat Awal (Hanya sekali di awal)
Pastikan laptop Anda sudah terinstall **Python (versi 3.10 atau lebih baru)**.
> ⚠️ **PENTING saat install Python**: Pastikan Anda mencentang kotak **"Add Python to PATH"** di installer Python!

---

### Langkah 1: Buka Folder Proyek di Terminal / CMD
1. Buka aplikasi **Command Prompt (CMD)** atau terminal di **VS Code**.
2. Masuk ke folder proyek `Prediksi-kelulusan-mahasiswa`.

### Langkah 2: Install Library / Paket Pendukung
Ketik perintah berikut lalu tekan **Enter**:
```bash
pip install -r requirements.txt
```
*(Tunggu 1–2 menit sampai semua paket berhasil di-download dan terpasang).*

### Langkah 3: Nyalakan Server Aplikasi
Ketik perintah berikut lalu tekan **Enter**:
```bash
uvicorn app.main:app --reload --port 8000
```
Jika berhasil, di terminal akan muncul tulisan:
`Application startup complete.` dan `Uvicorn running on http://127.0.0.1:8000`.

### Langkah 4: Buka di Browser
Buka browser Anda (Google Chrome / Microsoft Edge), lalu ketik alamat:
👉 **`http://localhost:8000`**

Aplikasi dashboard **EduPredict** sudah langsung siap digunakan! 🎉

> 🛑 **Cara Mematikan Aplikasi**:  
> Jika sudah selesai, kembali ke terminal/CMD lalu tekan tombol **`Ctrl` + `C`** di keyboard.

---

## 🛠️ 3. Mengatasi Kendala Umum (Troubleshooting)

| Kendala / Error | Penyebab | Solusi Cepat |
| :--- | :--- | :--- |
| `'pip' is not recognized` atau `'python' is not recognized` | Python belum masuk ke sistem Environment Variables. | Install ulang Python dan pastikan mencentang **"Add Python to PATH"**. |
| `Address already in use` atau port 8000 bentrok | Port 8000 sedang dipakai aplikasi lain. | Jalankan dengan port lain, contoh: `uvicorn app.main:app --reload --port 8080`, lalu buka `http://localhost:8080`. |
| Perubahan kode/tampilan tidak muncul | Cache browser masih menyimpan tampilan lama. | Tekan tombol **`Ctrl` + `F5`** di browser untuk Hard Refresh. |

---

## 🎬 4. Skenario Demo Presentasi di Depan Dosen (Wajib Dicoba!)

Saat presentasi atau demo ke dosen, Anda cukup mendemokan 3 bagian utama ini secara berurutan:

```
[1. Halaman Beranda]  ➡️  [2. Tab Simulasi Mandiri]  ➡️  [3. Tab Prediksi Massal]
(Pamerkan Statistik)      (Coba Masukkan Angka)           (Upload File CSV Angkatan)
```

### Skenario 1: Tampilkan Halaman Overview (Beranda)
- **Apa yang ditunjukkan**:
  - Tiga kartu KPI: Total Mahasiswa (1.200 sampel), Tingkat Kelulusan Tepat Waktu (62.3%), dan Akurasi Model (89.2%).
  - Donut Chart sebaran status kelulusan.
  - Diagram Batang **Feature Importance** (Faktor yang paling menentukan kelulusan).
- **Kalimat yang bisa diucapkan**:
  > *"Bapak/Ibu Dosen, ini adalah halaman ringkasan data historis. Di sini terlihat variabel yang paling dominan mempengaruhi ketepatan kelulusan adalah stabilitas IPK semester 1–4 dan tren penurunan nilai."*

### Skenario 2: Masuk ke Tab "Simulasi Mandiri (What-If)"
- **Apa yang didemokan**:
  - Geser slider atau ketik nilai:
    - **Contoh Mahasiswa Aman**: IPK 3.65, SKS 88, Tidak Bekerja. Klik "Prediksi Sekarang" ➡️ Hasil keluar: **Tepat Waktu (Risiko Rendah)** warna hijau.
    - **Contoh Mahasiswa Berisiko**: IPK 2.15, SKS 60, Bekerja. Klik "Prediksi Sekarang" ➡️ Hasil keluar: **Terlambat (Risiko Tinggi)** warna merah, lengkap dengan rekomendasi bimbingan akademik.
  - Klik tombol **"Cetak Rekomendasi Bimbingan"** untuk membuktikan bahwa lembar intervensi bisa langsung dicetak/diekspor ke PDF untuk dosen PA.

### Skenario 3: Masuk ke Tab "Prediksi Massal (Batch Ingestion)"
- **Apa yang didemokan**:
  - Tunjukkan bahwa sistem tidak hanya bisa cek 1 orang, tapi bisa cek **1 angkatan sekaligus**.
  - Klik tombol upload file, pilih file contoh di `data/dataset_kelulusan.csv`.
  - Sistem akan langsung menampilkan tabel hasil prediksi seluruh mahasiswa secara instan.
  - Tunjukkan fitur **Pencarian Nama/NIM** dan tombol **"Unduh Hasil Prediksi (CSV)"**.

---

## 📂 5. Peta Kodingan (Jika Dosen Meminta "Coba Buka Kodingannya")

Jika dosen bertanya atau menyuruh Anda membuka file kode di VS Code, buka file-file ini:

| Pertanyaan Dosen | File yang Harus Anda Buka | Penjelasan Singkat untuk Dosen |
| :--- | :--- | :--- |
| *"Mana kodingan Machine Learning / Algoritma pemodelannya?"* | `scripts/train_model.py` | Berisi proses training algoritma Random Forest, tuning hyperparameter, dan perhitungan akurasi, presisi, recall, F1-score, serta ROC-AUC. |
| *"Mana kodingan backend / API-nya?"* | `app/main.py` | Berisi endpoint REST API FastAPI untuk melayani permintaan data statistik, prediksi single, dan prediksi batch upload CSV. |
| *"Mana logika pemrosesan prediksi dan aturan akademiknya?"* | `app/predictor.py` | Berisi fungsi load model `.joblib`, inferensi probabilitas, dan *Academic Guardrails* (aturan batas IPK). |
| *"Mana kodingan antarmuka / tampilannya?"* | `app/static/index.html`<br>`app/static/js/app.js` | `index.html` untuk struktur tata letak dashboard, dan `app.js` untuk menghubungkan form ke backend API serta merender grafik Chart.js. |
| *"Mana dataset yang digunakan?"* | `data/dataset_kelulusan.csv` | File dataset berisi 1.200 baris rekam jejak akademik mahasiswa. |

---

## 💡 6. Landasan Ilmiah & Tanya-Jawab Evaluasi Sistem (FAQ)

Poin-poin penjelasan berikut merangkum dasar konseptual yang dapat digunakan dalam mempresentasikan cara kerja sistem:

### Q1: *"Kenapa memilih algoritma Random Forest, kenapa bukan Decision Tree biasa?"*
> **Penjelasan Konseptual**:  
> *"Decision Tree tunggal rentan mengalami overfitting dan mudah terkecoh data ekstrem. Random Forest adalah algoritma ensemble yang menggabungkan 100 pohon keputusan, sehingga hasil probabilitasnya jauh lebih stabil, tahan terhadap noise, dan terbukti menghasilkan akurasi tertinggi yaitu 89.17% dengan ROC-AUC 94.23%."*

### Q2: *"Datasetnya dapat dari mana dan ada berapa banyak?"*
> **Penjelasan Konseptual**:  
> *"Dataset kami berjumlah 1.200 sampel data mahasiswa. Data ini dikembangkan menggunakan metode Empirical Data Augmentation berbasis 379 rekam jejak riil mahasiswa di perguruan tinggi Indonesia, sehingga pola distribusinya tetap realistis dan proporsional untuk merepresentasikan populasi satu fakultas."*

### Q3: *"Apa saja faktor yang paling mempengaruhi kelulusan menurut sistem?"*
> **Penjelasan Konseptual**:  
> *"Berdasarkan analisis Feature Importance dari model Random Forest, faktor paling dominan adalah IPK Kumulatif semester 1–4, perolehan SKS tempuh, dan tren kenaikan/penurunan nilai semester. Faktor eksternal seperti status bekerja juga berkontribusi pada beban manajemen waktu mahasiswa."*

### Q4: *"Bagaimana jika ada mahasiswa yang nilainya sangat rendah (IPK 2.0), tapi karena dia tidak bekerja, apakah model bisa salah memprediksi dia lulus tepat waktu?"*
> **Penjelasan Konseptual**:  
> *"Sistem kami menggunakan pendekatan **Hybrid Decision Support System**. Selain mengandalkan probabilitas Random Forest, kami memasang **Academic Rule Guardrails**. Jika IPK mahasiswa berada di bawah standar kelulusan (< 2.50) atau tren nilainya anjlok drastis, sistem secara otomatis mengeskalasi risiko menjadi 'Terlambat / Berisiko Tinggi' demi keselamatan akademik mahasiswa."*

### Q5: *"Berapa metrik evaluasi model Anda secara lengkap?"*
> **Penjelasan Konseptual**:  
> *"Dari 240 sampel data uji (data baru yang belum pernah dilihat model), model kami mencatat:*  
> *- **Akurasi**: 89.17%*  
> *- **Presisi**: 87.36%*  
> *- **Recall (Sensitivitas Risiko)**: 83.52% (Mampu mendeteksi 76 dari 91 mahasiswa bermasalah)*  
> *- **ROC-AUC**: 94.23% (Kategori Sangat Istimewa / Outstanding Discrimination)*  

---

## 📊 7. Kamus Data & Arti Variabel (Data Dictionary)

Gunakan tabel ini jika dosen bertanya mengenai arti kolom pada dataset atau input form:

| Nama Variabel | Tipe Data | Keterangan & Rentang Nilai |
| :--- | :--- | :--- |
| `NIM` | Teks / Angka | Nomor Induk Mahasiswa unik (contoh: `2021001`). |
| `Nama` | Teks | Nama lengkap mahasiswa. |
| `Jenis_Kelamin` | Kategori | `Laki-laki` atau `Perempuan`. |
| `Umur` | Angka Bulat | Usia saat masa studi aktif (rentang 18 - 28 tahun). |
| `Status_Bekerja` | Biner (`0` atau `1`) | `0` = Tidak Bekerja (Reguler / Fokus Kuliah), `1` = Bekerja (Paruh/Penuh Waktu). |
| `Status_Nikah` | Biner (`0` atau `1`) | `0` = Belum Menikah (Lajang), `1` = Sudah Menikah. |
| `IPS_Sem1` s.d `IPS_Sem4` | Desimal (`Float`) | Indeks Prestasi Semester 1 hingga 4 (rentang 0.00 - 4.00). |
| `IPK_Kumulatif` | Desimal (`Float`) | Nilai IPK rata-rata sampai semester 4. |
| `Total_SKS` | Angka Bulat | Jumlah SKS yang telah ditempuh (normal semester 4 adalah 72 - 96 SKS). |
| **`Status_Kelulusan`** | **Target Prediksi** | **`Tepat Waktu`** ($\le$ 8 Semester / 4 Tahun) atau **`Terlambat`** (> 8 Semester). |

---

## 📈 8. Tabel Evaluasi & Komparasi Algoritma (Bahan Laporan / Skripsi)

Jika Anda butuh data untuk dimasukkan ke Bab 4 Skripsi / Laporan Tugas Akhir, gunakan tabel perbandingan resmi pengujian model berikut:

| Algoritma | Akurasi | Presisi | Recall (Sensitivitas) | F1-Score | ROC-AUC | Keterangan |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Random Forest Classifier** | **89.17%** | **87.36%** | **83.52%** | **85.39%** | **94.23%** | 🏆 **Model Terpilih (Tertinggi)** |
| **Decision Tree Classifier** | 87.08% | 84.09% | 81.32% | 82.68% | 90.57% | Baseline Pohon Tunggal |
| **Logistic Regression** | 85.00% | 83.95% | 74.73% | 79.07% | 93.24% | Baseline Linear |

> 📌 **Catatan**: Seluruh metrik di atas diuji secara adil menggunakan teknik **Stratified 5-Fold Cross Validation** dan dievaluasi pada **240 sampel data uji baru** (*unseen test data*).

---

## 📁 9. File Siap Pakai untuk Demo Upload Massal (Batch)

Untuk mencoba fitur upload massal saat demo, Anda bisa langsung menggunakan file:
👉 **`data/dataset_kelulusan.csv`**

File ini sudah berisi format kolom yang persis sesuai standar sistem, sehingga ketika di-upload, tabel hasil prediksi angkatan akan langsung muncul seketika!

---

**Selamat Berpresentasi & Semoga Sukses Ujian/Sidangnya! 🚀**
