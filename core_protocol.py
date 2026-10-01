import os
import time
import uuid
import json
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from legacy_bridge import LegacyWebBridge

USER_ACCOUNTS = {
    "user_ersin": {
        "balance": 5000.00,
        "daily_limit": 5000.00,
        "allowed_categories": ["retail", "travel", "finance"]
    }
}

MERCHANT_ACCOUNTS = {
    "store_sneakers_inc": 0.00,
    "store_trendpabuc": 0.00,
    "AGENTGATE_TREASURY": 0.00
}

MERCHANT_REGISTRY = [
    {"merchant_id": "store_sneakers_inc", "name": "Sneakers Inc.", "url": "http://127.0.0.1:9001"},
    {"merchant_id": "store_trendpabuc", "name": "TrendPabuç Outlet", "url": "http://127.0.0.1:9002"}
]

MISSION_TOKENS = {}
RECEIPTS = []
LOST_SALES = []
COMMISSION_RATE = 0.05
web_bridge = LegacyWebBridge()

# =====================================================================
# MOBİL TELEFONLAR İÇİN CHATGPT / GEMINI TARZI AI CHAT ARAYÜZÜ
# =====================================================================
CHAT_UI_HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>AgentGate AI | Mobil Alışveriş Asistanı</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    .chat-bubble { animation: fadeIn 0.25s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 flex flex-col h-screen overflow-hidden">
  
  <!-- Üst Bar -->
  <header class="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur flex justify-between items-center z-10">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-emerald-400 flex items-center justify-center font-bold text-xs shadow-lg shadow-indigo-500/30">
        AI
      </div>
      <div>
        <h1 class="text-sm font-bold text-white flex items-center gap-1.5 leading-none">
          AgentGate Asistanı
          <span class="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
        </h1>
        <span class="text-[10px] text-slate-400 font-mono">A-Commerce Otonom Gişe</span>
      </div>
    </div>
    <a href="/dashboard" class="text-[11px] font-mono bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 px-2.5 py-1 rounded-lg transition">
      Panel ↗
    </a>
  </header>

  <!-- Sohbet Mesaj Alanı -->
  <main id="chat-box" class="flex-1 overflow-y-auto p-4 space-y-3">
    <!-- Asistan Karşılama -->
    <div class="chat-bubble flex gap-2.5 max-w-[88%]">
      <div class="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-1">G</div>
      <div class="bg-slate-900 border border-slate-800 p-3 rounded-2xl rounded-tl-sm text-xs text-slate-200 leading-relaxed shadow-sm">
        Merhaba Ersin! Ben AgentGate otonom alışveriş asistanın. İstediğin ürünü ve bütçeni söyle, tüm piyasayı tarayıp en iyi fiyatı getireyim.
        <div class="mt-2 text-[10px] text-indigo-400 font-mono">Örnek: "42 numara air runner bütçem 1500 tl"</div>
      </div>
    </div>
  </main>

  <!-- Alt Giriş Çubuğu -->
  <footer class="p-3 border-t border-slate-800 bg-slate-900/90 backdrop-blur">
    <form id="chat-form" onsubmit="sendMessage(event)" class="flex gap-2 items-center">
      <input 
        type="text" 
        id="user-input" 
        autocomplete="off"
        placeholder="Ürün ve bütçeni yaz..." 
        class="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-3 text-xs text-white outline-none transition"
      />
      <button 
        type="submit" 
        id="send-btn"
        class="bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white font-bold p-3 rounded-xl transition shadow-lg shadow-indigo-600/30 flex items-center justify-center">
        <svg class="w-4 h-4 rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19V5m0 0l-7 7m7-7l7 7"/></svg>
      </button>
    </form>
  </footer>

  <script>
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('user-input');
    let lastRecommendation = null;

    function appendMessage(sender, text, isHtml = false) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `chat-bubble flex gap-2.5 max-w-[88%] ${sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`;
      
      const avatar = sender === 'user' 
        ? '<div class="w-6 h-6 rounded-full bg-emerald-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-1">E</div>'
        : '<div class="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-1">G</div>';
      
      const bubbleClass = sender === 'user'
        ? 'bg-indigo-600 text-white p-3 rounded-2xl rounded-tr-sm text-xs leading-relaxed shadow-sm'
        : 'bg-slate-900 border border-slate-800 p-3 rounded-2xl rounded-tl-sm text-xs text-slate-200 leading-relaxed shadow-sm';

      msgDiv.innerHTML = `
        ${avatar}
        <div class="${bubbleClass}">
          ${isHtml ? text : text.replace(/\\n/g, '<br>')}
        </div>
      `;
      chatBox.appendChild(msgDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage(e) {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      appendMessage('user', text);
      input.value = '';

      // Yükleniyor balonu
      const loadingId = 'loading-' + Date.now();
      const loadDiv = document.createElement('div');
      loadDiv.id = loadingId;
      loadDiv.className = 'chat-bubble flex gap-2.5 max-w-[88%]';
      loadDiv.innerHTML = `
        <div class="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-1">G</div>
        <div class="bg-slate-900 border border-slate-800 p-3 rounded-2xl text-xs text-slate-400 italic flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span>
          Piyasa ve AgentGate ağı taranıyor...
        </div>
      `;
      chatBox.appendChild(loadDiv);
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        // Numara ve ürün tespiti
        const sizeMatch = text.match(/(\\d{2})\\s*(numara|beden)?/i);
        const size = sizeMatch ? sizeMatch[1] : 42;
        const query = text.toLowerCase().includes('air runner') ? 'air runner' : 'ayakkabı';

        const res = await fetch(`/v1/ai/search?query=${encodeURIComponent(query)}&size=${size}`);
        const data = await res.json();
        document.getElementById(loadingId)?.remove();

        if (data.recommended_product) {
          lastRecommendation = data.recommended_product;
          let reply = `Piyasadaki tüm mağazaları taradım! 🎯<br><br>`;
          reply += `En avantajlı teklif: <strong>${lastRecommendation.merchant_name}</strong><br>`;
          reply += `Ürün: <strong>${lastRecommendation.title} (${lastRecommendation.size} No)</strong><br>`;
          reply += `Fiyat: <span class="text-emerald-400 font-bold text-sm">${Number(lastRecommendation.price).toFixed(2)} TL</span><br><br>`;
          
          if (data.lost_sale_warning) {
            reply += `<span class="text-[10px] text-amber-400/90 block bg-amber-950/30 border border-amber-500/20 p-2 rounded-lg mb-2">
              ⚠️ ${data.lost_sale_warning.lost_merchant} daha ucuzdu (${data.lost_sale_warning.offered_price} TL) ancak otonom satışa kapalı olduğu için tercih edilmedi.
            </span>`;
          }

          reply += `<button onclick="confirmOrder()" class="w-full mt-2 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white font-bold py-2.5 rounded-xl text-xs uppercase tracking-wider transition shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-1.5">
            <span>💳</span> Otonom Satın Alımı Onayla
          </button>`;

          appendMessage('assistant', reply, true);
        } else {
          appendMessage('assistant', 'Aradığınız kriterlere uygun ürün bulunamadı.');
        }
      } catch (err) {
        document.getElementById(loadingId)?.remove();
        appendMessage('assistant', 'Bir bağlantı hatası oluştu, lütfen tekrar deneyin.');
      }
    }

    async function confirmOrder() {
      if (!lastRecommendation) return;

      appendMessage('user', 'Onaylıyorum, satın al.');

      const loadingId = 'loading-buy-' + Date.now();
      const loadDiv = document.createElement('div');
      loadDiv.id = loadingId;
      loadDiv.className = 'chat-bubble flex gap-2.5 max-w-[88%]';
      loadDiv.innerHTML = `
        <div class="w-6 h-6 rounded-full bg-indigo-600 flex-shrink-0 flex items-center justify-center text-[10px] font-bold mt-1">G</div>
        <div class="bg-slate-900 border border-slate-800 p-3 rounded-2xl text-xs text-slate-400 italic flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          HTTP 402 gişesinden ödeme takası yapılıyor...
        </div>
      `;
      chatBox.appendChild(loadDiv);
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const res = await fetch('/v1/ai/buy', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            user_id: 'user_ersin',
            merchant_id: lastRecommendation.merchant_id,
            sku: lastRecommendation.sku,
            max_budget: 2000.0,
            shipping_address: 'Atatürk Mah. Balıkesir'
          })
        });
        const order = await res.json();
        document.getElementById(loadingId)?.remove();

        if (order.status === 'ORDER_SUCCESSFULLY_COMPLETED') {
          let successHtml = `🎉 <strong>Siparişiniz Başarıyla Verildi!</strong><br><br>`;
          successHtml += `🏪 Satıcı: <strong>${lastRecommendation.merchant_name}</strong><br>`;
          successHtml += `📦 Kargo Kodu: <span class="font-mono text-indigo-300 font-bold">${order.order_tracking_id}</span><br>`;
          successHtml += `🧾 Makbuz: <span class="font-mono text-slate-400">${order.receipt_id}</span><br>`;
          successHtml += `💳 Tahsilat: <strong>${order.total_paid_tl} TL</strong> (%5 komisyon kasaya aktarıldı)<br><br>`;
          successHtml += `<span class="text-emerald-400 text-[11px]">Kargonuz adrese yola çıkmak üzere hazırlanıyor!</span>`;
          appendMessage('assistant', successHtml, true);
        } else {
          appendMessage('assistant', 'Ödeme tamamlanamadı: ' + (order.error || 'Bilinmeyen hata'));
        }
      } catch (e) {
        document.getElementById(loadingId)?.remove();
        appendMessage('assistant', 'Satın alma sırasında bir hata oluştu.');
      }
    }
  </script>
