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
        student_data harus memiliki key:
        - IPS_Sem1, IPS_Sem2, IPS_Sem3, IPS_Sem4
        - SKS_Lulus, SKS_Gagal, Persentase_Kehadiran
        - Jalur_Masuk (SNBP, SNBT, Mandiri)
        - Status_Bekerja (0/1)
        - Pernah_Cuti (0/1)
        """
        if not self.is_ready():
            raise RuntimeError("Model belum dilatih atau file model tidak ditemukan.")

        # Hitung derived features
        ips1 = float(student_data["IPS_Sem1"])
        ips2 = float(student_data["IPS_Sem2"])
        ips3 = float(student_data["IPS_Sem3"])
        ips4 = float(student_data["IPS_Sem4"])
        
        ipk_kumulatif = round((ips1 + ips2 + ips3 + ips4) / 4.0, 2)
        tren_ips = round(ips4 - ips1, 2)
        
        sks_lulus = int(student_data["SKS_Lulus"])
        sks_gagal = int(student_data["SKS_Gagal"])
        total_sks = max(1, sks_lulus + sks_gagal)
        rasio_sks_gagal = round(sks_gagal / total_sks, 3)
        kehadiran = float(student_data["Persentase_Kehadiran"])
        
        jalur_masuk = str(student_data.get("Jalur_Masuk", "SNBT"))
        status_bekerja = int(student_data.get("Status_Bekerja", 0))
        pernah_cuti = int(student_data.get("Pernah_Cuti", 0))

        # Bentuk DataFrame satu baris untuk pipeline
        df_input = pd.DataFrame([{
            "IPS_Sem1": ips1,
            "IPS_Sem2": ips2,
            "IPS_Sem3": ips3,
            "IPS_Sem4": ips4,
            "IPK_Kumulatif": ipk_kumulatif,
            "SKS_Lulus": sks_lulus,
            "SKS_Gagal": sks_gagal,
            "Persentase_Kehadiran": kehadiran,
            "Tren_IPS": tren_ips,
            "Rasio_SKS_Gagal": rasio_sks_gagal,
            "Jalur_Masuk": jalur_masuk,
            "Status_Bekerja": status_bekerja,
            "Pernah_Cuti": pernah_cuti
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
            risk_factors.append(f"IPK Kumulatif di bawah standar aman ({ipk_kumulatif:.2f} < 2.75)")
        else:
            positive_factors.append(f"IPK Kumulatif solid ({ipk_kumulatif:.2f})")

        if sks_gagal > 4:
            risk_factors.append(f"Terdapat {sks_gagal} SKS gagal/mengulang yang perlu ditempuh ulang")
        
        if tren_ips < -0.30:
            risk_factors.append(f"Tren nilai menurun drastis dari Semester 1 ke 4 ({tren_ips:+.2f})")
        elif tren_ips > 0.20:
            positive_factors.append(f"Tren performa akademik meningkat positif ({tren_ips:+.2f})")

        if kehadiran < 75.0:
            risk_factors.append(f"Tingkat kehadiran rendah ({kehadiran}%), berisiko terkena syarat minimal ujian")

        if pernah_cuti == 1:
            risk_factors.append("Riwayat pernah mengambil cuti akademik berpotensi memundurkan masa studi")

        if status_bekerja == 1:
            risk_factors.append("Status bekerja paruh waktu berpotensi membagi fokus akademik")

        # Rekomendasi tindakan dosen PA
        if tingkat_risiko == "Tinggi":
            rekomendasi = "Perlu pemanggilan segera oleh Dosen PA. Susun rencana remedial SKS gagal pada Semester Pendek dan evaluasi beban kerja."
        elif tingkat_risiko == "Sedang":
            rekomendasi = "Berikan monitoring berkala di awal Semester 5. Pastikan kehadiran kuliah di atas 80% dan dorong perbaikan nilai mata kuliah prasyarat."
        else:
            rekomendasi = "Performa akademik sangat baik. Mahasiswa berpotensi lulus tepat waktu bahkan berpeluang lulus 3.5 tahun / predikat Pujian."

        return {
            "status": status,
            "tingkat_risiko": tingkat_risiko,
            "status_color": status_color,
            "probabilitas_tepat_waktu": prob_tepat,
            "probabilitas_terlambat": prob_terlambat,
            "ringkasan_akademik": {
                "ipk_kumulatif": ipk_kumulatif,
                "tren_ips": tren_ips,
                "sks_lulus": sks_lulus,
                "sks_gagal": sks_gagal,
                "rasio_sks_gagal": rasio_sks_gagal,
                "kehadiran": kehadiran
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
                "sks_lulus": pred["ringkasan_akademik"]["sks_lulus"],
                "sks_gagal": pred["ringkasan_akademik"]["sks_gagal"],
                "kehadiran": pred["ringkasan_akademik"]["kehadiran"],
                "prob_terlambat": pred["probabilitas_terlambat"],
                "status": pred["status"],
                "tingkat_risiko": pred["tingkat_risiko"],
                "status_color": pred["status_color"]
            })
        return results
