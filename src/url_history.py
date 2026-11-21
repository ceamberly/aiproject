
import json
from pathlib import Path
from datetime import datetime


PROJECT_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_DIR / "reports" / "url_history.json"


def load_url_history():
    """Memuat riwayat pemeriksaan URL."""

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_url_history(result):
    """Menyimpan hasil pemeriksaan URL."""

    history = load_url_history()

    new_entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "url": result["url"],
        "domain": result["domain"],
        "risk_level": result["risk_level"],
        "risk_score": result["risk_score"],
        "status": result["status"],
        "findings": result["findings"]
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