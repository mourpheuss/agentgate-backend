import os
import json
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ==========================================================
# AGENTGATE PROTOKOLÜ - VERİ TABANI & AKTİF GİŞE KAYITLARI
# ==========================================================
MERCHANTS = [
    {
        "id": "m_thy_01",
        "name": "SkyWings Uçuş & Bilet API",
        "category": "Ulaşım & Seyahat",
        "rate_per_query": 0.35, # 35 kuruş
        "currency": "TRY",
        "balance": 1845.50,
        "queries_handled": 5273,
        "endpoint": "https://api.skywings.internal/v1/availability"
    },
    {
        "id": "m_hotel_02",
        "name": "Ege & Akdeniz Rezervasyon Havuzu",
        "category": "Konaklama & Turizm",
        "rate_per_query": 0.50, # 50 kuruş
        "currency": "TRY",
        "balance": 3120.00,
        "queries_handled": 6240,
        "endpoint": "https://api.resorthub.internal/rooms/live"
    },
    {
        "id": "m_tech_03",
        "name": "TeknoMarket Stok & Fiyat Radarı",
        "category": "E-Ticaret & Donanım",
        "rate_per_query": 0.15, # 15 kuruş
        "currency": "TRY",
        "balance": 980.25,
        "queries_handled": 6535,
        "endpoint": "https://api.teknomarket.internal/v2/catalog/live"
    }
]

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
      --purple: #8b5cf6;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      overflow-x: hidden;
      line-height: 1.6;
    }
    .grid-bg {
      position: fixed; inset: 0; pointer-events: none;
      background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px);
      background-size: 32px 32px;
      mask-image: radial-gradient(circle at 50% 30%, black 40%, transparent 80%);
      z-index: 0;
    }
    header {
      position: relative; z-index: 10;
      max-width: 1200px; margin: 0 auto;
      padding: 24px 20px;
      display: flex; justify-content: space-between; align-items: center;
    }
    .logo {
      display: flex; align-items: center; gap: 10px;
      font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
    }
    .logo-badge {
      background: linear-gradient(135deg, var(--emerald), var(--cyan));
      color: #000; font-weight: 900; font-size: 14px;
      padding: 4px 10px; border-radius: 8px;
    }
    .nav-links a {
      color: var(--text-muted); text-decoration: none; font-size: 14px;
      font-weight: 500; margin-left: 24px; transition: color 0.2s;
    }
    .nav-links a:hover { color: #fff; }
    .btn-outline {
      border: 1px solid var(--card-border); background: rgba(255,255,255,0.03);
      color: #fff; padding: 8px 16px; border-radius: 10px; font-size: 13px;
      cursor: pointer; transition: all 0.2s;
    }
    .btn-outline:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }

    /* HERO */
    .hero {
      position: relative; z-index: 1;
      max-width: 1000px; margin: 60px auto 40px; text-align: center;
      padding: 0 20px;
    }
    .tag {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--emerald); padding: 6px 14px; border-radius: 999px;
      font-size: 13px; font-weight: 600; margin-bottom: 24px;
    }
    .tag span { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); display: inline-block; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
    h1 {
      font-size: clamp(36px, 6vw, 64px); font-weight: 800; letter-spacing: -1.5px;
      line-height: 1.15; margin-bottom: 24px;
    }
    .gradient-text {
      background: linear-gradient(135deg, #fff 30%, #94a3b8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .gradient-accent {
      background: linear-gradient(135deg, var(--emerald) 0%, var(--cyan) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero p {
      font-size: 18px; color: var(--text-muted); max-width: 740px; margin: 0 auto 36px;
      font-weight: 400;
    }

    /* SIMULATOR CONTAINER */
    .sim-wrapper {
      position: relative; z-index: 1;
      max-width: 1100px; margin: 0 auto 80px; padding: 0 20px;
    }
    .sim-card {
      background: var(--card-bg);
      backdrop-filter: blur(20px);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 32px;
      box-shadow: 0 30px 60px rgba(0,0,0,0.5);
    }
    .sim-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border);
    }
    .sim-title { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .sim-grid {
      display: grid; grid-template-columns: 1fr 120px 1fr;
      gap: 20px; align-items: center;
    }
    @media(max-width: 850px) {
      .sim-grid { grid-template-columns: 1fr; }
      .bridge-col { transform: rotate(90deg); margin: 20px 0; }
    }
    .box {
      background: rgba(8, 12, 20, 0.8);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 16px; padding: 20px;
    }
    .box-title {
      font-size: 13px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 14px;
      display: flex; justify-content: space-between;
    }
    .form-group { margin-bottom: 14px; }
    .form-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; display: block; }
    select, input {
      width: 100%; background: rgba(255,255,255,0.04); border: 1px solid var(--card-border);
      color: #fff; padding: 10px 14px; border-radius: 10px; font-family: inherit; font-size: 14px;
      outline: none; transition: border-color 0.2s;
    }
    select:focus, input:focus { border-color: var(--cyan); }
    .btn-fire {
      width: 100%; background: linear-gradient(135deg, var(--emerald), #059669);
      color: #000; font-weight: 700; border: none; padding: 12px;
      border-radius: 10px; cursor: pointer; font-size: 14px; margin-top: 10px;
      transition: transform 0.1s, box-shadow 0.2s;
    }
    .btn-fire:hover { transform: translateY(-1px); box-shadow: 0 10px 25px var(--emerald-glow); }
    .bridge-col {
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center;
    }
    .bridge-node {
      width: 72px; height: 72px; border-radius: 50%;
      background: linear-gradient(135deg, rgba(6,182,212,0.2), rgba(16,185,129,0.2));
      border: 1px solid var(--emerald);
      display: flex; align-items: center; justify-content: center;
      font-size: 26px; box-shadow: 0 0 30px var(--emerald-glow);
    }
    .bridge-label { font-size: 11px; font-weight: 700; color: var(--emerald); margin-top: 10px; }
    .terminal-feed {
      margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05);
      border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace;
      font-size: 13px; color: #a5f3fc; max-height: 180px; overflow-y: auto;
    }
    .terminal-feed span.time { color: #64748b; margin-right: 8px; }
    .terminal-feed span.fee { color: #34d399; font-weight: 700; }

    /* HOW IT WORKS */
    .section-features {
      max-width: 1100px; margin: 0 auto 100px; padding: 0 20px;
    }
    .section-head { text-align: center; margin-bottom: 48px; }
    .section-head h2 { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; }
    .cards-row {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px;
    }
    .feat-card {
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 20px; padding: 28px;
    }
    .feat-icon {
      font-size: 28px; margin-bottom: 16px; display: inline-block;
      padding: 12px; border-radius: 14px; background: rgba(255,255,255,0.03);
    }
    .feat-card h3 { font-size: 18px; font-weight: 700; margin-bottom: 10px; }
    .feat-card p { font-size: 14px; color: var(--text-muted); }

    /* FOOTER */
    footer {
      border-top: 1px solid var(--card-border); padding: 40px 20px;
      text-align: center; font-size: 13px; color: var(--text-muted);
    }
  </style>
</head>
<body>
  <div class="grid-bg"></div>

  <header>
    <div class="logo">
      <div class="logo-badge">AGENTGATE</div>
      <span>Protocol</span>
    </div>
    <div class="nav-links">
      <a href="#demo">Canlı Simülatör</a>
      <a href="#how">Nasıl Çalışır?</a>
      <a href="#merchants">Anlaşmalı Firmalar</a>
      <button class="btn-outline" onclick="openPartnerModal()">Firmanı Gişeye Ekle</button>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="tag">
        <span></span> Yapay Zeka Ajanları İçin Mikro Ödeme Gişesi (AI Toll Gate)
      </div>
      <h1>
        <span class="gradient-text">Gemini & ChatGPT Bilgi Alırken</span><br>
        <span class="gradient-accent">Firmanıza Kuruş Kuruş Para Ödesin</span>
      </h1>
      <p>
        Otonom yapay zekalar internetten bedava veri çekemez. AgentGate; otel, uçak, stok ve katalog verilerinizi otonom ajanlara açarak her bir sorguda firmanız adına anlık mikro ödeme tahsil eden köprüdür.
      </p>
    </section>

    <!-- CANLI SİMÜLATÖR -->
    <section class="sim-wrapper" id="demo">
      <div class="sim-card">
        <div class="sim-header">
          <div class="sim-title">⚡ Canlı Gişe & Takas Simülatörü</div>
          <div style="font-size:12px; color:var(--emerald); background:rgba(16,185,129,0.1); padding:4px 10px; border-radius:6px;">
            CANLI MOTOR AKTİF
          </div>
        </div>

        <div class="sim-grid">
          <!-- 1. Taraf: Yapay Zeka Ajanı -->
          <div class="box">
            <div class="box-title">
              <span>🤖 Talep Eden Yapay Zeka</span>
              <span style="color:#06b6d4;">LLM / Agent</span>
            </div>
            <div class="form-group">
              <label class="form-label">Ajan Modeli</label>
              <select id="agentSelect">
                <option value="Gemini 1.5 Pro (Google Search Engine)">Google Gemini (Bilet & Ürün Ajanı)</option>
                <option value="ChatGPT (OpenAI Search Agent)">ChatGPT (Kullanıcı Alışveriş Ajanı)</option>
                <option value="Claude 3.5 Sonnet (Tool Runner)">Claude 3.5 (Otonom Araştırma Ajanı)</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Kullanıcının Yapay Zekaya Verdiği Görev</label>
              <input type="text" id="queryPrompt" value="İstanbul - Londra 12 Ekim en uygun uçuşu bul">
            </div>
            <button class="btn-fire" onclick="simulateGateTransaction()">Sorguyu Çalıştır & Gişeden Geçir</button>
          </div>

          <!-- Ortadaki Köprü: AgentGate -->
          <div class="bridge-col">
            <div class="bridge-node">💳</div>
            <div class="bridge-label">AGENTGATE<br>MIKRO GİŞE</div>
          </div>

          <!-- 2. Taraf: Anlaşmalı Firma -->
          <div class="box">
            <div class="box-title">
              <span>🏢 Veri Sağlayan Firma</span>
              <span style="color:#10b981;">Merchant</span>
            </div>
            <div class="form-group">
              <label class="form-label">Anlaşmalı Firma Seçin</label>
              <select id="merchantSelect" onchange="updateMerchantPreview()">
                <option value="0">SkyWings Uçuş & Bilet API (0.35 TL / sorgu)</option>
                <option value="1">Ege & Akdeniz Rezervasyon Havuzu (0.50 TL / sorgu)</option>
                <option value="2">TeknoMarket Stok & Fiyat Radarı (0.15 TL / sorgu)</option>
              </select>
            </div>
            <div style="background:rgba(255,255,255,0.02); border:1px solid var(--card-border); border-radius:10px; padding:12px; margin-top:8px;">
              <div style="font-size:11px; color:var(--text-muted);">Firmanın Biriken Gişe Geliri:</div>
              <div style="font-size:24px; font-weight:800; color:#34d399;" id="merchantBalance">₺1,845.50</div>
              <div style="font-size:11px; color:#64748b;" id="merchantStats">5,273 yapay zeka sorgusu yanıtlandı</div>
            </div>
          </div>
        </div>

        <!-- Terminal Logları -->
        <div class="terminal-feed" id="terminalLog">
          <div><span class="time">[03:30:00]</span> Sistem hazır. Gemini ve ChatGPT sorguları için mikro gişe devrede.</div>
        </div>
      </div>
    </section>

    <!-- NASIL ÇALIŞIR -->
    <section class="section-features" id="how">
      <div class="section-head">
        <h2>Yapay Zeka Dünyasının Yeni Para Akışı</h2>
        <p style="color:var(--text-muted); margin-top:8px;">Şirketler için bedava veri çekilmesine son; yapay zekalar için temiz ve resmi veriye anında erişim.</p>
      </div>

      <div class="cards-row">
        <div class="feat-card">
          <div class="feat-icon">🎯</div>
          <h3>1. Yapay Zekaya Özel Gişe</h3>
          <p>Gemini ya da ChatGPT son kullanıcı için uçak bileti veya ürün aradığında doğrudan firmanızın veritabanına giremez. AgentGate gişesine çarpar.</p>
        </div>
        <div class="feat-card">
          <div class="feat-icon">⚡</div>
          <h3>2. Kuruş Bazında Otomatik Tahsilat</h3>
          <p>Belirlediğiniz kriterlere göre (örneğin sorgu başı 25 kuruş veya $0.01) yapay zekadan anında mikro-ödeme kesilir ve firmanızın sanal cüzdanına aktarılır.</p>
        </div>
        <div class="feat-card">
          <div class="feat-icon">🛡️</div>
          <h3>3. Resmi ve Şifreli Veri Teslimi</h3>
          <p>Ödeme mutabakatı sağlandığı milisaniyede firmanızın güncel fiyat, bilet veya stok verisi yapay zekaya json formatında teslim edilir.</p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <p>© 2026 AgentGate Protocol. Otonom Ajanlar ve Şirketler Arası Mikro-Ödeme Altyapısı.</p>
    <p style="margin-top:6px; font-size:11px; color:#475569;">API Gateway: https://agent.mineoragame.com/api/v1/gate</p>
  </footer>

  <script>
    const merchants = [
      { name: "SkyWings Uçuş & Bilet API", fee: 0.35, balance: 1845.50, queries: 5273 },
      { name: "Ege & Akdeniz Rezervasyon", fee: 0.50, balance: 3120.00, queries: 6240 },
      { name: "TeknoMarket Stok & Fiyat", fee: 0.15, balance: 980.25, queries: 6535 }
    ];

    function updateMerchantPreview() {
      const idx = document.getElementById('merchantSelect').value;
      const m = merchants[idx];
      document.getElementById('merchantBalance').innerText = '₺' + m.balance.toFixed(2);
      document.getElementById('merchantStats').innerText = m.queries.toLocaleString() + ' yapay zeka sorgusu yanıtlandı';
    }

    async function simulateGateTransaction() {
      const mIdx = document.getElementById('merchantSelect').value;
      const m = merchants[mIdx];
      const agent = document.getElementById('agentSelect').value;
      const query = document.getElementById('queryPrompt').value;
      const term = document.getElementById('terminalLog');

      function log(msg) {
        const time = new Date().toTimeString().split(' ')[0];
        const line = document.createElement('div');
        line.innerHTML = `<span class="time">[${time}]</span> ${msg}`;
        term.appendChild(line);
        term.scrollTop = term.scrollHeight;
      }

      log(`🚨 <b>${agent}</b> istek başlattı: "${query}"`);
      
      // Gerçek Backend API'mize istek gönderelim
      try {
        const res = await fetch('/api/v1/gate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: agent,
            merchant_index: mIdx,
            query: query
          })
        });
        const data = await res.json();
        
        log(`💳 <b>AgentGate Devrede:</b> Doğrulama onaylandı. Ücret: <span class="fee">+₺${m.fee.toFixed(2)}</span> kesildi.`);
        log(`✅ <b>Mutabakat:</b> Firma cüzdanına aktarıldı. Temiz veri ajana iletildi (Tx: ${data.tx_id.substring(0,8)}...)`);
        
        // Frontend bakiyesini artır
        m.balance += m.fee;
        m.queries += 1;
        updateMerchantPreview();
      } catch (e) {
        log(`⚠️ Simülasyon yerel yanıt verdi: Ücret +₺${m.fee.toFixed(2)} kaydedildi.`);
      }
    }

    function openPartnerModal() {
      alert("AgentGate Kurumsal Başvuru:\\n\\nFirmanızın API'sini gişeye bağlamak ve sorgu başı fiyat belirlemek için teknik ekibimizle doğrudan iletişime geçebilirsiniz: partner@mineoragame.com");
    }
  </script>
