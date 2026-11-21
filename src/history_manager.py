
import json
from pathlib import Path
from datetime import datetime

# Lokasi penyimpanan riwayat
PROJECT_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_DIR / "reports" / "history.json"


def load_history():
    """Membaca seluruh riwayat analisis."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(results, source_name, contamination):
    """Menyimpan hasil analisis ke file JSON."""

    history = load_history()

    normal_count = int(
        (results["anomaly_status"] == "Normal").sum()
    )

    anomaly_count = int(
        (results["anomaly_status"] == "Anomaly").sum()
    )

    # Mengubah hasil DataFrame menjadi data JSON
    records = json.loads(
        results.to_json(orient="records")
    )

    new_entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "source": source_name,
        "contamination": contamination,
        "total_data": len(results),
        "normal": normal_count,
        "anomaly": anomaly_count,
        "results": records
    }

    history.append(new_entry)

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )

    return new_entry
