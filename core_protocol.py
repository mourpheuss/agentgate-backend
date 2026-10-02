import os
import json
import time
import uuid
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ==========================================================
# FIREBASE BAĞLANTISI (GİŞE KALICI DEFTERİ)
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
# FİRMALAR & AJAN ÖN ÖDEMELİ CÜZDANLARI
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
        "queries_handled": 5273
    },
    {
        "id": "m_ege_resort",
        "name": "Ege & Akdeniz Rezervasyon Havuzu",
        "domain": "egerezervasyon.com",
        "category": "hotels",
        "rate_per_query": 0.50,
        "currency": "TRY",
        "balance": 3120.00,
        "queries_handled": 6240
    },
    {
        "id": "m_teknoradar",
        "name": "TeknoMarket Stok & Fiyat Radarı",
        "domain": "teknomarket.internal",
        "category": "retail",
        "rate_per_query": 0.15,
        "currency": "TRY",
        "balance": 980.25,
        "queries_handled": 6535
    }
]

# Örnek hazır yüklü bir Ajan HGS Geçiş Kartı
AGENT_PASSES = {
    "ag_pass_demo123": {
        "agent_name": "OpenAI GPTBot Kurumsal Havuzu",
        "balance": 500.00,
        "currency": "TRY",
        "created_at": 1727830000
    }
}

OPENAPI_SPEC = {
    "openapi": "3.0.1",
    "info": {
        "title": "AgentGate AI Micropayment Toll Gate (HGS)",
        "description": "Yapay zeka modellerinin HTTP 402 HGS geçiş biletiyle web sitelerinden canlı veri çekmesini sağlayan takas odası.",
        "version": "v1.3.0"
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
                                    "query": {"type": "string"},
                                    "category": {"type": "string"},
                                    "agent_id": {"type": "string"}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Bariyer açıldı, ücret kesildi ve canlı veri teslim edildi."},
                    "402": {"description": "Ödeme Gerekli! Bakiye yetersiz veya HGS geçiş bileti eksik."}
                }
            }
        }
    }
}

