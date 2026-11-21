import pandas as pd

from src.anomaly_detector import detect_anomalies

# Membaca dataset
data = pd.read_csv("data/sample_data.csv")

# Menghapus ID karena bukan fitur numerik untuk analisis
data = data.drop(columns=["transaction_id"])

# Menjalankan AI
results = detect_anomalies(
    data,
    contamination=0.10
)

# Menampilkan hasil
print("\n===== HASIL DETEKSI ANOMALI =====\n")

print(results.to_string(index=False))

# Menghitung jumlah data
normal = (results["anomaly_status"] == "Normal").sum()
anomaly = (results["anomaly_status"] == "Anomaly").sum()

print("\n===== RINGKASAN =====")
print(f"Data normal   : {normal}")
print(f"Data anomali  : {anomaly}")
print(f"Total data    : {len(results)}")
from sklearn.metrics import confusion_matrix, classification_report

# Label sebenarnya berdasarkan dataset percobaan
actual = ["Normal"] * 20 + ["Anomaly"] * 2

# Prediksi dari AI
predicted = results["anomaly_status"].tolist()

print("\n===== EVALUASI MODEL =====")

print("\nConfusion Matrix:")
print(confusion_matrix(
    actual,
    predicted,
    labels=["Normal", "Anomaly"]
))

print("\nClassification Report:")
print(classification_report(
    actual,
    predicted,
    labels=["Normal", "Anomaly"],
    zero_division=0
))