import os
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

def train_and_evaluate_models(data_path="data/dataset_kelulusan.csv", output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"1. Membaca dataset dari: {data_path}")
    df = pd.read_csv(data_path)

    # Feature Engineering tambahan
    df["Tren_IPS"] = np.round(df["IPS_Sem4"] - df["IPS_Sem1"], 2)
    df["Rasio_SKS_Gagal"] = np.round(df["SKS_Gagal"] / (df["SKS_Lulus"] + df["SKS_Gagal"]), 3)

    # Fitur dan Target
    numeric_features = [
        "IPS_Sem1", "IPS_Sem2", "IPS_Sem3", "IPS_Sem4",
        "IPK_Kumulatif", "SKS_Lulus", "SKS_Gagal",
        "Persentase_Kehadiran", "Tren_IPS", "Rasio_SKS_Gagal"
    ]
    categorical_features = ["Jalur_Masuk", "Status_Bekerja", "Pernah_Cuti"]

    X = df[numeric_features + categorical_features]
    # Label: 0 = Tepat Waktu, 1 = Terlambat
    y = (df["Status_Kelulusan"] == "Terlambat").astype(int)

    # Simpan statistik dataset untuk dashboard KPI
    dataset_stats = {
        "total_mahasiswa": int(len(df)),
        "tepat_waktu_count": int((y == 0).sum()),
        "terlambat_count": int((y == 1).sum()),
        "persentase_tepat_waktu": round(float((y == 0).mean() * 100), 1),
        "persentase_terlambat": round(float((y == 1).mean() * 100), 1),
        "rata_rata_ipk": round(float(df["IPK_Kumulatif"].mean()), 2),
        "rata_rata_sks_gagal": round(float(df["SKS_Gagal"].mean()), 1),
        "rata_rata_kehadiran": round(float(df["Persentase_Kehadiran"].mean()), 1)
    }
    with open(os.path.join(output_dir, "dataset_stats.json"), "w") as f:
        json.dump(dataset_stats, f, indent=2)

    # Split Data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Data latih: {len(X_train)} sampel, Data uji: {len(X_test)} sampel")

    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    # Kandidat Model
    candidate_models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_split=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_split=6, random_state=42)
    }

    results = {}
    best_f1 = -1
    best_model_name = ""
    best_pipeline = None

    print("\n2. Melatih dan membandingkan model:")
    print("=" * 70)

    for name, clf in candidate_models.items():
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm
        }

        print(f"[{name}]")
        print(f"  Akurasi  : {acc:.4f}")
        print(f"  Presisi  : {prec:.4f}")
        print(f"  Recall   : {rec:.4f} (Kemampuan mendeteksi mahasiswa berisiko)")
        print(f"  F1-Score : {f1:.4f}")
        print(f"  ROC-AUC  : {auc:.4f}")
        print("-" * 70)

        # Pemilihan model terbaik memprioritaskan F1-score & Recall
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipeline

    print(f"\n>> Model Terbaik Terpilih: {best_model_name} dengan F1-Score: {best_f1:.4f}")

    # Ekstraksi Feature Importance dari model terbaik (jika Random Forest / Decision Tree)
    clf_step = best_pipeline.named_steps["classifier"]
    pre_step = best_pipeline.named_steps["preprocessor"]
    
    # Ambil nama fitur setelah one-hot encoding
    cat_encoder = pre_step.named_transformers_["cat"]
    encoded_cat_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + encoded_cat_names

    feature_importances = []
    if hasattr(clf_step, "feature_importances_"):
        importances = clf_step.feature_importances_
        for feat_name, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True):
            feature_importances.append({
                "feature": feat_name,
                "importance": round(float(imp), 4)
            })
    elif hasattr(clf_step, "coef_"):
        importances = np.abs(clf_step.coef_[0])
        for feat_name, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True):
            feature_importances.append({
                "feature": feat_name,
                "importance": round(float(imp), 4)
            })

    # Simpan ringkasan evaluasi
    evaluation_summary = {
        "best_model": best_model_name,
        "models_comparison": results,
        "feature_importances": feature_importances,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features
    }

    with open(os.path.join(output_dir, "metrics_summary.json"), "w") as f:
        json.dump(evaluation_summary, f, indent=2)

    # Simpan model pipeline utuh (.joblib)
    joblib.dump(best_pipeline, os.path.join(output_dir, "best_model.joblib"))
    print(f"\nModel dan artefak berhasil disimpan di direktori: '{output_dir}/'")
    print("Files:")
    print("  - best_model.joblib")
    print("  - metrics_summary.json")
    print("  - dataset_stats.json")

if __name__ == "__main__":
    train_and_evaluate_models()
