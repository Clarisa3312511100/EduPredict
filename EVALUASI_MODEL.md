# Laporan Teknis: Evaluasi Model Machine Learning & Komparasi Algoritma

Dokumen ini disusun sebagai dokumentasi teknis independen mengenai **metodologi pemodelan, hasil pengujian eksperimental, dan analisis pemilihan algoritma** pada sistem prediksi kelulusan mahasiswa (**EduPredict**) menggunakan **Dataset Riil Mahasiswa Perguruan Tinggi Indonesia**.

---

## 1. Skema Pengujian & Pembagian Data (Data Partitioning)

Eksperimen pemodelan dilakukan menggunakan data riil riwayat akademik mahasiswa sebanyak **379 mahasiswa** dengan sebaran label:
- **Tepat Waktu ($\le$ 8 Semester)**: 216 mahasiswa (57.0%)
- **Terlambat / Berisiko (> 8 Semester)**: 163 mahasiswa (43.0%)

### Konfigurasi Pembagian Data:
- **Metode**: *Stratified Train-Test Split*
- **Rasio**: **80% Data Latih** (303 sampel) dan **20% Data Uji** (76 sampel).
- **Alasan Penggunaan Stratifikasi**: Menjamin bahwa proporsi mahasiswa yang tepat waktu dan terlambat pada data latihan identik secara statistik dengan data ujian, sehingga mencegah terjadinya bias evaluasi.
- **Random State**: `42` (menjamin eksperimen dapat direproduksi secara persis / *reproducible*).

---

## 2. Pipeline Pra-pemrosesan Data (Preprocessing Pipeline)

Untuk memastikan data mentah siap dikonsumsi oleh algoritma tanpa kebocoran data (*data leakage*), seluruh proses pra-pemrosesan diintegrasikan ke dalam satu arsitektur pipeline Scikit-Learn:

1. **Rekayasa Fitur (Feature Engineering)**:
   - **Gradien Tren IPS**: $\text{Tren IPS} = IPS_{\text{Sem 4}} - IPS_{\text{Sem 1}}$ (mendeteksi akselerasi atau kemerosotan performa belajar).
   - **IPK Kumulatif**: Rata-rata tertimbang nilai semester 1 hingga semester 4.
2. **StandardScaler (Fitur Kontinu / Numerik)**:
   - Diterapkan pada: `IPS_Sem1`, `IPS_Sem2`, `IPS_Sem3`, `IPS_Sem4`, `IPK_Kumulatif`, `Umur`, dan `Tren_IPS`.
   - Menyetarakan skala data ke rata-rata ($\mu = 0$) dan varians unit ($\sigma = 1$).
3. **OneHotEncoder (Fitur Kategorikal / Biner)**:
   - Diterapkan pada: `Jenis_Kelamin` (Laki-laki, Perempuan), `Status_Bekerja` (0/1), dan `Status_Nikah` (0/1).

---

## 3. Hasil Komparasi Kinerja Algoritma (Experimental Benchmark)

Pengujian dilakukan pada **76 sampel data uji riil yang belum pernah dilihat oleh model** selama proses pelatihan. Berikut hasil perbandingan kinerja 3 algoritma kandidat:

| Algoritma | Akurasi | Presisi | Recall (Sensitivitas Risiko) | F1-Score | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Decision Tree Classifier** | **92.11%** | **96.55%** | **84.85%** | **90.32%** | **95.10%** | 🏆 **Model Terpilih (Best)** |
| **Random Forest Classifier** | 89.47% | 90.32% | 84.85% | 87.50% | 97.11% | Ensemble Baseline |
| **Logistic Regression** | 86.84% | 84.85% | 84.85% | 84.85% | 94.15% | Linear Baseline |

---

## 4. Alasan Ilmiah Pemilihan Decision Tree (Akurasi 92.11%)

Model **Decision Tree Classifier** (dengan konfigurasi `max_depth=5` dan `min_samples_split=6` untuk mencegah overfitting) secara resmi dipilih sebagai model inferensi utama pada sistem EduPredict berdasarkan pertimbangan ilmiah berikut:

### 1. Akurasi & Presisi Tertinggi (92.11% & 96.55%)
- Dari 76 mahasiswa pada data uji, Decision Tree berhasil mengklasifikasikan **70 mahasiswa secara tepat** (hanya 1 false alarm / false positive dari 43 mahasiswa yang tepat waktu).
- Presisi sebesar **96.55%** membuktikan bahwa ketika model mendiagnosis seorang mahasiswa berstatus terlambat, probabilitas kebenarannya mencapai lebih dari 96%.

