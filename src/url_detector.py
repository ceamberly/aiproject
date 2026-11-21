
from urllib.parse import urlparse
import ipaddress
import re


# =====================================
# DAFTAR DOMAIN TERPERCAYA
# =====================================

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


# =====================================
# KATA-KATA YANG PERLU DIWASPADAI
# =====================================

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


# =====================================
# DAFTAR URL SHORTENER
# =====================================

SHORTENER_DOMAINS = [
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at"
]


# =====================================
# CEK DOMAIN TERPERCAYA
# =====================================

def is_trusted_domain(domain):

    domain = domain.lower().strip(".")

    return any(
        domain == trusted
        or domain.endswith("." + trusted)
        for trusted in TRUSTED_DOMAINS
    )


# =====================================
# CEK URL
# =====================================

def analyze_url(url):

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL tidak boleh kosong.")

    url = url.strip()

    # Tambahkan protokol jika belum tersedia
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url

    parsed = urlparse(url)

    hostname = parsed.hostname

    if not hostname:
        raise ValueError("Format URL tidak valid.")

    domain = hostname.lower().strip(".")

    score = 0
    findings = []

    trusted = is_trusted_domain(domain)

    # =================================
    # 1. PANJANG URL
    # =================================

    if len(url) > 100:
        score += 1

        findings.append(
            f"URL memiliki panjang {len(url)} karakter. "
            "URL yang sangat panjang dapat digunakan untuk menyamarkan tujuan tautan."
        )

    # =================================
    # 2. PENGGUNAAN HTTPS
    # =================================

    if parsed.scheme.lower() != "https":
        score += 1

        findings.append(
            f"Protokol '{parsed.scheme.upper()}' digunakan. "
            "URL tidak menggunakan HTTPS untuk koneksi terenkripsi."
        )

    # =================================
    # 3. PENGGUNAAN ALAMAT IP
    # =================================

    try:
        ipaddress.ip_address(domain)

        score += 4

        findings.append(
            f"Alamat tujuan menggunakan IP langsung: '{domain}'. "
            "Penggunaan IP langsung perlu diwaspadai karena tidak menunjukkan nama domain situs."
        )

    except ValueError:
        pass

    # =================================
    # 4. SIMBOL @
    # =================================

    if "@" in url:
        score += 3

        findings.append(
            "Ditemukan simbol '@' pada URL. "
            "Simbol ini dapat digunakan untuk menyamarkan alamat tujuan sebenarnya."
        )

    # =================================
    # 5. TANDA HUBUNG PADA DOMAIN
    # =================================

    if "-" in domain:
        score += 1

        findings.append(
            f"Domain '{domain}' mengandung tanda hubung (-). "
            "Pola ini terkadang digunakan pada domain tiruan."
        )

    # =================================
    # 6. DOMAIN PUNYCODE
    # =================================

    if "xn--" in domain:
        score += 3

        findings.append(
            f"Domain '{domain}' mengandung format Punycode (xn--). "
            "Format ini dapat digunakan untuk meniru karakter domain lain."
        )

    # =================================
    # 7. SUBDOMAIN BERLEBIHAN
    # =================================

    try:
        ipaddress.ip_address(domain)
        is_ip = True
    except ValueError:
        is_ip = False

    if not is_ip and len(domain.split(".")) >= 5:
        score += 2

        findings.append(
            f"Domain memiliki banyak tingkatan subdomain: '{domain}'. "
            "Struktur ini dapat digunakan untuk membuat alamat terlihat seperti domain lain."
        )

    # =================================
    # 8. KATA-KATA MENCURIGAKAN
    # =================================

    if not trusted:

        found_keywords = []

        for keyword in SUSPICIOUS_KEYWORDS:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(keyword)
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, url.lower()):
                found_keywords.append(keyword)

        if found_keywords:
            score += 1

            keyword_text = ", ".join(
                f"'{word}'" for word in found_keywords
            )

            findings.append(
                f"Ditemukan kata yang perlu diwaspadai: {keyword_text}. "
                "Kata-kata tersebut dapat digunakan sebagai umpan untuk meminta "
                "informasi akun atau menarik perhatian pengguna."
            )

    # =================================
    # 9. URL SHORTENER
    # =================================

    if any(
        domain == shortener
        or domain.endswith("." + shortener)
        for shortener in SHORTENER_DOMAINS
    ):
        score += 2

        findings.append(
            f"Domain '{domain}' merupakan layanan URL shortener. "
            "Alamat tujuan sebenarnya tidak terlihat secara langsung."
        )

    # =================================
    # 10. KATEGORI RISIKO
    # =================================

    if score >= 6:
        risk_level = "High Risk"
        status = "Berisiko Tinggi"

    elif score >= 3:
        risk_level = "Medium Risk"
        status = "Perlu Diwaspadai"

    else:
        risk_level = "Low Risk"
        status = "Risiko Rendah"

    # =================================
    # 11. KESIMPULAN
    # =================================

    if not findings:
        findings.append(
            "Tidak ditemukan indikator mencurigakan berdasarkan "
            "pemeriksaan sederhana sistem."
        )

    return {
        "url": url,
        "domain": domain,
        "risk_level": risk_level,
        "status": status,
        "risk_score": score,
        "findings": findings
    }