import os
import random
import numpy as np
import pandas as pd

# Set seed agar hasil augmentasi konsisten (reproducible)
np.random.seed(42)
random.seed(42)

def generate_augmented_dataset(target_total=1200):
    print(f"=== Memulai Data Augmentation (Target: {target_total} Mahasiswa) ===")
    
    # 1. Baca data riil yang sudah ada sebagai basis / seed
    base_csv = "data/dataset_kelulusan.csv"
    if not os.path.exists(base_csv):
        raise FileNotFoundError(f"File dasar {base_csv} tidak ditemukan.")
    
    df_base = pd.read_csv(base_csv)
    n_real = len(df_base)
    print(f"Berhasil memuat {n_real} sampel data riil mahasiswa sebagai benih dasar.")
    
    n_synthetic = target_total - n_real
    if n_synthetic <= 0:
        print("Jumlah data sudah mencukupi target.")
        return df_base

    # Daftar nama khas Indonesia untuk data variasi
    first_names_male = [
        "Ahmad", "Budi", "Bayu", "Dimas", "Eko", "Fajar", "Gilang", "Hafiz",
        "Ilham", "Joko", "Kevin", "Lukman", "Muhammad", "Naufal", "Prasetyo",
        "Rian", "Rizky", "Satria", "Taufik", "Wahyu", "Yoga", "Zulfikar",
        "Bambang", "Danu", "Fikri", "Guntur", "Haris", "Irfan", "Kurniawan", "Reza"
    ]
    first_names_female = [
        "Annisa", "Aulia", "Bella", "Citra", "Dewi", "Dinda", "Fadilah", "Gita",
        "Intan", "Lestari", "Maya", "Nabila", "Nur", "Putri", "Rahma", "Rina",
        "Sari", "Siti", "Tiara", "Wulandari", "Yulia", "Zahra", "Indah", "Novita"
    ]
    last_names = [
        "Pratama", "Saputra", "Wijaya", "Kusuma", "Utomo", "Santoso", "Hidayat",
        "Nugroho", "Wibowo", "Setiawan", "Lestari", "Permana", "Kurniawan", "Suryono",
        "Firmansyah", "Ramadhan", "Purnama", "Siregar", "Nasution", "Tanjung", "Mahendra"
    ]

    new_rows = []
    start_nim = 20180000 + n_real + 1

    for i in range(n_synthetic):
        nim = str(start_nim + i)
        gender = np.random.choice(["Laki-laki", "Perempuan"], p=[0.55, 0.45])
        if gender == "Laki-laki":
            nama = f"{random.choice(first_names_male)} {random.choice(last_names)}"
        else:
            nama = f"{random.choice(first_names_female)} {random.choice(last_names)}"

        # Status demografis (mengikuti proporsi realistis mahasiswa)
        status_bekerja = int(np.random.choice([0, 1], p=[0.68, 0.32]))
        status_nikah = int(np.random.choice([0, 1], p=[0.88, 0.12])) if status_bekerja == 1 else int(np.random.choice([0, 1], p=[0.97, 0.03]))
        umur = int(np.random.choice([20, 21, 22, 23, 24, 25, 26, 27, 28], p=[0.05, 0.20, 0.35, 0.20, 0.10, 0.05, 0.03, 0.01, 0.01]))

        # Pola performa akademik mahasiswa
        # 1. Mahasiswa unggul / rajin (35%)
        # 2. Mahasiswa rata-rata / moderat (40%)
        # 3. Mahasiswa berisiko / berjuang (25%)
        tier = np.random.choice(["unggul", "moderat", "kritis"], p=[0.38, 0.38, 0.24])

        if tier == "unggul":
            ips1 = round(np.random.uniform(3.25, 3.95), 2)
            ips2 = round(np.clip(ips1 + np.random.normal(0.05, 0.12), 3.0, 4.0), 2)
            ips3 = round(np.clip(ips2 + np.random.normal(0.02, 0.12), 3.0, 4.0), 2)
            ips4 = round(np.clip(ips3 + np.random.normal(0.02, 0.12), 3.0, 4.0), 2)
        elif tier == "moderat":
            ips1 = round(np.random.uniform(2.70, 3.35), 2)
            ips2 = round(np.clip(ips1 + np.random.normal(0.00, 0.20), 2.4, 3.6), 2)
            ips3 = round(np.clip(ips2 + np.random.normal(-0.02, 0.20), 2.2, 3.7), 2)
            ips4 = round(np.clip(ips3 + np.random.normal(0.00, 0.20), 2.2, 3.7), 2)
        else:  # kritis
            ips1 = round(np.random.uniform(2.20, 2.90), 2)
            ips2 = round(np.clip(ips1 + np.random.normal(-0.15, 0.22), 1.6, 2.8), 2)
            ips3 = round(np.clip(ips2 + np.random.normal(-0.10, 0.22), 1.5, 2.7), 2)
            ips4 = round(np.clip(ips3 + np.random.normal(-0.10, 0.25), 1.4, 2.6), 2)

        ipk = round((ips1 + ips2 + ips3 + ips4) / 4.0, 2)
        tren_ips = round(ips4 - ips1, 2)

        # Penentuan Status Kelulusan yang logis dan konsisten secara akademik:
        # Menghitung skor penentu kelulusan
        skor_kelulusan = 0.0

        # Bobot IPK
        if ipk >= 3.50:
            skor_kelulusan += 4.5
        elif ipk >= 3.00:
            skor_kelulusan += 3.0
        elif ipk >= 2.75:
            skor_kelulusan += 1.0
        elif ipk >= 2.50:
            skor_kelulusan -= 1.5
        elif ipk >= 2.00:
            skor_kelulusan -= 3.5
        else:
            skor_kelulusan -= 5.5

        # Bobot Tren Nilai
        if tren_ips > 0.30:
            skor_kelulusan += 1.5
        elif tren_ips < -0.60:
            skor_kelulusan -= 2.5
        elif tren_ips < -0.30:
            skor_kelulusan -= 1.0

        # Bobot Status Bekerja & Menikah
        if status_bekerja == 1:
            skor_kelulusan -= 1.8
        if status_nikah == 1:
            skor_kelulusan -= 1.2
        if umur >= 26:
            skor_kelulusan -= 1.0

        # Klasifikasi probabilitas probabilistik realistis (Logistic sigmoid)
        prob_tepat = 1.0 / (1.0 + np.exp(-skor_kelulusan))
        status_kelulusan = "Tepat Waktu" if np.random.rand() < prob_tepat else "Terlambat"

        new_rows.append({
            "NIM": nim,
            "Nama": nama,
            "Jenis_Kelamin": gender,
            "Umur": umur,
            "Status_Bekerja": status_bekerja,
            "Status_Nikah": status_nikah,
            "IPS_Sem1": ips1,
            "IPS_Sem2": ips2,
            "IPS_Sem3": ips3,
            "IPS_Sem4": ips4,
            "IPK_Kumulatif": ipk,
            "Status_Kelulusan": status_kelulusan
        })

    df_augmented = pd.DataFrame(new_rows)
    df_final = pd.concat([df_base, df_augmented], ignore_index=True)

    # Simpan kembali ke file dataset_kelulusan.csv
    df_final.to_csv(base_csv, index=False)
    
    print(f"Data Augmentation Sukses! Total dataset sekarang: {len(df_final)} baris.")
    print(f"Sebaran Status Kelulusan:\n{df_final['Status_Kelulusan'].value_counts()}")
    return df_final

if __name__ == "__main__":
    generate_augmented_dataset(1200)
