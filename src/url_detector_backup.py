
import re
import ipaddress
from urllib.parse import urlparse


SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "verification",
    "account",
    "password",
    "secure",
    "update",
    "free",
    "gift",
    "bonus",
    "claim",
    "banking",
    "wallet",
    "confirm",
    "signin"
]

SHORTENER_DOMAINS = [
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at"
]


def analyze_url(url):
    """
    Memeriksa indikator mencurigakan pada sebuah URL.
    Pemeriksaan ini berbasis heuristik, bukan jaminan keamanan.
    """

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL tidak boleh kosong.")

    url = url.strip()

    # Tambahkan skema jika pengguna tidak menuliskannya
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url

    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()

    if not domain:
        raise ValueError("Format URL atau nama domain tidak valid.")

    score = 0
    findings = []

    def add_finding(points, message):
        nonlocal score
        score += points
        findings.append(message)

    # Panjang URL
    if len(url) > 100:
        add_finding(1, "URL memiliki panjang yang tidak biasa.")

    if len(url) > 200:
        add_finding(2, "URL sangat panjang.")

    # HTTPS
    if parsed.scheme.lower() != "https":
        add_finding(1, "URL tidak menggunakan HTTPS.")

    # Penggunaan alamat IP sebagai domain
    try:
        ipaddress.ip_address(domain)
        add_finding(3, "Domain menggunakan alamat IP langsung.")
    except ValueError:
        pass

    # Simbol @ pada URL
    if "@" in url:
        add_finding(3, "URL mengandung simbol @ yang dapat menyamarkan tujuan.")

    # Karakter khusus
    if "-" in domain:
        add_finding(1, "Domain mengandung tanda hubung.")

    # Punycode
    if "xn--" in domain:
        add_finding(2, "Domain menggunakan format Punycode.")

    # Jumlah subdomain
    domain_parts = domain.split(".")
    if len(domain_parts) >= 4:
        add_finding(2, "Domain memiliki banyak subdomain.")

    # Kata-kata mencurigakan
    matched_keywords = [
        keyword for keyword in SUSPICIOUS_KEYWORDS
        if keyword in url.lower()
    ]

    if matched_keywords:
        add_finding(
            min(len(matched_keywords), 3),
            "Mengandung kata mencurigakan: "
            + ", ".join(matched_keywords)
        )

    # URL shortener
    if domain in SHORTENER_DOMAINS:
        add_finding(2, "Menggunakan layanan pemendek URL.")

    # Tentukan tingkat risiko
    if score >= 6:
        risk = "High Risk"
        status = "Berisiko Tinggi"
    elif score >= 3:
        risk = "Medium Risk"
        status = "Perlu Diwaspadai"
    else:
        risk = "Low Risk"
        status = "Indikator Risiko Rendah"

    if not findings:
        findings.append(
            "Tidak ditemukan indikator mencurigakan dari pemeriksaan dasar."
        )

    return {
        "url": url,
        "domain": domain,
        "risk_level": risk,
        "status": status,
        "risk_score": score,
        "findings": findings
    }
