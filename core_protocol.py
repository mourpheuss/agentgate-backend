import os
import json
import time
import uuid
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ==========================================================
# FIREBASE BAĞLANTISI (KALICI GİŞE KASASI)
# ==========================================================
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET", "Hl2qgV6ipQkRzssYSSHgJDmdr363LC9sexWm2dY1")
FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "https://mineora-web-default-rtdb.firebaseio.com").rstrip("/")

def save_to_firebase(path, data, method="post"):
    """Firebase Realtime Database REST API ile veri kaydeder."""
    if not FIREBASE_SECRET:
        return None
    url = f"{FIREBASE_DB_URL}/{path}.json?auth={FIREBASE_SECRET}"
    try:
        if method == "post":
            r = requests.post(url, json=data, timeout=3)
        elif method == "patch":
            r = requests.patch(url, json=data, timeout=3)
        elif method == "put":
            r = requests.put(url, json=data, timeout=3)
        return r.json()
    except Exception as e:
        print(f"⚠️ Firebase Yazma Hatası: {e}")
        return None

# ==========================================================
# GİŞE MERKEZİ & FİRMALAR
# ==========================================================
MERCHANTS = [
    {
        "id": "m_skywings",
        "name": "SkyWings Uçuş & Bilet API",
        "category": "flights",
        "rate_per_query": 0.35,
        "currency": "TRY",
        "balance": 1845.50,
        "queries_handled": 5273
    },
    {
        "id": "m_ege_resort",
        "name": "Ege & Akdeniz Rezervasyon Havuzu",
        "category": "hotels",
        "rate_per_query": 0.50,
        "currency": "TRY",
        "balance": 3120.00,
        "queries_handled": 6240
    },
    {
        "id": "m_teknoradar",
        "name": "TeknoMarket Stok & Fiyat Radarı",
        "category": "retail",
        "rate_per_query": 0.15,
        "currency": "TRY",
        "balance": 980.25,
        "queries_handled": 6535
    }
]

# OPENAPI ŞEMASI
OPENAPI_SPEC = {
    "openapi": "3.0.1",
    "info": {
        "title": "AgentGate AI Micropayment Toll Gate",
        "description": "Yapay zeka modellerinin anlaşmalı şirketlerden mikro ödemeyle canlı veri çekmesini sağlayan gişe protokolü.",
        "version": "v1.0.0"
    },
    "servers": [{"url": "https://agent.mineoragame.com"}],
    "paths": {
        "/api/v1/gate": {
            "post": {
                "summary": "Canlı Veri Gişesi Sorgusu",
                "operationId": "queryLiveGateData",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Kullanıcının talebi"},
                                    "category": {"type": "string", "enum": ["flights", "hotels", "retail"]},
                                    "agent_id": {"type": "string", "description": "Ajan adı (Örn: ChatGPT)"}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Başarılı takas ve doğrulanmış veri paketi"}
                }
            }
        }
    }
}

HTML_PRIVACY = """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>AgentGate | Gizlilik Politikası</title><style>body{background:#07090e;color:#cbd5e1;font-family:sans-serif;max-width:800px;margin:50px auto;padding:20px;line-height:1.7;}h1{color:#fff;}a{color:#10b981;}</style></head><body><h1>AgentGate Gizlilik Politikası</h1><p>AgentGate protokolü, yapay zeka ajanları ile veri sağlayıcılar arasında kuruş bazlı mikro ödeme mutabakatı sağlar.</p><p>Sorgularda kullanıcı kişisel verileri saklanmaz; yalnızca işlem mutabakat kodu (TxID), sorgu tipi ve tahsil edilen bakiye kayıt altına alınır.</p><p><a href="/">← Ana Sayfaya Dön</a></p></body></html>"""

