import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import urllib.request
import time
from app.predictor import StudentGraduationPredictor

def test_predictor():
    print("Testing StudentGraduationPredictor...")
    predictor = StudentGraduationPredictor()
    assert predictor.is_ready(), "Model should be loaded and ready"

    # Test 1: Mahasiswa Aman / Berprestasi
    safe_student = {
        "IPS_Sem1": 3.75,
        "IPS_Sem2": 3.80,
        "IPS_Sem3": 3.85,
        "IPS_Sem4": 3.90,
        "SKS_Lulus": 88,
        "SKS_Gagal": 0,
        "Persentase_Kehadiran": 96.0,
        "Jalur_Masuk": "SNBP",
        "Status_Bekerja": 0,
        "Pernah_Cuti": 0
    }
    res_safe = predictor.predict_single(safe_student)
    print("Safe student prediction:", res_safe["status"], f"(Risk: {res_safe['probabilitas_terlambat']}%)")
    assert res_safe["status"] == "Tepat Waktu", f"Expected 'Tepat Waktu' but got {res_safe['status']}"

    # Test 2: Mahasiswa Berisiko Tinggi
    risky_student = {
        "IPS_Sem1": 2.60,
        "IPS_Sem2": 2.20,
        "IPS_Sem3": 1.90,
        "IPS_Sem4": 1.70,
        "SKS_Lulus": 64,
        "SKS_Gagal": 16,
        "Persentase_Kehadiran": 68.0,
        "Jalur_Masuk": "Mandiri",
        "Status_Bekerja": 1,
        "Pernah_Cuti": 1
    }
    res_risky = predictor.predict_single(risky_student)
    print("Risky student prediction:", res_risky["status"], f"(Risk: {res_risky['probabilitas_terlambat']}%)")
    assert res_risky["status"] in ["Terlambat", "Berisiko Sedang"], f"Expected risky status but got {res_risky['status']}"

    print("ALL PREDICTOR TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    test_predictor()
