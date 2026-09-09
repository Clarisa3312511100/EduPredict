# Laporan Teknis: Evaluasi Model Machine Learning & Komparasi Algoritma

Dokumen ini disusun sebagai dokumentasi teknis independen mengenai **metodologi pemodelan, hasil pengujian eksperimental, dan analisis pemilihan algoritma** pada sistem prediksi kelulusan mahasiswa (**EduPredict**).

---

## 1. Skema Pengujian & Pembagian Data (Data Partitioning)

Eksperimen pemodelan dilakukan menggunakan data riwayat akademik sebanyak **1.500 mahasiswa** dengan sebaran label:
- **Tepat Waktu ($\le$ 8 Semester)**: 715 mahasiswa (47.7%)
- **Terlambat / Berisiko (> 8 Semester)**: 785 mahasiswa (52.3%)

### Konfigurasi Pembagian Data:
- **Metode**: *Stratified Train-Test Split*
- **Rasio**: **80% Data Latih** (1.200 sampel) dan **20% Data Uji** (300 sampel).
- **Alasan Penggunaan Stratifikasi**: Menjamin bahwa proporsi mahasiswa yang tepat waktu dan terlambat pada data latihan identik secara statistik dengan data ujian, sehingga mencegah terjadinya bias evaluasi.

---

## 2. Pipeline Pra-pemrosesan Data (Preprocessing Pipeline)

Untuk memastikan data mentah siap dikonsumsi oleh algoritma tanpa kebocoran data (*data leakage*), seluruh proses pra-pemrosesan diintegrasikan ke dalam satu arsitektur pipeline:

1. **Rekayasa Fitur (Feature Engineering)**:
   - **Gradien Tren IPS**: $\text{Tren IPS} = IPS_{\text{Sem 4}} - IPS_{\text{Sem 1}}$ (mendeteksi tren akselerasi atau penurunan prestasi akademik).
   - **Rasio SKS Gagal**: $\frac{\text{SKS Gagal}}{\text{SKS Lulus} + \text{SKS Gagal}}$ (mengukur persentase beban studi yang mengulang).
2. **StandardScaler (Fitur Kontinu / Numerik)**:
   - Diterapkan pada: `IPS_Sem1`, `IPS_Sem2`, `IPS_Sem3`, `IPS_Sem4`, `IPK_Kumulatif`, `SKS_Lulus`, `SKS_Gagal`, `Persentase_Kehadiran`, `Tren_IPS`, dan `Rasio_SKS_Gagal`.
   - Menyetarakan skala data ke rata-rata ($\mu = 0$) dan varians ($\sigma = 1$).
3. **OneHotEncoder (Fitur Kategorikal)**:
   - Diterapkan pada: `Jalur_Masuk` (SNBP, SNBT, Mandiri), `Status_Bekerja` (0/1), dan `Pernah_Cuti` (0/1).

---

## 3. Hasil Komparasi Kinerja Algoritma (Experimental Benchmark)

Pengujian dilakukan pada **300 sampel data uji yang belum pernah dilihat oleh model** selama proses pelatihan. Berikut hasil perbandingan kinerja 3 algoritma kandidat:

| Algoritma | Akurasi | Presisi | Recall (Sensitivitas Risiko) | F1-Score | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **79.33%** | **78.44%** | **83.44%** | **80.86%** | **90.93%** | 🏆 **Model Terpilih (Best)** |
| **Random Forest Classifier** | 78.00% | 76.92% | 82.80% | 79.75% | 89.11% | Baseline Ensemble |
| **Decision Tree Classifier** | 78.00% | 80.13% | 77.07% | 78.57% | 85.01% | Baseline Tree |

---

## 4. Alasan Ilmiah Pemilihan Logistic Regression

Model **Logistic Regression** secara resmi dipilih sebagai model inferensi utama pada sistem EduPredict berdasarkan pertimbangan ilmiah berikut:

### 1. Keunggulan Nilai Recall Tertinggi (83.44%)
Dalam domain **Sistem Peringatan Dini (*Early Warning System*)**, dampak kesalahan klasifikasi tidaklah seimbang:
- **False Positive**: Mahasiswa yang sebenarnya aman diprediksi berisiko. *(Dampaknya ringan: dosen PA hanya memanggil mahasiswa untuk bimbingan preventif).*
- **False Negative**: Mahasiswa yang sebenarnya **terancam terlambat/DO tetapi diprediksi aman**. *(Dampaknya fatal: kampus kehilangan kesempatan intervensi dini).*

