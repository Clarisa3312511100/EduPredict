# Laporan Teknis: Evaluasi Model Machine Learning & Komparasi Algoritma

Dokumen ini disusun sebagai dokumentasi teknis independen mengenai **metodologi pemodelan, augmentasi data berbasis data riil, hasil pengujian eksperimental, dan analisis pemilihan algoritma** pada sistem prediksi kelulusan mahasiswa (**EduPredict**).

---

## 1. Skema Pengujian & Pembagian Data (Data Partitioning)

Eksperimen pemodelan dilakukan menggunakan **1.200 sampel data mahasiswa** yang dikembangkan melalui metode **Empirical Data Augmentation** berbasis **379 data riil rekam akademik mahasiswa perguruan tinggi Indonesia**.

### Sebaran Label Dataset:
- **Tepat Waktu ($\le$ 8 Semester)**: 747 mahasiswa (62.3%)
- **Terlambat / Berisiko (> 8 Semester)**: 453 mahasiswa (37.7%)

### Konfigurasi Pembagian Data:
- **Metode**: *Stratified Train-Test Split*
- **Rasio**: **80% Data Latih** (960 sampel) dan **20% Data Uji** (240 sampel).
- **Alasan Penggunaan Stratifikasi**: Menjamin bahwa proporsi mahasiswa yang tepat waktu dan terlambat pada data latihan identik secara statistik dengan data ujian, sehingga mencegah terjadinya bias evaluasi.
- **Random State**: `42` (menjamin eksperimen dapat direproduksi secara persis / *reproducible*).

---

## 2. Metodologi Augmentasi Data Berbasis Data Riil (*Empirical Data Augmentation*)

Untuk menghindari kelemahan data sintetis murni dan keterbatasan ukuran sampel tunggal, proyek ini menerapkan metode ilmiah **Data Augmentation**:
1. **Benih Utama (Seed Data)**: Menggunakan 379 data riil rekam jejak akademik mahasiswa Indonesia yang memuat nilai IPS semester 1 s.d 4, IPK kumulatif, profil pekerjaan, dan status kelulusan.
2. **Ekspansi Statistik**: Mengembangkan populasi hingga 1.200 sampel dengan menjaga kovarians antarvariabel dan distribusi probabilitas alami.
3. **Koreksi Bias**: Menambahkan variasi mahasiswa yang bekerja namun memiliki determinasi belajar tinggi, serta mahasiswa reguler yang mengalami penurunan nilai (*academic decline*), sehingga model terlatih secara adil (*fair & unbiased*).

---

## 3. Hasil Komparasi Kinerja Algoritma (Experimental Benchmark)

Pengujian dilakukan pada **240 sampel data uji yang belum pernah dilihat oleh model** selama proses pelatihan. Berikut hasil perbandingan kinerja 3 algoritma kandidat:

| Algoritma | Akurasi | Presisi | Recall (Sensitivitas Risiko) | F1-Score | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Classifier** | **89.17%** | **87.36%** | **83.52%** | **85.39%** | **94.23%** | 🏆 **Model Terpilih (Best)** |
| **Decision Tree Classifier** | 87.08% | 84.09% | 81.32% | 82.68% | 90.57% | Tree Baseline |
| **Logistic Regression** | 85.00% | 83.95% | 74.73% | 79.07% | 93.24% | Linear Baseline |

---

## 4. Alasan Ilmiah Pemilihan Random Forest (Ensemble Learning)

Model **Random Forest Classifier** (dengan konfigurasi `n_estimators=100`, `max_depth=6`, `class_weight='balanced'`) secara resmi dipilih sebagai model inferensi utama pada sistem EduPredict berdasarkan pertimbangan ilmiah berikut:

### 1. Keseimbangan Terbaik Akurasi & F1-Score (89.17% & 85.39%)
Random Forest mengungguli Decision Tree tunggal karena menggunakan mekanisme agregasi *Bagging (Bootstrap Aggregating)* dengan ratusan pohon keputusan independen. Hal ini mereduksi varians (*variance reduction*) dan mencegah keputusan ekstrem (0% atau 100%) yang sering terjadi pada pohon tunggal.

### 2. Sensitivitas Peringatan Dini Tinggi (Recall 83.52%)
Dalam domain **Sistem Peringatan Dini (*Early Warning System*)**, metrik recall untuk mendeteksi mahasiswa yang terlambat sangat krusial:
- Model berhasil menangkap **76 dari 91 mahasiswa berisiko** pada data uji.
- Mengurangi risiko *False Negative* (mahasiswa bermasalah yang terlewat dari pengawasan dosen PA).

### 3. Diskriminasi Luar Biasa (ROC-AUC 94.23%)
Skor **ROC-AUC mencapai 0.9423**. Berdasarkan standar literatur statistik dan Data Science (*Hosmer & Lemeshow*), nilai AUC $\ge 0.90$ diklasifikasikan sebagai **"Outstanding / Excellent Discrimination"**, membuktikan ketajaman model dalam membedakan mahasiswa berisiko tinggi dan mahasiswa aman.

### 4. Dilengkapi Academic Guardrails (Hybrid AI)
Untuk menjamin tidak ada celah di mana mahasiswa dengan IPK kritis (< 2.50) lolos dari deteksi hanya karena faktor eksternal, sistem mengintegrasikan **Academic Rule Guardrails**:
- IPK di bawah standar kelulusan (< 2.75 dan < 2.50) langsung mengeskalasi tingkat risiko.
- Penurunan tren nilai IPS semester 1 ke 4 ($<-0.80$) memicu sinyal intervensi.

---

## 5. Panduan Tanya-Jawab Sidang / Evaluasi Dosen (FAQ)

Gunakan argumen berikut jika dosen penguji menanyakan aspek teknis pemodelan:

### Q1: *"Bagaimana metodologi perolehan dataset 1.200 sampel ini?"*
> **Jawaban**:  
> *"Dataset ini dikembangkan melalui teknik **Empirical Data Augmentation** berbasis **379 data riil rekam akademik mahasiswa perguruan tinggi di Indonesia**. Teknik augmentasi statistik diterapkan untuk memperluas sampel dari 379 menjadi 1.200 mahasiswa guna merepresentasikan populasi satu fakultas secara proporsional dan melatih model pada variasi kasus akademik yang lebih kaya."*

### Q2: *"Mengapa Random Forest lebih unggul dibanding Decision Tree tunggal?"*
> **Jawaban**:  
> *"Decision Tree tunggal rentan mengalami bias lokal (*shortcut rule*) dan varians tinggi. Random Forest memadukan 100 pohon keputusan secara *ensemble*, sehingga probabilitas yang dihasilkan lebih halus (*calibrated probability*), generalisasinya lebih stabil, dan F1-Score-nya mencapai 85.39%."*

### Q3: *"Bagaimana sistem menangani mahasiswa yang IPK-nya rendah tapi tidak bekerja?"*
> **Jawaban**:  
> *"Sistem kami mengadopsi arsitektur **Hybrid Decision Support System**. Selain mengandalkan probabilitas Random Forest, sistem memiliki aturan batas (*academic guardrails*) berbasis standar kelulusan Dikti. Jika IPK kumulatif berada di bawah 2.50 atau tren nilai anjlok tajam, sistem secara otomatis mengeskalasi risiko keterlambatan menjadi Berisiko Sedang/Tinggi."*
