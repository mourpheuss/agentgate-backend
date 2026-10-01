import re
import requests

LEGACY_TARGETS = [
    {"name": "GelenekselPazar.com", "url": "http://127.0.0.1:9003"}
]

class LegacyWebBridge:
    """Protokole üye olmayan klasik web sitelerini tarayan harici gözlemci"""

    def scan_unregistered_web(self, query: str, size: int = None):
        scraped_offers = []

        for site in LEGACY_TARGETS:
            try:
                # 1. Önce protokol desteği var mı diye bakar
                check = requests.get(f"{site['url']}/.well-known/agentgate.json", timeout=1.5)
                has_agentgate = check.status_code == 200
            except Exception:
                has_agentgate = False

            try:
                # 2. Sayfa içeriğini indirip HTML'den fiyat/ürün kazır
                html_res = requests.get(site["url"], timeout=2.0)
                html = html_res.text

                if query.lower() in html.lower():
                    # Fiyatı HTML içinden bul
                    price_match = re.search(r"(\d+[\.,]?\d*)\s*TL", html)
                    price = float(price_match.group(1).replace(",", ".")) if price_match else 0.0

                    scraped_offers.append({
                        "merchant_name": site["name"],
                        "url": site["url"],
                        "title": f"Air Runner Spor Ayakkabı",
                        "size": size or 42,
                        "price": price,
                        "supports_agentgate": has_agentgate,
                        "friction": "HIGH_MANUAL_FORM_REQUIRED" if not has_agentgate else "NONE"
                    })
            except Exception as e:
                pass

        return scraped_offers