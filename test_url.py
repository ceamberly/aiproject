from src.url_detector import analyze_url


test_urls = [
    "https://www.google.com",
    "http://192.168.1.100/login/verify",
    "http://secure-account-free-bonus.example.com/login"
]

for url in test_urls:
    result = analyze_url(url)

    print("=" * 60)
    print("URL:", result["url"])
    print("Domain:", result["domain"])
    print("Risk Level:", result["risk_level"])
    print("Risk Score:", result["risk_score"])
    print("Status:", result["status"])

    print("Findings:")
    for finding in result["findings"]:
        print("-", finding)