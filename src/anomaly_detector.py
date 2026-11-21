import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer


def detect_anomalies(data, contamination=0.05):
    """
    Mendeteksi data abnormal menggunakan Isolation Forest.

    Parameters:
        data: Pandas DataFrame
        contamination: Perkiraan proporsi data anomali (0.01 - 0.5)

    Returns:
        DataFrame dengan label dan skor anomali.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input harus berupa Pandas DataFrame.")

    if data.empty:
        raise ValueError("Dataset kosong.")

    if not 0.01 <= contamination <= 0.5:
        raise ValueError("Contamination harus antara 0.01 dan 0.5.")

    # Ambil kolom numerik
    numeric_data = data.select_dtypes(include=np.number).copy()

    # Bersihkan nilai tak terhingga
    numeric_data = numeric_data.replace([np.inf, -np.inf], np.nan)

    # Hapus kolom yang seluruh nilainya kosong
    numeric_data = numeric_data.dropna(axis=1, how="all")

    if numeric_data.shape[1] == 0:
        raise ValueError("Dataset tidak memiliki kolom numerik yang valid.")

    if len(numeric_data) < 3:
        raise ValueError("Dataset minimal harus memiliki 3 baris.")

    # Mengisi nilai kosong menggunakan median
    imputer = SimpleImputer(strategy="median")
    processed_data = imputer.fit_transform(numeric_data)

    # Membuat model Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )

    predictions = model.fit_predict(processed_data)

    # Menyimpan hasil deteksi
    results = data.copy()

    results["anomaly_status"] = np.where(
        predictions == -1,
        "Anomaly",
        "Normal"
    )

    # Semakin tinggi skor, semakin mencurigakan
    results["anomaly_score"] = -model.decision_function(
        processed_data
    )

    return results