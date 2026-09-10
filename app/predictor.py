import os
import json
import numpy as np
import pandas as pd
import joblib

class StudentGraduationPredictor:
    def __init__(self, model_path="models/best_model.joblib", metrics_path="models/metrics_summary.json", stats_path="models/dataset_stats.json"):
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.stats_path = stats_path
        self.model = None
        self.metrics = None
        self.stats = None
        self.load_artifacts()

    def load_artifacts(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, "r") as f:
                self.metrics = json.load(f)
        if os.path.exists(self.stats_path):
            with open(self.stats_path, "r") as f:
                self.stats = json.load(f)

    def is_ready(self):
        return self.model is not None

    def predict_single(self, student_data: dict) -> dict:
        """
        student_data key:
        - IPS_Sem1, IPS_Sem2, IPS_Sem3, IPS_Sem4
        - IPK_Kumulatif (opsional, jika kosong dihitung otomatis dari rata-rata IPS)
        - Umur (integer, default: 23)
        - Jenis_Kelamin ('Laki-laki', 'Perempuan')
        - Status_Bekerja (0/1)
        - Status_Nikah (0/1)
        """
        if not self.is_ready():
            raise RuntimeError("Model belum dilatih atau file model tidak ditemukan.")

        ips1 = float(student_data["IPS_Sem1"])
        ips2 = float(student_data["IPS_Sem2"])
        ips3 = float(student_data["IPS_Sem3"])
        ips4 = float(student_data["IPS_Sem4"])
        
        ipk_kumulatif = float(student_data.get("IPK_Kumulatif") or round((ips1 + ips2 + ips3 + ips4) / 4.0, 2))
        tren_ips = round(ips4 - ips1, 2)
        umur = int(student_data.get("Umur", 23))
        
        jenis_kelamin = str(student_data.get("Jenis_Kelamin", "Laki-laki"))
        status_bekerja = int(student_data.get("Status_Bekerja", 0))
        status_nikah = int(student_data.get("Status_Nikah", 0))

        # Bentuk DataFrame satu baris sesuai skema pipeline model
        df_input = pd.DataFrame([{
            "IPS_Sem1": ips1,
            "IPS_Sem2": ips2,
            "IPS_Sem3": ips3,
            "IPS_Sem4": ips4,
            "IPK_Kumulatif": ipk_kumulatif,
            "Umur": umur,
            "Tren_IPS": tren_ips,
            "Jenis_Kelamin": jenis_kelamin,
            "Status_Bekerja": status_bekerja,
            "Status_Nikah": status_nikah
        }])

        # Prediksi probabilitas keterlambatan (kelas 1)
        probabilities = self.model.predict_proba(df_input)[0]
        prob_tepat = round(float(probabilities[0]) * 100, 1)
        prob_terlambat = round(float(probabilities[1]) * 100, 1)

        # Klasifikasi status dan tingkat risiko
        if prob_terlambat >= 60.0:
            status = "Terlambat"
            tingkat_risiko = "Tinggi"
            status_color = "danger"
        elif prob_terlambat >= 35.0:
            status = "Berisiko Sedang"
            tingkat_risiko = "Sedang"
            status_color = "warning"
        else:
            status = "Tepat Waktu"
            tingkat_risiko = "Rendah"
            status_color = "success"

        # Analisis faktor pemicu / peringatan dini
        risk_factors = []
        positive_factors = []

        if ipk_kumulatif < 2.75:
            risk_factors.append(f"IPK Kumulatif di bawah batas standar kelulusan ({ipk_kumulatif:.2f} < 2.75)")
        else:
            positive_factors.append(f"IPK Kumulatif kompetitif ({ipk_kumulatif:.2f})")

        if tren_ips < -0.30:
            risk_factors.append(f"Tren performa akademik menurun drastis dari semester 1 ke 4 ({tren_ips:+.2f})")
        elif tren_ips > 0.20:
            positive_factors.append(f"Tren performa akademik meningkat positif ({tren_ips:+.2f})")

        if ips4 < 2.50:
            risk_factors.append(f"IPS Semester 4 berada pada level kritis ({ips4:.2f})")

        if status_bekerja == 1:
            risk_factors.append("Status bekerja membagi alokasi waktu belajar dan pengerjaan tugas kuliah")

        if status_nikah == 1:
            risk_factors.append("Tanggung jawab keluarga berpotensi mempengaruhi fokus studi perkuliahan")

        if umur >= 26:
            risk_factors.append(f"Faktor usia ({umur} tahun) berkorelasi dengan potensi hambatan penyelesaian skripsi")

        # Rekomendasi tindakan dosen PA
        if tingkat_risiko == "Tinggi":
            rekomendasi = "Perlu pemanggilan segera oleh Dosen PA. Evaluasi kendala belajar mahasiswa dan susun target perbaikan nilai di Semester 5."
        elif tingkat_risiko == "Sedang":
            rekomendasi = "Berikan monitoring berkala. Pastikan fokus belajar terjaga terutama jika mahasiswa memiliki aktivitas kerja paruh waktu."
        else:
            rekomendasi = "Performa akademik sangat baik dan stabil. Mahasiswa berada pada jalur optimal untuk lulus tepat waktu $\\le$ 8 semester."

        return {
            "status": status,
            "tingkat_risiko": tingkat_risiko,
            "status_color": status_color,
            "probabilitas_tepat_waktu": prob_tepat,
            "probabilitas_terlambat": prob_terlambat,
            "ringkasan_akademik": {
                "ipk_kumulatif": ipk_kumulatif,
                "tren_ips": tren_ips,
                "umur": umur,
                "ips_sem1": ips1,
                "ips_sem4": ips4
            },
            "faktor_risiko": risk_factors,
            "faktor_positif": positive_factors,
            "rekomendasi_tindakan": rekomendasi
        }

    def predict_batch(self, df_input: pd.DataFrame) -> list:
        results = []
        for _, row in df_input.iterrows():
            nim = str(row.get("NIM", "-"))
            nama = str(row.get("Nama", "Mahasiswa"))
            
            row_dict = row.to_dict()
            pred = self.predict_single(row_dict)
            
            results.append({
                "nim": nim,
                "nama": nama,
                "ipk": pred["ringkasan_akademik"]["ipk_kumulatif"],
                "tren_ips": pred["ringkasan_akademik"]["tren_ips"],
                "umur": pred["ringkasan_akademik"]["umur"],
                "prob_terlambat": pred["probabilitas_terlambat"],
                "status": pred["status"],
                "tingkat_risiko": pred["tingkat_risiko"],
                "status_color": pred["status_color"]
            })
        return results
