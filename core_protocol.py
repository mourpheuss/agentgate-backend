import os
import json
import time
import uuid
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ==========================================================
# FIREBASE BAĞLANTISI (GİŞE DEFTERİ)
# ==========================================================
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET", "Hl2qgV6ipQkRzssYSSHgJDmdr363LC9sexWm2dY1")
FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL", "https://mineora-web-default-rtdb.firebaseio.com").rstrip("/")

def save_to_firebase(path, data, method="post"):
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
        print(f"⚠️ Firebase Hatası: {e}")
        return None

# ==========================================================
# FİRMALAR & HGS GİŞELERİ
# ==========================================================
MERCHANTS = [
    {
        "id": "m_skywings",
        "name": "SkyWings Uçuş & Bilet API",
        "domain": "skywings.com.tr",
        "category": "flights",
        "rate_per_query": 0.35,
        "currency": "TRY",
        "balance": 1845.50,
        "queries_handled": 5273,
        "api_key": "ag_live_skywings_pass"
    },
    {
        "id": "m_ege_resort",
        "name": "Ege & Akdeniz Rezervasyon Havuzu",
        "domain": "egerezervasyon.com",
        "category": "hotels",
        "rate_per_query": 0.50,
        "currency": "TRY",
        "balance": 3120.00,
        "queries_handled": 6240,
        "api_key": "ag_live_egeresort_pass"
    },
    {
        "id": "m_teknoradar",
        "name": "TeknoMarket Stok & Fiyat Radarı",
        "domain": "teknomarket.internal",
        "category": "retail",
        "rate_per_query": 0.15,
        "currency": "TRY",
        "balance": 980.25,
        "queries_handled": 6535,
        "api_key": "ag_live_teknoradar_pass"
    }
]

# OPENAPI 3.0
OPENAPI_SPEC = {
    "openapi": "3.0.1",
    "info": {
        "title": "AgentGate AI Micropayment Toll Gate (HGS)",
        "description": "Yapay zeka botlarının web sitelerinden veri çekerken HTTP 402 ödemesi yaptığı otonom gişe.",
        "version": "v1.2.0"
    },
    "servers": [{"url": "https://agent.mineoragame.com"}],
    "paths": {
        "/api/v1/gate": {
            "post": {
                "summary": "HGS Otoban Gişesi Geçişi",
                "operationId": "passHgsGate",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Talep edilen veri"},
                                    "category": {"type": "string"},
                                    "agent_id": {"type": "string", "description": "Örn: GPTBot, Google-Extended"}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Bariyer açıldı, ücret kesildi ve canlı veri verildi."}
                }
            }
        }
    }
}

HTML_PRIVACY = """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>AgentGate HGS | Gizlilik</title><style>body{background:#07090e;color:#cbd5e1;font-family:sans-serif;max-width:800px;margin:50px auto;padding:20px;line-height:1.7;}h1{color:#fff;}a{color:#10b981;}</style></head><body><h1>AgentGate HGS Gizlilik Politikası</h1><p>AgentGate protokolü, web siteleri ile otonom botlar arasında mikro-ödeme takası sağlar. Kullanıcıların kişisel verileri saklanmaz; yalnızca bot kimliği ve işlem tutarı deftere işlenir.</p><p><a href="/">← Ana Sayfaya Dön</a></p></body></html>"""

