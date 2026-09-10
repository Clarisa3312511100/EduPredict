import os
import io
import json
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.predictor import StudentGraduationPredictor

app = FastAPI(
    title="Sistem Prediksi Kelulusan Mahasiswa",
    description="Sistem Cerdas Pendeteksi Dini Risiko Keterlambatan Kelulusan Mahasiswa Berbasis Machine Learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Predictor
predictor = StudentGraduationPredictor()

class StudentInput(BaseModel):
    NIM: str = Field(default="20180099", description="Nomor Induk Mahasiswa")
    Nama: str = Field(default="Contoh Mahasiswa", description="Nama Lengkap")
    Jenis_Kelamin: str = Field(default="Laki-laki", description="Laki-laki / Perempuan")
    Umur: int = Field(ge=18, le=60, default=23, description="Usia Mahasiswa")
    Status_Bekerja: int = Field(ge=0, le=1, default=0, description="0: Mahasiswa Murni, 1: Bekerja")
    Status_Nikah: int = Field(ge=0, le=1, default=0, description="0: Belum Menikah, 1: Menikah")
    IPS_Sem1: float = Field(ge=0.0, le=4.0, default=3.25)
    IPS_Sem2: float = Field(ge=0.0, le=4.0, default=3.10)
    IPS_Sem3: float = Field(ge=0.0, le=4.0, default=2.85)
    IPS_Sem4: float = Field(ge=0.0, le=4.0, default=2.70)
    IPK_Kumulatif: float = Field(ge=0.0, le=4.0, default=2.98)


class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(creds: LoginRequest):
    """Autentikasi Dosen / Admin Program Studi"""
    users = {
        "dosen": {
            "name": "Dosen Pembimbing Akademik",
            "role": "Dosen PA",
            "nidn": "0021059001",
            "pass": "password123"
        },
        "admin": {
            "name": "Administrator Program Studi",
            "role": "Admin Akademik",
            "nidn": "ADM-PLB-01",
            "pass": "admin123"
        }
    }

    u = users.get(creds.username.lower())
    if not u:
        # Nama dan peran dinamis menyesuaikan username yang dimasukkan
        if creds.username and creds.password:
            cleaned_name = creds.username.replace("_", " ").replace(".", " ").title()
            role = "Admin Akademik" if "admin" in creds.username.lower() else "Dosen Pembimbing Akademik"
            return {
                "status": "success",
                "user": {
                    "username": creds.username.lower(),
                    "name": cleaned_name,
                    "role": role,
                    "nidn": "-"
                }
            }
        raise HTTPException(status_code=401, detail="Username atau password salah.")

    if u["pass"] != creds.password:
        raise HTTPException(status_code=401, detail="Password salah.")

    return {
        "status": "success",
        "user": {
            "username": creds.username.lower(),
            "name": u["name"],
            "role": u["role"],
            "nidn": u["nidn"]
        }
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "model_ready": predictor.is_ready()
    }

@app.get("/api/overview")
def get_overview():
    """Mengembalikan statistik dataset dan performa model"""
    predictor.load_artifacts()
    return {
        "stats": predictor.stats,
        "metrics": predictor.metrics
    }

@app.post("/api/predict")
def predict_single_student(student: StudentInput):
    """Prediksi kelulusan untuk 1 mahasiswa"""
    try:
        if not predictor.is_ready():
            predictor.load_artifacts()
            if not predictor.is_ready():
                raise HTTPException(status_code=500, detail="Model belum dilatih. Silakan jalankan training terlebih dahulu.")
        
        result = predictor.predict_single(student.model_dump())
        result["mahasiswa"] = {
            "nim": student.NIM,
            "nama": student.Nama,
            "jenis_kelamin": student.Jenis_Kelamin,
            "status_bekerja": student.Status_Bekerja,
            "status_nikah": student.Status_Nikah
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/predict-batch")
async def predict_batch_file(file: UploadFile = File(...)):
    """Prediksi massal melalui upload file CSV atau Excel"""
    try:
        if not predictor.is_ready():
            predictor.load_artifacts()

        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung. Harap gunakan format .csv atau .xlsx")

        required_cols = ["IPS_Sem1", "IPS_Sem2", "IPS_Sem3", "IPS_Sem4"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Kolom wajib berikut tidak ditemukan dalam file: {', '.join(missing)}"
            )

        batch_results = predictor.predict_batch(df)

        # Hitung agregasi hasil batch
        total = len(batch_results)
        tepat = sum(1 for r in batch_results if r["status"] == "Tepat Waktu")
        sedang = sum(1 for r in batch_results if r["tingkat_risiko"] == "Sedang")
        tinggi = sum(1 for r in batch_results if r["tingkat_risiko"] == "Tinggi")

        return {
            "total_mahasiswa": total,
            "tepat_waktu_count": tepat,
            "risiko_sedang_count": sedang,
            "risiko_tinggi_count": tinggi,
            "persentase_berisiko": round(((sedang + tinggi) / total) * 100, 1) if total > 0 else 0,
            "results": batch_results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mount static data directory (untuk unduh template contoh dataset)
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")

# Mount static web files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