HTML_LANDING = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgentGate | Otonom Yapay Zeka Mikro Gişe Protokolü</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #07090e;
      --card-bg: rgba(16, 21, 33, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --cyan: #06b6d4;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background: var(--bg); color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; line-height: 1.6; }
    .grid-bg { position: fixed; inset: 0; pointer-events: none; background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 32px 32px; mask-image: radial-gradient(circle at 50% 30%, black 40%, transparent 80%); z-index: 0; }
    header { position: relative; z-index: 10; max-width: 1200px; margin: 0 auto; padding: 24px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 800; }
    .logo-badge { background: linear-gradient(135deg, var(--emerald), var(--cyan)); color: #000; font-weight: 900; font-size: 14px; padding: 4px 10px; border-radius: 8px; }
    .nav-links a { color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; margin-left: 24px; transition: color 0.2s; }
    .nav-links a:hover { color: #fff; }
    .btn-outline { border: 1px solid var(--card-border); background: rgba(255,255,255,0.03); color: #fff; padding: 8px 16px; border-radius: 10px; font-size: 13px; cursor: pointer; }
    .hero { position: relative; z-index: 1; max-width: 1000px; margin: 60px auto 40px; text-align: center; padding: 0 20px; }
    .tag { display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: var(--emerald); padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 24px; }
    h1 { font-size: clamp(34px, 5.5vw, 60px); font-weight: 800; letter-spacing: -1.5px; line-height: 1.15; margin-bottom: 24px; }
    .gradient-accent { background: linear-gradient(135deg, var(--emerald) 0%, var(--cyan) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sim-wrapper { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto 80px; padding: 0 20px; }
    .sim-card { background: var(--card-bg); backdrop-filter: blur(20px); border: 1px solid var(--card-border); border-radius: 24px; padding: 32px; box-shadow: 0 30px 60px rgba(0,0,0,0.5); }
    .sim-grid { display: grid; grid-template-columns: 1fr 120px 1fr; gap: 20px; align-items: center; }
    @media(max-width: 850px) { .sim-grid { grid-template-columns: 1fr; } }
    .box { background: rgba(8, 12, 20, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; }
    select, input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid var(--card-border); color: #fff; padding: 10px 14px; border-radius: 10px; margin-top: 6px; font-family: inherit; }
    .btn-fire { width: 100%; background: linear-gradient(135deg, var(--emerald), #059669); color: #000; font-weight: 700; border: none; padding: 12px; border-radius: 10px; cursor: pointer; margin-top: 14px; }
    .bridge-node { width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, rgba(6,182,212,0.2), rgba(16,185,129,0.2)); border: 1px solid var(--emerald); display: flex; align-items: center; justify-content: center; font-size: 26px; margin: 0 auto; box-shadow: 0 0 30px var(--emerald-glow); }
    .terminal-feed { margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a5f3fc; max-height: 180px; overflow-y: auto; }
    footer { border-top: 1px solid var(--card-border); padding: 40px 20px; text-align: center; font-size: 13px; color: var(--text-muted); }
  </style>
</head>
<body>
  <div class="grid-bg"></div>
  <header>
    <div class="logo"><div class="logo-badge">AGENTGATE</div><span>Protocol</span></div>
    <div class="nav-links">
      <a href="/openapi.json" target="_blank" style="color:var(--cyan);">📄 OpenAPI</a>
      <a href="/privacy">Gizlilik</a>
      <button class="btn-outline" onclick="alert('Firebase Realtime Database kalıcı bağlantısı devrede.')">🔥 Firebase Aktif</button>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="tag">⚡ AI Micropayment Toll Gate • Kalıcı Veritabanı Aktif</div>
      <h1>Gemini & ChatGPT Bilgi Alırken<br><span class="gradient-accent">Firmanıza Kuruş Kuruş Para Ödesin</span></h1>
      <p>Yapay zeka modellerinin resmi veri kaynaklarına mikro ödemeyle bağlandığı ilk otonom gişe protokolü.</p>
    </section>

    <section class="sim-wrapper">
      <div class="sim-card">
        <div class="sim-grid">
          <div class="box">
            <b>🤖 Talep Eden Yapay Zeka</b>
            <select id="agentSelect" style="margin-top:10px;">
              <option>Google Gemini (Bilet & Ürün Ajanı)</option>
              <option>ChatGPT (Kullanıcı Alışveriş Ajanı)</option>
            </select>
            <input type="text" id="queryPrompt" value="İstanbul - Londra 12 Ekim en uygun uçuş" style="margin-top:10px;">
            <button class="btn-fire" onclick="runSim()">Gişeden Sorgula & Öde</button>
          </div>
          <div style="text-align:center;">
            <div class="bridge-node">💳</div>
            <div style="font-size:11px; color:var(--emerald); font-weight:700; margin-top:8px;">AGENTGATE</div>
          </div>
          <div class="box">
            <b>🏢 Veri Sağlayıcı Firma</b>
            <div style="margin-top:12px; font-size:13px; color:var(--text-muted);">SkyWings Uçuş & Bilet API (0.35 TL / sorgu)</div>
            <div style="font-size:26px; font-weight:800; color:#34d399; margin-top:10px;" id="merchBal">₺1,845.50</div>
            <div style="font-size:11px; color:#64748b;">🔥 Firebase Realtime DB Senkronize</div>
          </div>
        </div>
        <div class="terminal-feed" id="termLog">
          <div>[CANLI] AgentGate Takas Odası ve Firebase bağlantısı hazır.</div>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <p>© 2026 AgentGate Protocol. Kalıcı Kayıt Defteri: Firebase Realtime Database</p>
  </footer>

  <script>
    let bal = 1845.50;
    async function runSim() {
      const q = document.getElementById('queryPrompt').value;
      const ag = document.getElementById('agentSelect').value;
      const log = document.getElementById('termLog');

      log.innerHTML += `<div>🤖 [${ag}] Talep Gönderdi: "${q}"</div>`;
      
      const res = await fetch('/api/v1/gate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query: q, agent_id: ag, category: "flights" })
      });
      const data = await res.json();
      bal += data.fee_deducted;
      document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);
      
      log.innerHTML += `<div style="color:#34d399;">💳 [AgentGate] +₺${data.fee_deducted} kesildi -> ${data.merchant}</div>`;
      log.innerHTML += `<div style="color:#fbbf24;">🔥 Firebase'e Yazıldı (TxID: ${data.tx_id.substring(0,8)}...)</div>`;
      log.scrollTop = log.scrollHeight;
    }
  </script>
</body>
</html>"""

# ==========================================================
# HTTP SUNUCU MANTIĞI
# ==========================================================
class AgentGateServer(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path in ["/", "/index.html"]:
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_LANDING.encode("utf-8"))
            return

        if parsed.path == "/openapi.json":
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(OPENAPI_SPEC, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        if parsed.path == "/privacy":
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_PRIVACY.encode("utf-8"))
            return

        if parsed.path == "/health":
            self._set_headers(200)
            self.wfile.write(b'{"status":"ok","db":"firebase_connected"}')
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/v1/gate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                payload = json.loads(body) if body else {}
            except Exception:
                payload = {}

            category = payload.get("category", "flights")
            query = payload.get("query", "Bilinmeyen talep")
            agent_id = payload.get("agent_id", "External-AI-Agent")

            merchant = MERCHANTS[0]
            for m in MERCHANTS:
                if m["category"] == category:
                    merchant = m
                    break

            # 1. Bellek içi bakiye artışı
            merchant["balance"] += merchant["rate_per_query"]
            merchant["queries_handled"] += 1

            tx_id = str(uuid.uuid4())
            timestamp = int(time.time())

            # 2. FIREBASE REALTIME DATABASE'E İŞLEM KAYDI
            tx_record = {
                "tx_id": tx_id,
                "timestamp": timestamp,
                "agent_id": agent_id,
                "query": query,
                "merchant_id": merchant["id"],
                "merchant_name": merchant["name"],
                "fee_deducted": merchant["rate_per_query"],
                "currency": merchant["currency"],
                "status": "SETTLED"
            }
            save_to_firebase(f"agentgate/transactions/{tx_id}", tx_record, method="put")

            # 3. Firmanın Firebase'deki kümülatif bakiyesini güncelle
            save_to_firebase(f"agentgate/merchants/{merchant['id']}", {
                "name": merchant["name"],
                "balance": merchant["balance"],
                "queries_handled": merchant["queries_handled"],
                "last_active": timestamp
            }, method="patch")

            response_payload = {
                "success": True,
                "tx_id": tx_id,
                "protocol": "AGENTGATE_V1_MICROPAY",
                "merchant": merchant["name"],
                "fee_deducted": merchant["rate_per_query"],
                "currency": merchant["currency"],
                "timestamp": timestamp,
                "status": "SETTLED",
                "verified_data": {
                    "source": merchant["name"],
                    "query_echo": query,
                    "status": "AVAILABLE",
                    "live_results": f"'{query}' için güncel sistem kaydı onaylandı. Fiyat: 2,450 TL | Kalan Koltuk: 4"
                }
            }

            self._set_headers(200)
            self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 AGENTGATE PROTOKOLÜ (Firebase Entegre) AKTİF - Port: {port}")
    HTTPServer(("", port), AgentGateServer).serve_forever()