HTML_LANDING = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgentGate HGS | Yapay Zekalar İçin Otoban Gişesi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #07090e;
      --card-bg: rgba(16, 21, 33, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --cyan: #06b6d4;
      --amber: #f59e0b;
      --rose: #f43f5e;
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
    .btn-register { background: linear-gradient(135deg, var(--emerald), #059669); color: #000; border: none; font-weight: 700; padding: 10px 18px; border-radius: 10px; font-size: 13px; cursor: pointer; transition: 0.2s; }
    .hero { position: relative; z-index: 1; max-width: 1050px; margin: 50px auto 35px; text-align: center; padding: 0 20px; }
    .tag { display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: var(--emerald); padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 24px; }
    h1 { font-size: clamp(34px, 5.5vw, 58px); font-weight: 800; letter-spacing: -1.5px; line-height: 1.15; margin-bottom: 20px; }
    .gradient-accent { background: linear-gradient(135deg, var(--emerald) 0%, var(--cyan) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { font-size: 18px; color: var(--text-muted); max-width: 780px; margin: 0 auto; }

    /* HGS SIMULATOR */
    .sim-wrapper { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto 60px; padding: 0 20px; }
    .sim-card { background: var(--card-bg); backdrop-filter: blur(20px); border: 1px solid var(--card-border); border-radius: 24px; padding: 32px; box-shadow: 0 30px 60px rgba(0,0,0,0.5); }
    .sim-grid { display: grid; grid-template-columns: 1fr 140px 1fr; gap: 20px; align-items: center; }
    @media(max-width: 850px) { .sim-grid { grid-template-columns: 1fr; } }
    .box { background: rgba(8, 12, 20, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; }
    select, input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid var(--card-border); color: #fff; padding: 10px 14px; border-radius: 10px; margin-top: 6px; font-family: inherit; }
    .btn-fire { width: 100%; background: linear-gradient(135deg, var(--amber), #d97706); color: #000; font-weight: 700; border: none; padding: 12px; border-radius: 10px; cursor: pointer; margin-top: 14px; }
    .bridge-node { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(16,185,129,0.2)); border: 2px dashed var(--amber); display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto; }
    .terminal-feed { margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a5f3fc; max-height: 200px; overflow-y: auto; }

    /* CODE SNIPPET SECTION */
    .snippet-section { max-width: 1100px; margin: 0 auto 80px; padding: 0 20px; position: relative; z-index: 1; }
    .snippet-card { background: rgba(12, 17, 29, 0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 28px; }
    pre { background: #020408; padding: 16px; border-radius: 12px; overflow-x: auto; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 13px; margin-top: 12px; border: 1px solid rgba(255,255,255,0.05); }

    footer { border-top: 1px solid var(--card-border); padding: 40px 20px; text-align: center; font-size: 13px; color: var(--text-muted); }
  </style>
</head>
<body>
  <div class="grid-bg"></div>
  <header>
    <div class="logo"><div class="logo-badge">AGENTGATE</div><span>HGS Protokolü</span></div>
    <div class="nav-links">
      <a href="#snippet">Sitenize Gişe Kurun</a>
      <a href="/openapi.json" target="_blank" style="color:var(--cyan);">OpenAPI</a>
      <a href="/privacy">Gizlilik</a>
      <button class="btn-register" onclick="alert('HGS Kurulum Asistanı hazır!')">HGS Etiketi Al</button>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="tag">🛡️ HTTP 402 Standartlı Otonom Bot Gişesi</div>
      <h1>Web Sitenizi Kapatmayın,<br><span class="gradient-accent">Kapısına Yapay Zeka HGS'si Koyun</span></h1>
      <p>
        İnsanlar sitenizi ücretsiz gezmeye devam etsin; Gemini, ChatGPT ve arama botları verinizi her çektiğinde HGS gişesinden kuruş bazında ödeme yapsın.
      </p>
    </section>

    <!-- HGS CANLI SİMÜLASYONU -->
    <section class="sim-wrapper">
      <div class="sim-card">
        <div class="sim-grid">
          <div class="box">
            <b>🤖 Yaklaşan Yapay Zeka Botu</b>
            <select id="botSelect" style="margin-top:10px;">
              <option value="GPTBot (OpenAI Web Ajanı)">GPTBot / ChatGPT Search</option>
              <option value="Google-Extended (Gemini Crawler)">Google-Extended / Gemini Bot</option>
              <option value="ClaudeBot (Anthropic Research)">ClaudeBot</option>
            </select>
            <input type="text" id="targetPath" value="/fiyatlar/ayvalik-otelleri.json" style="margin-top:10px;">
            <button class="btn-fire" onclick="simulateHgsPass()">Bot Olarak Siteye Saldır (Test Et)</button>
          </div>

          <div style="text-align:center;">
            <div class="bridge-node" id="gateBarrier">🚧</div>
            <div style="font-size:11px; color:var(--amber); font-weight:700; margin-top:8px;" id="barrierText">HGS BARİYERİ</div>
          </div>

          <div class="box">
            <b>🏢 Web Siteniz (Otel / E-Ticaret)</b>
            <div style="font-size:13px; color:var(--text-muted); margin-top:8px;">Durum: <b>Normal Ziyaretçiye Ücretsiz</b></div>
            <div style="font-size:13px; color:var(--emerald);">Bot Tarifesi: <b>0.35 TL / sorgu</b></div>
            <div style="font-size:26px; font-weight:800; color:#34d399; margin-top:10px;" id="merchBal">₺1,845.50</div>
            <div style="font-size:11px; color:#64748b;">🔥 Firebase Realtime Kasa</div>
          </div>
        </div>

        <div class="terminal-feed" id="termLog">
          <div>[04:00:00] HGS Gişe Kontrolörü devrede. HTTP 402 kapısı açık.</div>
        </div>
      </div>
    </section>

    <!-- KOD PARÇASI: SİTENİZE NASIL EKLERSİNİZ -->
    <section class="snippet-section" id="snippet">
      <div class="snippet-card">
        <div style="font-size:20px; font-weight:800; color:#fff;">🛠️ Web Sitenizin Kapısına HGS Takmak Sadece 1 Satır</div>
        <p style="font-size:14px; color:var(--text-muted); margin-top:6px;">
          Cloudflare Worker'ınıza, Nginx sunucunuza veya sitenizin koduna ekleyin; botlar içeri sızdığında AgentGate bakiye tahsil etmeden veriyi vermez.
        </p>

        <pre><code>// Örnek: Cloudflare / Node.js / PHP Gişe Kuralı
const AI_BOTS = ['GPTBot', 'Google-Extended', 'ClaudeBot', 'PerplexityBot'];
const userAgent = request.headers.get('User-Agent') || '';

if (AI_BOTS.some(bot => userAgent.includes(bot))) {
  const hgsPass = request.headers.get('X-AgentGate-Pass');
  if (!hgsPass) {
    // BARİYERİ İNDİR: Yapay zekadan para iste
    return new Response(JSON.stringify({
      error: "HTTP 402 Payment Required",
      message: "Bu sitenin verisi otonom botlar için ücretlidir.",
      toll_gate: "https://agent.mineoragame.com/api/v1/gate",
      fee: "0.35 TRY"
    }), { status: 402, headers: { 'Content-Type': 'application/json' } });
  }
}
// Normal insansa siteyi ücretsiz aç:
return fetch(request);</code></pre>
      </div>
    </section>
  </main>

  <footer>
    <p>© 2026 AgentGate HGS Protocol. Resmi Takas Uç Noktası: agent.mineoragame.com/api/v1/gate</p>
  </footer>

  <script>
    let bal = 1845.50;

    async function simulateHgsPass() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      function addLog(msg) {
        log.innerHTML += `<div>${msg}</div>`;
        log.scrollTop = log.scrollHeight;
      }

      // 1. Bot veriyi bedavaya çekmeye çalışır
      addLog(`🚨 <b>[${bot}]</b> siteye daldı: "${path}" (Bedava veri istiyor)`);
      barrier.innerHTML = "🛑";
      barrier.style.borderColor = "#f43f5e";
      bText.innerText = "HTTP 402 BLOKAJI";
      bText.style.color = "#f43f5e";

      await new Promise(r => setTimeout(r, 600));

      addLog(`<span style="color:#f43f5e;">⛔ <b>[HTTP 402 Payment Required]</b> Bot durduruldu! Bedava geçiş yok.</span>`);

      await new Promise(r => setTimeout(r, 800));

      // 2. AgentGate devreye girer ve ödemeyi çözer
      addLog(`💳 <b>[AgentGate HGS]:</b> Botun cüzdanından 0.35 TL tahsil edildi.`);
      
      const res = await fetch('/api/v1/gate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query: path, agent_id: bot, category: "flights" })
      });
      const data = await res.json();

      bal += data.fee_deducted;
      document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);

      barrier.innerHTML = "🟢";
      barrier.style.borderColor = "#10b981";
      bText.innerText = "BARİYER AÇILDI";
      bText.style.color = "#10b981";

      addLog(`<span style="color:#34d399;">✅ <b>Bariyer Açıldı:</b> Otelin kasasına +₺${data.fee_deducted} eklendi. (TxID: ${data.tx_id.substring(0,8)}...)</span>`);
      addLog(`<span style="color:#a5f3fc;">📦 Temiz veri şifrelenip bota verildi. İşlem tamamlandı.</span>`);
    }
  </script>
</body>
</html>"""

# ==========================================================
# SUNUCU İSTEK YÖNETİCİSİ
# ==========================================================
class AgentGateServer(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-AgentGate-Pass")
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
            self.wfile.write(b'{"status":"ok","hgs":"active"}')
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        # HGS GİŞE GEÇİŞ KAPISI
        if parsed.path == "/api/v1/gate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            category = payload.get("category", "flights")
            query = payload.get("query", "Bilinmeyen istek")
            agent_id = payload.get("agent_id", "GPTBot-Crawler")

            merchant = MERCHANTS[0]
            merchant["balance"] += merchant["rate_per_query"]
            merchant["queries_handled"] += 1

            tx_id = str(uuid.uuid4())
            timestamp = int(time.time())

            # Firebase'e HGS logu kaydet
            tx_record = {
                "tx_id": tx_id,
                "timestamp": timestamp,
                "agent_id": agent_id,
                "query": query,
                "toll_fee": merchant["rate_per_query"],
                "merchant": merchant["name"],
                "status": "HGS_CLEARED"
            }
            save_to_firebase(f"agentgate/hgs_transactions/{tx_id}", tx_record, method="put")

            response_payload = {
                "success": True,
                "tx_id": tx_id,
                "protocol": "AGENTGATE_HGS_V1",
                "status": "CLEARED",
                "fee_deducted": merchant["rate_per_query"],
                "currency": "TRY",
                "merchant": merchant["name"]
            }

            self._set_headers(200)
            self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 AGENTGATE HGS GİŞESİ AKTİF - Port: {port}")
    HTTPServer(("", port), AgentGateServer).serve_forever()