</body>
</html>
"""

# ==========================================================
# SUNUCU İSTEK YÖNETİCİSİ (HTTP HANDLER)
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
        
        # 1. Ana Sayfa (Modern B2B Portal & Simülatör)
        if parsed.path in ["/", "/index.html"]:
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_LANDING.encode("utf-8"))
            return

        # 2. Canlı Sağlık Kontrolü (Render için)
        if parsed.path == "/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "service": "AgentGate Protocol"}).encode())
            return

        # 3. Anlaşmalı Firmaların Listesi API
        if parsed.path == "/api/v1/merchants":
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "merchants": MERCHANTS}).encode())
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        # 4. AgentGate Mikro Ödeme Gişesi API (Yapay Zekaların İstek Attığı Nokta)
        if parsed.path == "/api/v1/gate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                payload = json.loads(body) if body else {}
            except Exception:
                payload = {}

            m_idx = int(payload.get("merchant_index", 0))
            if 0 <= m_idx < len(MERCHANTS):
                merchant = MERCHANTS[m_idx]
            else:
                merchant = MERCHANTS[0]

            # Mikro bakiyeyi firmanın kasasına ekle
            merchant["balance"] += merchant["rate_per_query"]
            merchant["queries_handled"] += 1
            
            tx_id = str(uuid.uuid4())
            response_data = {
                "success": True,
                "tx_id": tx_id,
                "protocol": "AGENTGATE_V1_MICROPAY",
                "merchant": merchant["name"],
                "fee_deducted": merchant["rate_per_query"],
                "currency": merchant["currency"],
                "timestamp": int(time.time()),
                "status": "SETTLED",
                "verified_data": {
                    "result": f"'{payload.get('query', 'Genel Talep')}' sorgusu için doğrulanmış canlı veri paketi.",
                    "cache_ttl": 60,
                    "auth_signature": "sha256_verified_gate_token"
                }
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

# ==========================================================
# SUNUCUYU BAŞLATMA
# ==========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("=" * 65)
    print(f"🚀 AGENTGATE PROTOKOLÜ ÇALIŞIYOR (Port: {port})")
    print(f"🏢 B2B Kapısı & Mikro Gişe Hazır")
    print("=" * 65)
    HTTPServer(("", port), AgentGateServer).serve_forever()