### 2. Sensitivitas Risiko Tinggi (Recall 84.85%)
Dalam domain **Sistem Peringatan Dini (*Early Warning System*)**, metrik recall untuk mendeteksi mahasiswa yang terlambat sangat krusial:
- Model berhasil menangkap **28 dari 33 mahasiswa** yang terbukti terlambat pada data uji riil.
- Nilai False Negative ditekan seminimal mungkin (hanya 5 kasus), sehingga dosen PA memiliki kepastian tinggi dalam memberikan bimbingan intervensi.

### 3. Diskriminasi Luar Biasa (ROC-AUC 95.10%)
Skor **ROC-AUC mencapai 0.9510**. Berdasarkan standar literatur statistik dan Data Science (*Hosmer & Lemeshow*), nilai AUC $\ge 0.90$ diklasifikasikan sebagai **"Outstanding / Excellent Discrimination"**, membuktikan ketajaman model dalam membedakan mahasiswa berisiko tinggi dan aman.

### 4. Transparansi & *Explainability* yang Tinggi (White-box Model)
Berbeda dengan model ensemble kompleks yang bersifat *black-box*, struktur pohon keputusan pada Decision Tree memungkinkan setiap aturan pemisahan (*if-else splits*) diverifikasi secara logis dan transparan oleh dosen akademik, tim kurikulum, maupun penguji sidang.

---

## 5. Analisis Bobot Pengaruh Indikator (Feature Importance)

Berdasarkan nilai *Gini Feature Importance* pada model Decision Tree terbaik:

```
URUTAN FAKTOR PENENTU KELULUSAN MAHASISWA:
1. Status Mahasiswa Kuliah Sambil Bekerja (73.4%) ─── Kritis
2. Faktor Usia Mahasiswa                 (7.1%)  ─── Signifikan
3. Indeks Prestasi Semester 2 (IPS 2)    (7.1%)  ─── Signifikan
4. Indeks Prestasi Semester 4 (IPS 4)    (7.0%)  ─── Signifikan
5. Indeks Prestasi Semester 1 (IPS 1)    (3.2%)  ─── Moderat
6. Indeks Prestasi Semester 3 (IPS 3)    (2.4%)  ─── Moderat
```

> **Wawasan Akademik**:  
> Status bekerja dan stabilitas nilai pada semester 2 dan 4 merupakan prediktor paling menentukan. Mahasiswa yang bekerja memiliki tantangan membagi waktu antara pekerjaan dan tugas akhir/praktikum, sehingga memerlukan pendampingan akademik yang lebih proaktif dari Dosen Pembimbing Akademik (PA).

---

## 6. Panduan Tanya-Jawab Sidang / Evaluasi Dosen (FAQ)

Gunakan argumen berikut jika dosen penguji menanyakan aspek teknis pemodelan:

### Q1: *"Dari mana dataset ini diperoleh dan mengapa jumlahnya 379 sampel?"*
> **Jawaban**:  
> *"Dataset ini bersumber dari data publik riil rekam akademik kelulusan mahasiswa Indonesia (juga tersedia di Kaggle & repositori riset akademik). Jumlah 379 data riil ini sangat representatif untuk menguji ketepatan algoritma klasifikasi pada konteks perkuliahan di Indonesia, berbeda dengan data tiruan buatan yang rentan bias artifisial."*

### Q2: *"Mengapa Decision Tree dipilih dibanding Random Forest yang ROC-AUC nya sedikit lebih tinggi (97.11% vs 95.10%)?"*
> **Jawaban**:  
> *"Decision Tree memberikan Akurasi (92.11% vs 89.47%) dan Presisi (96.55% vs 90.32%) yang lebih unggul pada data uji dengan Recall yang sama persis (84.85%). Selain itu, Decision Tree bersifat transparan (white-box model), sehingga keputusan klasifikasinya dapat diuraikan secara logis kepada dosen PA tanpa hambatan komputasi ensemble."*

### Q3: *"Bagaimana cara mencegah terjadinya Overfitting pada Decision Tree?"*
> **Jawaban**:  
> *"Kami menerapkan regularisasi pohon berupa pembatasan kedalaman maksimum (`max_depth=5`) dan jumlah sampel minimum per percabangan (`min_samples_split=6`), serta evaluasi ketat menggunakan Stratified Holdout Test Set."*