> **Kesimpulan**: Logistic Regression memiliki tingkat *False Negative* paling rendah di antara semua model yang diuji, dengan berhasil menangkap **83.44%** mahasiswa yang benar-benar membutuhkan perhatian khusus.

### 2. Diskriminasi Probabilitas Luar Biasa (ROC-AUC 90.93%)
Skor **ROC-AUC mencapai 0.9093**. Dalam literatur statistik dan Data Science (*Hosmer & Lemeshow*), nilai AUC $\ge 0.90$ diklasifikasikan sebagai **"Outstanding / Excellent Discrimination"**, membuktikan bahwa model mampu mengurutkan tingkat keparahan risiko mahasiswa dengan tingkat kepastian yang sangat tinggi.

### 3. Efisiensi Komputasi & Inferensi Real-Time
Logistic Regression memiliki bobot komputasi linear yang sangat ringan (ukuran file model hanya $\approx 3$ KB), dengan waktu respon inferensi di bawah **5 milidetik**, memungkinkan sistem melayani ratusan prediksi mahasiswa per detik tanpa membebani server kampus.

---

## 5. Analisis Bobot Pengaruh Indikator (Feature Importance)

Berdasarkan bobot koefisien absolut ($|w_i|$) pada model terbaik, berikut urutan faktor yang paling dominan mempengaruhi potensi keterlambatan kelulusan:

```
URUTAN FAKTOR PENENTU KELULUSAN MAHASISWA:
1. Riwayat Pernah Mengambil Cuti Akademik  (Bobot: 0.224) ─── Kritis
2. Jumlah SKS Gagal / Mengulang (D-E)       (Bobot: 0.198) ─── Kritis
3. Penurunan Tren Nilai (IPS 1 ke 4)       (Bobot: 0.175) ─── Tinggi
4. IPK Kumulatif Akhir Semester 4          (Bobot: 0.152) ─── Tinggi
5. Rata-rata Persentase Kehadiran Kuliah   (Bobot: 0.121) ─── Sedang
6. Status Mahasiswa Kuliah Sambil Kerja    (Bobot: 0.086) ─── Sedang
7. Jalur Masuk Perguruan Tinggi            (Bobot: 0.044) ─── Rendah
```

> **Wawasan Akademik**:  
> Mahasiswa yang pernah cuti akademik dan memiliki lebih dari 4 SKS mengulang memiliki probabilitas keterlambatan lebih dari 75%, meskipun IPK mereka berada di batas rata-rata.

---

## 6. Panduan Tanya-Jawab Sidang / Evaluasi Dosen (FAQ)

Gunakan argumen berikut jika dosen penguji menanyakan aspek teknis model:

### Q1: *"Kenapa tidak memakai Deep Learning / Jaringan Saraf Tiruan (Neural Network)?"*
> **Jawaban**:  
> *"Untuk data tabular terstruktur dengan 1.500 sampel dan belasan fitur akademik, algoritma Deep Learning memiliki risiko over-parameterization dan overfitting yang tinggi. Model linier probabilistik seperti Logistic Regression terbukti memberikan generalisasi yang lebih stabil, transparan, dan tidak memerlukan resource komputasi besar."*

### Q2: *"Kenapa Logistic Regression bisa mengalahkan Random Forest?"*
> **Jawaban**:  
> *"Data akademik memiliki relasi probabilitas yang konsisten dan monotonik (misalnya: semakin tinggi SKS gagal, risiko keterlambatan naik secara teratur). Pada karakteristik data seperti ini, fungsi logit linear sering kali mampu menangkap batas keputusan secara lebih optimal dibandingkan ensemble pohon yang memotong ruang fitur secara orthogonal."*

### Q3: *"Kenapa mengutamakan metrik Recall daripada Akurasi?"*
> **Jawaban**:  
> *"Karena fokus utama sistem ini adalah mitigasi risiko. Akurasi tinggi tidak ada artinya jika banyak mahasiswa berisiko yang terlewat (False Negative tinggi). Recall yang tinggi menjamin bahwa hampir seluruh mahasiswa bermasalah berhasil terdeteksi sedini mungkin."*
