import os
import numpy as np
import pandas as pd

def generate_student_dataset(n_samples=1500, random_seed=42):
    """
    Menghasilkan dataset akademik mahasiswa sintetis yang realistis.
    Logika penentuan status kelulusan didasarkan pada aturan akademik nyata:
    - Mahasiswa dengan IPK tinggi dan sedikit SKS gagal cenderung lulus tepat waktu.
    - Faktor pemicu keterlambatan: penurunan IPS drastis, SKS mengulang banyak, pernah cuti, bekerja.
    """
    np.random.seed(random_seed)

    # 1. Identitas & Demografi
    nim_list = [f"2021{str(i).zfill(5)}" for i in range(1, n_samples + 1)]
    
    first_names_male = ["Budi", "Dimas", "Rizky", "Aditya", "Fajar", "Bagus", "Ilham", "Bayu", "Eko", "Satria", "Wahyu", "Rafi", "Farhan", "Yoga"]
    first_names_female = ["Siti", "Nurul", "Putri", "Dwi", "Rina", "Anisa", "Aulia", "Dewi", "Fitri", "Tiara", "Nabila", "Zahra", "Maya"]
    last_names = ["Pratama", "Saputra", "Santoso", "Hidayat", "Wijaya", "Kusuma", "Setiawan", "Utomo", "Nugroho", "Wibowo", "Permana", "Hakim"]
    
    gender_choices = np.random.choice(["Laki-laki", "Perempuan"], size=n_samples, p=[0.55, 0.45])
    names = []
    for g in gender_choices:
        if g == "Laki-laki":
            names.append(f"{np.random.choice(first_names_male)} {np.random.choice(last_names)}")
        else:
            names.append(f"{np.random.choice(first_names_female)} {np.random.choice(last_names)}")

    # 2. Jalur Masuk (SNBP = 30%, SNBT = 40%, Mandiri = 30%)
    jalur_masuk = np.random.choice(["SNBP", "SNBT", "Mandiri"], size=n_samples, p=[0.30, 0.40, 0.30])

    # 3. Status Bekerja & Riwayat Cuti
    status_bekerja = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
    pernah_cuti = np.random.choice([0, 1], size=n_samples, p=[0.90, 0.10])

    # 4. Nilai IPS Semester 1 - 4
    # Nilai dasar dengan variasi kemampuan mahasiswa
    base_ability = np.random.normal(loc=3.10, scale=0.45, size=n_samples)
    base_ability = np.clip(base_ability, 1.50, 3.95)

    ips_sem1 = np.clip(base_ability + np.random.normal(0, 0.20, size=n_samples), 1.50, 4.00)
    ips_sem2 = np.clip(base_ability + np.random.normal(0, 0.22, size=n_samples), 1.40, 4.00)
    
    # Penurunan performa lebih mungkin pada mahasiswa bekerja / cuti
    drop_sem3 = np.where(status_bekerja == 1, np.random.uniform(0.1, 0.4, size=n_samples), 0)
    ips_sem3 = np.clip(base_ability - drop_sem3 + np.random.normal(0, 0.25, size=n_samples), 1.20, 4.00)
    
    drop_sem4 = np.where(status_bekerja == 1, np.random.uniform(0.1, 0.4, size=n_samples), 0)
    ips_sem4 = np.clip(base_ability - drop_sem4 + np.random.normal(0, 0.25, size=n_samples), 1.10, 4.00)

    # Bulatkan ke 2 desimal
    ips_sem1 = np.round(ips_sem1, 2)
    ips_sem2 = np.round(ips_sem2, 2)
    ips_sem3 = np.round(ips_sem3, 2)
    ips_sem4 = np.round(ips_sem4, 2)

    # IPK Kumulatif (rata-rata 4 semester)
    ipk_kumulatif = np.round((ips_sem1 + ips_sem2 + ips_sem3 + ips_sem4) / 4.0, 2)

    # 5. SKS Lulus & SKS Gagal
    # Normal perkuliahan semester 4 = ~80 - 88 SKS
    total_sks_diambil = np.random.choice([80, 84, 86, 88], size=n_samples, p=[0.15, 0.35, 0.35, 0.15])
    
    # SKS gagal berkorelasi terbalik dengan IPK
    sks_gagal_base = np.maximum(0, (3.30 - ipk_kumulatif) * 8 + np.random.normal(0, 2.5, size=n_samples))
    sks_gagal = np.round(sks_gagal_base).astype(int)
    sks_gagal = np.clip(sks_gagal, 0, 24)

    sks_lulus = total_sks_diambil - sks_gagal
    sks_lulus = np.clip(sks_lulus, 55, total_sks_diambil)

    # 6. Kehadiran Kuliah (%)
    kehadiran_base = 72.0 + (ipk_kumulatif / 4.0) * 25.0 - (status_bekerja * 6.0) + np.random.normal(0, 3.5, size=n_samples)
    persentase_kehadiran = np.round(np.clip(kehadiran_base, 60.0, 100.0), 1)

    # 7. Penentuan Label Kelulusan Logis
    # Formula Skor Risiko (Logit):
    # Faktor positif: IPK tinggi, SKS lulus banyak, kehadiran tinggi
    # Faktor negatif: SKS gagal banyak, pernah cuti, bekerja, tren IPS menurun
    tren_ips = ips_sem4 - ips_sem1

    risk_score = (
        (3.00 - ipk_kumulatif) * 2.6 +
        (sks_gagal / 6.0) * 1.8 +
        (1.0 - (persentase_kehadiran / 100.0)) * 2.2 +
        (pernah_cuti * 2.0) +
        (status_bekerja * 0.8) -
        (tren_ips * 1.2) -
        0.9
    )

    # Probabilitas terlambat menggunakan fungsi sigmoid
    prob_terlambat = 1.0 / (1.0 + np.exp(-risk_score))
    
    # Label kelulusan (1 = Terlambat, 0 = Tepat Waktu)
    is_terlambat = (np.random.rand(n_samples) < prob_terlambat).astype(int)
    status_kelulusan = np.where(is_terlambat == 1, "Terlambat", "Tepat Waktu")

    # Susun ke DataFrame
    df = pd.DataFrame({
        "NIM": nim_list,
        "Nama": names,
        "Jenis_Kelamin": gender_choices,
        "Jalur_Masuk": jalur_masuk,
        "IPS_Sem1": ips_sem1,
        "IPS_Sem2": ips_sem2,
        "IPS_Sem3": ips_sem3,
        "IPS_Sem4": ips_sem4,
        "IPK_Kumulatif": ipk_kumulatif,
        "SKS_Lulus": sks_lulus,
        "SKS_Gagal": sks_gagal,
        "Persentase_Kehadiran": persentase_kehadiran,
        "Status_Bekerja": status_bekerja,
        "Pernah_Cuti": pernah_cuti,
        "Status_Kelulusan": status_kelulusan
    })

    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "dataset_kelulusan.csv")
    
    print("Membuat dataset sintetis akademik mahasiswa...")
    df = generate_student_dataset(n_samples=1500)
    df.to_csv(output_path, index=False)
    
    print(f"Dataset berhasil dibuat dan disimpan di: {output_path}")
    print(f"Total baris data: {len(df)}")
    print("\nDistribusi Status Kelulusan:")
    print(df["Status_Kelulusan"].value_counts(normalize=True).round(3) * 100)
    print("\nSampel 5 data teratas:")
    print(df.head())
