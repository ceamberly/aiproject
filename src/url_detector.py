
import re
import ipaddress
from urllib.parse import urlparse


# Domain resmi yang dipercaya.
# Daftar ini bisa ditambah sesuai kebutuhan.
TRUSTED_DOMAINS = [
    "facebook.com",
    "fb.com",
    "instagram.com",
    "messenger.com",
    "threads.net",
    "google.com",
    "youtube.com",
    "whatsapp.com",
    "microsoft.com",
    "live.com",
    "apple.com",
    "icloud.com"
]


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


def is_trusted_domain(domain):
    """
    Memeriksa apakah domain termasuk daftar domain tepercaya.
    Subdomain resmi juga diperbolehkan.
    Contoh: accounts.google.com
    """

    return any(
        domain == trusted or domain.endswith("." + trusted)
        for trusted in TRUSTED_DOMAINS
    )


def analyze_url(url):
    """
    Menganalisis indikator risiko URL menggunakan
    Trusted Domain dan Heuristic Detection.

    Pemeriksaan ini bukan jaminan bahwa URL aman.
    """

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL tidak boleh kosong.")

    url = url.strip()

    # Tambahkan skema jika tidak tersedia
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url

    try:
        parsed = urlparse(url)
        domain = (parsed.hostname or "").lower()
    except ValueError:
        raise ValueError("Format URL tidak valid.")

    if not domain:
        raise ValueError("Format URL atau nama domain tidak valid.")

    score = 0
    findings = []

    def add_finding(points, message):
        nonlocal score
        score += points
        findings.append(message)

    # Periksa domain tepercaya
    trusted = is_trusted_domain(domain)

    if trusted:
        findings.append(
            "Domain cocok dengan daftar domain resmi yang dipercaya."
        )

    # Panjang URL
    if len(url) > 100:
        add_finding(1, "URL memiliki panjang yang tidak biasa.")

    if len(url) > 200:
        add_finding(2, "URL sangat panjang.")

    # HTTPS
    if parsed.scheme.lower() != "https":
        add_finding(1, "URL tidak menggunakan HTTPS.")

    # Periksa alamat IP
    is_ip = False

    try:
        ipaddress.ip_address(domain)
        is_ip = True
        add_finding(3, "Domain menggunakan alamat IP langsung.")
    except ValueError:
        pass

    # Simbol @
    if "@" in url:
        add_finding(
            3,
            "URL mengandung simbol @ yang dapat menyamarkan tujuan."
        )

    # Tanda hubung pada domain
    if "-" in domain:
        add_finding(1, "Domain mengandung tanda hubung.")

    # Punycode
    if "xn--" in domain:
        add_finding(2, "Domain menggunakan format Punycode.")

    # Banyak subdomain
    # Alamat IP tidak dihitung sebagai subdomain.
    # Ambang dibuat lebih tinggi agar tidak mudah salah menandai.
    if not is_ip and len(domain.split(".")) >= 5:
        add_finding(2, "Domain memiliki banyak bagian subdomain.")

    # Kata mencurigakan
    matched_keywords = [
        keyword
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in url.lower()
    ]

    # Kata login/verify tidak diberi skor jika domain tepercaya.
    if matched_keywords and not trusted:
        add_finding(
            min(len(matched_keywords), 3),
            "Mengandung kata mencurigakan: "
            + ", ".join(matched_keywords)
        )
    elif matched_keywords and trusted:
        findings.append(
            "Kata login/verifikasi ditemukan, tetapi tidak diberi "
            "skor tambahan karena domain cocok dengan daftar tepercaya."
        )

    # URL shortener
    if domain in SHORTENER_DOMAINS:
        add_finding(2, "Menggunakan layanan pemendek URL.")

    # Tingkat risiko
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
