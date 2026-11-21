import io
import json
import re

import pandas as pd
import streamlit as st


def _read_text_table(text):
    """Mencoba membaca teks sebagai tabel atau kumpulan key=value."""

    text = text.strip()

    if not text:
        raise ValueError("File tidak memiliki isi teks.")

    # Coba membaca format CSV, TSV, atau tabel dengan pemisah otomatis.
    for separator in [None, ",", ";", "\t", "|"]:
        try:
            df = pd.read_csv(
                io.StringIO(text),
                sep=separator,
                engine="python",
                on_bad_lines="skip"
            )

            if len(df.columns) >= 2 and not df.empty:
                return df

        except Exception:
            continue

    # Coba membaca format log seperti:
    # login_attempts=10 ip_score=20 duration=5
    records = []

    for line in text.splitlines():
        pairs = re.findall(
            r'([A-Za-z_][A-Za-z0-9_.-]*)\s*[:=]\s*(-?\d+(?:\.\d+)?)',
            line
        )

        if pairs:
            records.append(dict(pairs))

    if records:
        return pd.DataFrame(records)

    raise ValueError(
        "Tidak ditemukan tabel atau data numerik terstruktur. "
        "Untuk Anomaly Detection, gunakan file yang memiliki "
        "baris data dan kolom numerik."
    )


def _read_pdf(file_bytes):
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return _read_text_table("\n".join(pages))


def _read_docx(file_bytes):
    from docx import Document

    document = Document(io.BytesIO(file_bytes))

    # Prioritaskan tabel Word jika tersedia.
    for table in document.tables:
        rows = []

        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])

        if len(rows) >= 2:
            return pd.DataFrame(rows[1:], columns=rows[0])

    # Jika tidak ada tabel, coba baca paragraf sebagai teks.
    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return _read_text_table(text)


def _read_json(file_bytes):
    content = json.loads(file_bytes.decode("utf-8-sig"))

    if isinstance(content, list):
        df = pd.json_normalize(content)

    elif isinstance(content, dict):
        # Mendukung JSON yang membungkus daftar data.
        list_values = [
            value for value in content.values()
            if isinstance(value, list) and value
        ]

        if list_values and all(
            isinstance(item, dict) for item in list_values[0]
        ):
            df = pd.json_normalize(list_values[0])
        else:
            df = pd.json_normalize(content)

    else:
        raise ValueError("Struktur JSON tidak didukung.")

    if df.empty:
        raise ValueError("JSON tidak memiliki data untuk dianalisis.")

    return df


def parse_uploaded_file(uploaded_file):
    """
    Membaca file yang diunggah dan mengubahnya menjadi DataFrame.
    Mendukung CSV, TXT, LOG, XLSX, XLS, PDF, DOCX, dan JSON.
    """

    filename = uploaded_file.name
    extension = filename.rsplit(".", 1)[-1].lower()
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("File kosong.")

    if extension == "csv":
        data = pd.read_csv(io.BytesIO(file_bytes))

    elif extension in ["txt", "log"]:
        text = file_bytes.decode("utf-8-sig", errors="replace")
        data = _read_text_table(text)

    elif extension in ["xlsx", "xls"]:
        data = pd.read_excel(io.BytesIO(file_bytes))

    elif extension == "pdf":
        data = _read_pdf(file_bytes)

    elif extension == "docx":
        data = _read_docx(file_bytes)

    elif extension == "json":
        data = _read_json(file_bytes)

    else:
        raise ValueError(f"Format .{extension} belum didukung.")

    if data.empty:
        raise ValueError("Tidak ada data yang berhasil dibaca.")

    # Ubah kolom angka yang tersimpan sebagai teks menjadi numerik.
    for column in data.columns:
        converted = pd.to_numeric(data[column], errors="coerce")

        if converted.notna().sum() > 0:
            data[column] = converted

    return data