HTML_PRIVACY = """<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><title>AgentGate HGS | Gizlilik</title><style>body{background:#07090e;color:#cbd5e1;font-family:sans-serif;max-width:800px;margin:50px auto;padding:20px;line-height:1.7;}h1{color:#fff;}a{color:#10b981;}</style></head><body><h1>AgentGate HGS Gizlilik Politikası</h1><p>AgentGate protokolü, web siteleri ile otonom botlar arasında mikro ödeme takası sağlar. Kullanıcıların kişisel verileri saklanmaz; yalnızca bot kimliği ve işlem tutarı deftere işlenir.</p><p><a href="/">← Ana Sayfaya Dön</a></p></body></html>"""

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
    .nav-links { display: flex; align-items: center; gap: 16px; }
    .nav-links a { color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; transition: color 0.2s; }
    .nav-links a:hover { color: #fff; }
    .btn-topup { background: linear-gradient(135deg, var(--cyan), #0284c7); color: #fff; border: none; font-weight: 700; padding: 10px 18px; border-radius: 10px; font-size: 13px; cursor: pointer; transition: 0.2s; }
    .btn-topup:hover { box-shadow: 0 0 20px rgba(6,182,212,0.4); transform: translateY(-1px); }
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
    .btn-fire-danger { width: 100%; background: linear-gradient(135deg, var(--rose), #be123c); color: #fff; font-weight: 700; border: none; padding: 11px; border-radius: 10px; cursor: pointer; margin-top: 10px; }
    .btn-fire-pass { width: 100%; background: linear-gradient(135deg, var(--emerald), #059669); color: #000; font-weight: 700; border: none; padding: 11px; border-radius: 10px; cursor: pointer; margin-top: 10px; }
    .bridge-node { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(16,185,129,0.2)); border: 2px dashed var(--amber); display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto; transition: 0.3s; }
    .terminal-feed { margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a5f3fc; max-height: 220px; overflow-y: auto; }

    /* MODAL */
    .modal-overlay { display: none; position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); justify-content: center; align-items: center; padding: 20px; }
    .modal-card { background: #0d121f; border: 1px solid rgba(255,255,255,0.15); width: 100%; max-width: 520px; border-radius: 20px; padding: 32px; position: relative; }
    .modal-close { position: absolute; top: 20px; right: 20px; background: none; border: none; color: #64748b; font-size: 20px; cursor: pointer; }
    .modal-close:hover { color: #fff; }
    .amount-pill { border: 1px solid var(--card-border); background: rgba(255,255,255,0.03); color: #fff; padding: 10px; border-radius: 10px; cursor: pointer; text-align: center; font-weight: 700; transition: 0.2s; }
    .amount-pill:hover, .amount-pill.active { border-color: var(--cyan); background: rgba(6,182,212,0.15); color: #a5f3fc; }

    /* CODE SNIPPET */
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
      <button class="btn-topup" onclick="openTopupModal()">💳 Ajanına Bakiye Yükle (Top-Up)</button>
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
            <b>🤖 Yapay Zeka Botu / Crawler</b>
            <select id="botSelect" style="margin-top:8px;">
              <option value="GPTBot (OpenAI Web Ajanı)">GPTBot / ChatGPT Search</option>
              <option value="Google-Extended (Gemini Crawler)">Google-Extended / Gemini Bot</option>
              <option value="ClaudeBot (Anthropic Research)">ClaudeBot</option>
            </select>
            <input type="text" id="targetPath" value="/fiyatlar/ayvalik-otelleri.json" style="margin-top:8px;">
            
            <div style="margin-top:14px; font-size:12px; color:var(--text-muted);">Test Seçeneği:</div>
            <button class="btn-fire-danger" onclick="testWithoutPass()">1. Bilet/Bakiye Olmadan Saldır (HTTP 402 Testi)</button>
            <button class="btn-fire-pass" onclick="testWithPass()">2. HGS Geçiş Kartıyla Geç (Otomatik Ödeme)</button>
          </div>

          <div style="text-align:center;">
            <div class="bridge-node" id="gateBarrier">🚧</div>
            <div style="font-size:11px; color:var(--amber); font-weight:700; margin-top:8px;" id="barrierText">HGS GİŞESİ</div>
          </div>

          <div class="box">
            <b>🏢 Web Siteniz (Otel / E-Ticaret)</b>
            <div style="font-size:13px; color:var(--text-muted); margin-top:8px;">Ziyaretçi: <b>Ücretsiz</b></div>
            <div style="font-size:13px; color:var(--emerald);">Bot Tarifesi: <b>0.35 TL / sorgu</b></div>
            <div style="font-size:26px; font-weight:800; color:#34d399; margin-top:10px;" id="merchBal">₺1,845.50</div>
            <div style="font-size:11px; color:#64748b;">🔥 Firebase Realtime Kasa</div>
          </div>
        </div>

        <div class="terminal-feed" id="termLog">
          <div>[04:15:00] HGS Gişe Kontrolörü devrede. HTTP 402 yönlendirmesi aktif.</div>
        </div>
      </div>
    </section>

    <!-- KOD PARÇASI: SİTENİZE NASIL EKLERSİNİZ -->
    <section class="snippet-section" id="snippet">
      <div class="snippet-card">
        <div style="font-size:20px; font-weight:800; color:#fff;">🛠️ Web Sitenizin Kapısına HGS Takmak Sadece 1 Satır</div>
        <p style="font-size:14px; color:var(--text-muted); margin-top:6px;">
          Botlar sitenize girdiğinde kapıdaki gişe HTTP 402 ile durdurur ve bakiye yüklemeleri için doğrudan <b>agent.mineoragame.com</b> gişesine sevk eder.
        </p>

        <pre><code>// Sitenize eklenecek Cloudflare / PHP / Node.js Gişe Kuralı
const AI_BOTS = ['GPTBot', 'Google-Extended', 'ClaudeBot', 'PerplexityBot'];
const userAgent = request.headers.get('User-Agent') || '';

if (AI_BOTS.some(bot => userAgent.includes(bot))) {
  const hgsPass = request.headers.get('X-AgentGate-Pass');
  if (!hgsPass) {
    // BARİYER: Bota HTTP 402 bas ve AgentGate portalına gönder!
    return new Response(JSON.stringify({
      error: "HTTP 402 Payment Required",
      message: "Bu sitenin canlı verisi botlar için ücretlidir.",
      toll_operator: "AgentGate HGS Protocol",
      topup_portal: "https://agent.mineoragame.com",
      fee: "0.35 TRY",
      required_header: "X-AgentGate-Pass"
    }), { status: 402, headers: { 'Content-Type': 'application/json' } });
  }
}
return fetch(request); // Normal insanlara ücretsiz aç</code></pre>
      </div>
    </section>
  </main>

  <!-- BAKİYE YÜKLEME MODALI (TOP-UP) -->
  <div class="modal-overlay" id="topupModal">
    <div class="modal-card">
      <button class="modal-close" onclick="closeTopupModal()">✕</button>
      <div style="font-size:20px; font-weight:800; margin-bottom:6px; color:#fff;">💳 Yapay Zeka Ajan Havuzuna Bakiye Yükle</div>
      <p style="font-size:13px; color:var(--text-muted); margin-bottom:18px;">
        Botlarınızın internetteki anlaşmalı yüzlerce otel, uçak ve e-ticaret sitesine takılmadan girebilmesi için ön ödemeli HGS geçiş bileti (Token) oluşturun.
      </p>

      <div style="margin-bottom:14px;">
        <label style="font-size:12px; color:var(--text-muted); display:block; margin-bottom:6px;">Şirket / Ajan Adı</label>
        <input type="text" id="topupAgentName" value="OpenAI / Gemini Crawler Agent">
      </div>

      <div style="margin-bottom:14px;">
        <label style="font-size:12px; color:var(--text-muted); display:block; margin-bottom:8px;">Yüklenecek Tutar (TL)</label>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
          <div class="amount-pill active" onclick="selectAmount(500, this)">₺500</div>
          <div class="amount-pill" onclick="selectAmount(2500, this)">₺2,500</div>
          <div class="amount-pill" onclick="selectAmount(10000, this)">₺10,000</div>
        </div>
      </div>

      <button class="btn-topup" style="width:100%; padding:14px; font-size:14px; margin-top:10px;" onclick="submitTopup()">
        Bakiyeyi Onayla & HGS Geçiş Kartı Üret
      </button>
    </div>
  </div>

  <footer>
    <p>© 2026 AgentGate HGS Protocol. Resmi Takas Uç Noktası: agent.mineoragame.com/api/v1/gate</p>
  </footer>

  <script>
    let bal = 1845.50;
    let selectedTopupAmount = 500;
    let activeAgentPass = "ag_pass_demo123";

    function openTopupModal() { document.getElementById('topupModal').style.display = 'flex'; }
    function closeTopupModal() { document.getElementById('topupModal').style.display = 'none'; }

    function selectAmount(amt, el) {
      selectedTopupAmount = amt;
      document.querySelectorAll('.amount-pill').forEach(p => p.classList.remove('active'));
      el.classList.add('active');
    }

    // BAKİYE YÜKLEME İŞLEMİ
    async function submitTopup() {
      const name = document.getElementById('topupAgentName').value.trim();
      const res = await fetch('/api/v1/topup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ agent_name: name, amount: selectedTopupAmount })
      });
      const data = await res.json();

      if (data.success) {
        activeAgentPass = data.pass_token;
        alert(`Bakiye Yüklendi!\\n\\nKart: ${data.pass_token}\\nYüklenen: ₺${data.amount}\\n\\nBotlarınız artık sitelerin kapısındaki AgentGate gişelerinden takılmadan geçebilir!`);
        closeTopupModal();

        const log = document.getElementById('termLog');
        log.innerHTML += `<div style="color:#38bdf8;">💳 <b>[Ajan Havuzu Yüklendi]:</b> ${data.pass_token} koduna +₺${data.amount} bakiye eklendi. (Firebase senkronize)</div>`;
        log.scrollTop = log.scrollHeight;
      }
    }

    // 1. TEST: BİLET OLMADAN SALDIRI (HTTP 402)
    async function testWithoutPass() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      log.innerHTML += `<div>🚨 <b>[${bot}]</b> siteye daldı: "${path}" (Bileti yok)</div>`;
      barrier.innerHTML = "🛑";
      barrier.style.borderColor = "#f43f5e";
      bText.innerText = "HTTP 402 DURDURULDU";
      bText.style.color = "#f43f5e";

      const res = await fetch('/api/v1/gate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query: path, agent_id: bot, pass_token: "" })
      });
      const data = await res.json();

      log.innerHTML += `<div style="color:#f43f5e;">⛔ <b>[HTTP 402 Payment Required]:</b> Geçiş reddedildi! Bota şu emir yollandı:</div>`;
      log.innerHTML += `<div style="color:#fbbf24; font-size:12px; margin-left:14px;">👉 "Giriş için https://agent.mineoragame.com üzerinden bakiye yükleyin."</div>`;
      log.scrollTop = log.scrollHeight;
    }

    // 2. TEST: HGS KARTIYLA GEÇİŞ
    async function testWithPass() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      log.innerHTML += `<div>🚙 <b>[${bot}]</b> HGS Geçiş Kartını okuttu: "${activeAgentPass}"</div>`;

      const res = await fetch('/api/v1/gate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-AgentGate-Pass': activeAgentPass},
        body: JSON.stringify({ query: path, agent_id: bot, pass_token: activeAgentPass })
      });
      const data = await res.json();

      if (data.success) {
        bal += data.fee_deducted;
        document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);

        barrier.innerHTML = "🟢";
        barrier.style.borderColor = "#10b981";
        bText.innerText = "HGS GEÇİŞİ ONAYLANDI";
        bText.style.color = "#10b981";

        log.innerHTML += `<div style="color:#34d399;">💳 <b>[Bakiye Düştü]:</b> Ajan havuzundan -₺${data.fee_deducted.toFixed(2)} düşüldü -> Firmanın kasasına eklendi.</div>`;
        log.innerHTML += `<div style="color:#a5f3fc;">📦 Bariyer açıldı, canlı veri şifrelenip bota verildi. (TxID: ${data.tx_id.substring(0,8)}...)</div>`;
      }
      log.scrollTop = log.scrollHeight;
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

        # 1. AJAN BAKİYE YÜKLEME KAPISI (TOP-UP ENDPOINT)
        if parsed.path == "/api/v1/topup":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            pass_token = "ag_pass_" + str(uuid.uuid4()).replace("-", "")[:12]
            amount = float(payload.get("amount", 500))
            agent_name = payload.get("agent_name", "Otonom Ajan Havuzu")

            wallet_data = {
                "pass_token": pass_token,
                "agent_name": agent_name,
                "balance": amount,
                "currency": "TRY",
                "created_at": int(time.time())
            }
            AGENT_PASSES[pass_token] = wallet_data

            # Firebase'e kaydet
            save_to_firebase(f"agentgate/agent_wallets/{pass_token}", wallet_data, method="put")

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "pass_token": pass_token,
                "amount": amount,
                "currency": "TRY",
                "message": "Bakiye havuzu oluşturuldu. X-AgentGate-Pass başlığı ile kullanabilirsiniz."
            }).encode("utf-8"))
            return

        # 2. HGS GİŞE GEÇİŞ KAPISI
        if parsed.path == "/api/v1/gate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            pass_header = self.headers.get("X-AgentGate-Pass") or payload.get("pass_token", "")
            query = payload.get("query", "Bilinmeyen istek")
            agent_id = payload.get("agent_id", "GPTBot-Crawler")

            # HGS Kartı yoksa -> HTTP 402 PAYMENT REQUIRED DÖN!
            if not pass_header or pass_header not in AGENT_PASSES:
                self._set_headers(402)
                response_402 = {
                    "status": 402,
                    "error": "Payment Required",
                    "message": "Bu sitenin verisi otonom yapay zeka botları için ücretlidir.",
                    "toll_operator": "AgentGate Protocol",
                    "action_required": {
                        "step_1": "Bakiye yükleyip geçerli bir HGS kartı (X-AgentGate-Pass) alın.",
                        "topup_portal": "https://agent.mineoragame.com",
                        "fee_per_request": "0.35 TRY",
                        "required_header": "X-AgentGate-Pass"
                    }
                }
                self.wfile.write(json.dumps(response_402, ensure_ascii=False).encode("utf-8"))
                return

            # HGS Kartı var -> Bakiyeyi kontrol et ve düş
            agent_wallet = AGENT_PASSES[pass_header]
            fee = 0.35

            if agent_wallet["balance"] < fee:
                self._set_headers(402)
                self.wfile.write(json.dumps({
                    "status": 402,
                    "error": "Insufficient Funds",
                    "message": "HGS Kartınızdaki bakiye tükendi. Lütfen bakiye yükleyin: https://agent.mineoragame.com"
                }).encode("utf-8"))
                return

            # Bakiyeleri güncelle
            agent_wallet["balance"] -= fee
            merchant = MERCHANTS[0]
            merchant["balance"] += fee
            merchant["queries_handled"] += 1

            tx_id = str(uuid.uuid4())
            timestamp = int(time.time())

            # Firebase'e işlemi yaz
            tx_record = {
                "tx_id": tx_id,
                "timestamp": timestamp,
                "agent_id": agent_id,
                "pass_token": pass_header,
                "query": query,
                "toll_fee": fee,
                "merchant": merchant["name"],
                "remaining_agent_balance": agent_wallet["balance"],
                "status": "HGS_CLEARED"
            }
            save_to_firebase(f"agentgate/hgs_transactions/{tx_id}", tx_record, method="put")

            # Firebase cüzdanını güncelle
            save_to_firebase(f"agentgate/agent_wallets/{pass_header}", {
                "balance": agent_wallet["balance"],
                "last_used": timestamp
            }, method="patch")

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "tx_id": tx_id,
                "protocol": "AGENTGATE_HGS_V1",
                "status": "CLEARED",
                "fee_deducted": fee,
                "remaining_pass_balance": agent_wallet["balance"],
                "currency": "TRY",
                "merchant": merchant["name"]
            }, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 AGENTGATE HGS GİŞESİ & TOP-UP AKTİF - Port: {port}")
    HTTPServer(("", port), AgentGateServer).serve_forever()