</body>
</html>
"""

# =====================================================================
# CORE PROTOCOL HTTP HANDLER
# =====================================================================
class ProtocolHandler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. MOBİL CHAT EKRANI (Telefondan açılacak)
        if parsed.path in ["/chat", "/app"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(CHAT_UI_HTML.encode("utf-8"))
            return

        # 2. YÖNETİCİ VE HAZİNE PANELİ
        elif parsed.path in ["/", "/dashboard"]:
            # Basit yönlendirme veya panel
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>AgentGate Aktif. Sohbete gitmek icin: <a href='/chat'>/chat</a></h1>")
            return

        elif parsed.path == "/v1/registry":
            return self._json({"network_merchants": MERCHANT_REGISTRY})

        elif parsed.path == "/v1/ledger":
            return self._json({
                "user_accounts": USER_ACCOUNTS,
                "merchant_accounts": MERCHANT_ACCOUNTS,
                "network_merchants": MERCHANT_REGISTRY,
                "receipts": RECEIPTS,
                "lost_sales": LOST_SALES
            })

        # 3. LLM ARAMA VE PİYASA TARAMA UCUNU ÇALIŞTIR
        elif parsed.path == "/v1/ai/search":
            query_params = urllib.parse.parse_qs(parsed.query)
            q = query_params.get("query", [""])[0].lower()
            size = query_params.get("size", [None])[0]
            size_int = int(size) if size else None

            offers = []
            for m in MERCHANT_REGISTRY:
                try:
                    manifest = requests.get(f"{m['url']}/.well-known/agentgate.json", timeout=1.5).json()
                    search_url = f"{m['url']}{manifest['endpoints']['search']}?q={q}"
                    if size_int:
                        search_url += f"&size={size_int}"
                    res = requests.get(search_url, timeout=1.5).json()
                    for item in res.get("items", []):
                        offers.append({
                            "merchant_id": m["merchant_id"],
                            "merchant_name": m["name"],
                            "sku": item["sku"],
                            "title": item["title"],
                            "size": item["size"],
                            "price": item["price"],
                            "store_url": m["url"],
                            "checkout_endpoint": manifest["endpoints"]["checkout"],
                            "autonomous_buy_supported": True
                        })
                except Exception:
                    pass

            legacy_offers = web_bridge.scan_unregistered_web(q, size_int)

            offers.sort(key=lambda x: x["price"])
            best_choice = offers[0] if offers else None

            lost_sale_detected = None
            if legacy_offers and best_choice:
                cheapest_legacy = min(legacy_offers, key=lambda x: x["price"])
                if cheapest_legacy["price"] < best_choice["price"]:
                    lost_sale_detected = {
                        "lost_merchant": cheapest_legacy["merchant_name"],
                        "offered_price": cheapest_legacy["price"],
                        "reason": "Site requires manual form/captcha; no HTTP 402 support."
                    }
                    LOST_SALES.append({
                        "lost_merchant": cheapest_legacy["merchant_name"],
                        "offered_price": cheapest_legacy["price"],
                        "winning_merchant": best_choice["merchant_name"],
                        "actual_price": best_choice["price"],
                        "timestamp": time.time()
                    })

            return self._json({
                "status": "SUCCESS",
                "recommended_product": best_choice,
                "all_network_offers": offers,
                "unregistered_web_offers": legacy_offers,
                "lost_sale_warning": lost_sale_detected
            })

        return self._json({"error": "NOT_FOUND"}, 404)

    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        # 4. OTONOM SATIN ALMA
        if self.path == "/v1/ai/buy":
            user_id = body.get("user_id", "user_ersin")
            merchant_id = body.get("merchant_id")
            sku = body.get("sku")
            max_budget = float(body.get("max_budget", 0))
            shipping_address = body.get("shipping_address", "Varsayılan Adres")

            user = USER_ACCOUNTS.get(user_id)
            if not user or user["balance"] < max_budget:
                return self._json({"error": "INSUFFICIENT_FUNDS_OR_USER_NOT_FOUND"}, 400)

            merchant = next((m for m in MERCHANT_REGISTRY if m["merchant_id"] == merchant_id), None)
            if not merchant:
                return self._json({"error": "MERCHANT_NOT_FOUND"}, 404)

            manifest = requests.get(f"{merchant['url']}/.well-known/agentgate.json").json()
            checkout_url = f"{merchant['url']}{manifest['endpoints']['checkout']}"
            payload = {"sku": sku, "shipping_address": shipping_address}

            challenge_res = requests.post(checkout_url, json=payload)
            if challenge_res.status_code != 402:
                return self._json({"error": "STORE_DID_NOT_RETURN_402"}, 500)
            
            challenge = challenge_res.json()
            price = challenge["price_tl"]

            if price > max_budget:
                return self._json({"error": "PRICE_EXCEEDS_USER_BUDGET"}, 403)

            fee = round(price * COMMISSION_RATE, 2)
            merchant_payout = round(price - fee, 2)

            user["balance"] -= price
            MERCHANT_ACCOUNTS[merchant_id] = round(MERCHANT_ACCOUNTS.get(merchant_id, 0.0) + merchant_payout, 2)
            MERCHANT_ACCOUNTS["AGENTGATE_TREASURY"] = round(MERCHANT_ACCOUNTS["AGENTGATE_TREASURY"] + fee, 2)

            receipt_id = f"rcpt_{uuid.uuid4().hex[:10]}"
            RECEIPTS.append({
                "receipt_id": receipt_id,
                "user_id": user_id,
                "merchant_id": merchant_id,
                "amount": price,
                "fee": fee,
                "timestamp": time.time()
            })

            final_res = requests.post(
                checkout_url,
                json=payload,
                headers={"X-AgentGate-Receipt": receipt_id}
            ).json()

            return self._json({
                "status": "ORDER_SUCCESSFULLY_COMPLETED",
                "receipt_id": receipt_id,
                "product_name": final_res.get("product"),
                "total_paid_tl": price,
                "protocol_fee_tl": fee,
                "order_tracking_id": final_res.get("order_id"),
                "delivery_address": shipping_address
            })

        return self._json({"error": "NOT_FOUND"}, 404)

    def log_message(self, *args):
        return

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    print(f"⚡ AGENTGATE AKTİF - PORT: {port}")
    HTTPServer(("", port), ProtocolHandler).serve_forever()
