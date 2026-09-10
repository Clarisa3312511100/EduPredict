import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import urllib.request
import time
from app.predictor import StudentGraduationPredictor

def test_predictor():
    print("=== Menguji StudentGraduationPredictor (Dataset Riil) ===")
    predictor = StudentGraduationPredictor()
    assert predictor.is_ready(), "Model harus terpasang dan siap digunakan."

    # Test 1: Mahasiswa Berprestasi / Tepat Waktu
    safe_student = {
        "IPS_Sem1": 3.75,
        "IPS_Sem2": 3.80,
        "IPS_Sem3": 3.85,
        "IPS_Sem4": 3.90,
        "Umur": 22,
        "Jenis_Kelamin": "Perempuan",
        "Status_Bekerja": 0,
        "Status_Nikah": 0
    }
    res_safe = predictor.predict_single(safe_student)
    print("Prediksi Mahasiswa Aman:", res_safe["status"], f"(Risiko: {res_safe['probabilitas_terlambat']}%)")
    assert res_safe["status"] == "Tepat Waktu", f"Ekspektasi 'Tepat Waktu' namun didapat {res_safe['status']}"

    # Test 2: Mahasiswa Berisiko Terlambat
    risky_student = {
        "IPS_Sem1": 2.40,
        "IPS_Sem2": 2.10,
        "IPS_Sem3": 1.90,
        "IPS_Sem4": 1.80,
        "Umur": 27,
        "Jenis_Kelamin": "Laki-laki",
        "Status_Bekerja": 1,
        "Status_Nikah": 1
    }
    res_risky = predictor.predict_single(risky_student)
    print("Prediksi Mahasiswa Berisiko:", res_risky["status"], f"(Risiko: {res_risky['probabilitas_terlambat']}%)")
    assert res_risky["status"] in ["Terlambat", "Berisiko Sedang"], f"Ekspektasi status berisiko namun didapat {res_risky['status']}"

    print("Pengujian Predictor Sukses!\n")

def test_api_endpoints():
    print("=== Menguji API FastAPI EduPredict (Localhost:8000) ===")
    base_url = "http://127.0.0.1:8000"

    try:
        # 1. Test GET /api/overview
        req = urllib.request.urlopen(f"{base_url}/api/overview", timeout=5)
        assert req.status == 200
        overview_data = json.loads(req.read().decode("utf-8"))
        print(f"GET /api/overview OK - Total Data Latih: {overview_data.get('stats', {}).get('total_mahasiswa')}")

        # 2. Test POST /api/predict
        payload = {
            "NIM": "3312511100",
            "Nama": "Clarisa Tampilang",
            "IPS_Sem1": 3.50,
            "IPS_Sem2": 3.60,
            "IPS_Sem3": 3.65,
            "IPS_Sem4": 3.70,
            "IPK_Kumulatif": 3.61,
            "Umur": 21,
            "Jenis_Kelamin": "Perempuan",
            "Status_Bekerja": 0,
            "Status_Nikah": 0
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req_post = urllib.request.Request(
            f"{base_url}/api/predict",
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        res_post = urllib.request.urlopen(req_post, timeout=5)
        assert res_post.status == 200
        res_data = json.loads(res_post.read().decode("utf-8"))
        print(f"POST /api/predict OK - Status: {res_data.get('status')}, Probabilitas Terlambat: {res_data.get('probabilitas_terlambat')}%")

        print("Semua endpoint API berjalan sempurna!\n")
    except Exception as e:
        print(f"Peringatan: Tidak dapat menghubungi server API secara langsung ({e}). Pastikan uvicorn berjalan jika menguji server.")

if __name__ == "__main__":
    test_predictor()
    test_api_endpoints()
