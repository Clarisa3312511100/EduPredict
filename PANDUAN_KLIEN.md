# 📘 PANDUAN PENGGUNAAN & HANDOVER PROYEK EDUPREDICT
*(Dokumentasi Khusus Klien / Mahasiswa)*

Selamat! Proyek **EduPredict (Sistem Cerdas Prediksi Kelulusan Mahasiswa Berbasis Machine Learning)** telah selesai dikembangkan secara lengkap, mulai dari pipeline Machine Learning, RESTful API backend, hingga dashboard web interaktif modern.

Dokumen ini disusun dengan bahasa yang **mudah dipahami** agar Anda dapat:
1. Menjalankan aplikasi sendiri di laptop tanpa kendala teknis.
2. Melakukan demo dengan percaya diri di hadapan dosen pembimbing/penguji.
3. Menjawab pertanyaan-pertanyaan teknis saat presentasi/sidang.

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

## 💡 6. Bocoran Kunci Jawaban Pertanyaan Dosen

Hafalkan 5 poin penting ini agar Anda lancar menjawab saat ditanya dosen penguji:

### Q1: *"Kenapa memilih algoritma Random Forest, kenapa bukan Decision Tree biasa?"*
> **Jawaban Mantap**:  
> *"Decision Tree tunggal rentan mengalami overfitting dan mudah terkecoh data ekstrem. Random Forest adalah algoritma ensemble yang menggabungkan 100 pohon keputusan, sehingga hasil probabilitasnya jauh lebih stabil, tahan terhadap noise, dan terbukti menghasilkan akurasi tertinggi yaitu 89.17% dengan ROC-AUC 94.23%."*

### Q2: *"Datasetnya dapat dari mana dan ada berapa banyak?"*
> **Jawaban Mantap**:  
> *"Dataset kami berjumlah 1.200 sampel data mahasiswa. Data ini dikembangkan menggunakan metode Empirical Data Augmentation berbasis 379 rekam jejak riil mahasiswa di perguruan tinggi Indonesia, sehingga pola distribusinya tetap realistis dan proporsional untuk merepresentasikan populasi satu fakultas."*

### Q3: *"Apa saja faktor yang paling mempengaruhi kelulusan menurut sistem?"*
> **Jawaban Mantap**:  
> *"Berdasarkan analisis Feature Importance dari model Random Forest, faktor paling dominan adalah IPK Kumulatif semester 1–4, perolehan SKS tempuh, dan tren kenaikan/penurunan nilai semester. Faktor eksternal seperti status bekerja juga berkontribusi pada beban manajemen waktu mahasiswa."*

### Q4: *"Bagaimana jika ada mahasiswa yang nilainya sangat rendah (IPK 2.0), tapi karena dia tidak bekerja, apakah model bisa salah memprediksi dia lulus tepat waktu?"*
> **Jawaban Mantap**:  
> *"Sistem kami menggunakan pendekatan **Hybrid Decision Support System**. Selain mengandalkan probabilitas Random Forest, kami memasang **Academic Rule Guardrails**. Jika IPK mahasiswa berada di bawah standar kelulusan (< 2.50) atau tren nilainya anjlok drastis, sistem secara otomatis mengeskalasi risiko menjadi 'Terlambat / Berisiko Tinggi' demi keselamatan akademik mahasiswa."*

### Q5: *"Berapa metrik evaluasi model Anda secara lengkap?"*
> **Jawaban Mantap**:  
> *"Dari 240 sampel data uji (data baru yang belum pernah dilihat model), model kami mencatat:*  
> *- **Akurasi**: 89.17%*  
> *- **Presisi**: 87.36%*  
> *- **Recall (Sensitivitas Risiko)**: 83.52% (Mampu mendeteksi 76 dari 91 mahasiswa bermasalah)*  
> *- **ROC-AUC**: 94.23% (Kategori Sangat Istimewa / Outstanding Discrimination)*  

---

**Selamat Berpresentasi & Semoga Sukses Ujian/Sidangnya! 🚀**
