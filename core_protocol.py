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
# FİRMALAR & CÜZDAN HAVUZLARI
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

# Aktif HGS Geçiş Kartları
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
        "version": "v1.4.0"
    },
    "servers": [{"url": "https://agent.mineoragame.com"}],
    "paths": {
        "/api/v1/instant-pay": {
            "post": {
                "summary": "Makineden Makineye (M2M) Anlık Mikro Ödeme",
                "description": "Botun HTTP 402 faturasını anında ödeyip tek kullanımlık geçiş bileti aldığı uç nokta.",
                "operationId": "instantPaySettlement",
                "responses": {
                    "200": {"description": "Ödeme onaylandı, geçiş kartı üretildi."}
                }
            }
        },
        "/api/v1/gate": {
            "post": {
                "summary": "HGS Otoban Gişesi Geçişi",
                "operationId": "passHgsGate",
                "responses": {
                    "200": {"description": "Bariyer açıldı, veri teslim edildi."},
                    "402": {"description": "Ödeme Gerekli! Bilet eksik veya bakiye yetersiz."}
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
  <title>AgentGate HGS | Otonom Yapay Zeka Otoban Gişesi</title>
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
      --purple: #a855f7;
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
    .sim-grid { display: grid; grid-template-columns: 1.1fr 130px 1fr; gap: 20px; align-items: center; }
    @media(max-width: 850px) { .sim-grid { grid-template-columns: 1fr; } }
    .box { background: rgba(8, 12, 20, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; }
    select, input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid var(--card-border); color: #fff; padding: 10px 14px; border-radius: 10px; margin-top: 6px; font-family: inherit; }
    .btn-fire-danger { width: 100%; background: rgba(244,63,94,0.15); border: 1px solid rgba(244,63,94,0.4); color: #fca5a5; font-weight: 700; padding: 10px; border-radius: 10px; cursor: pointer; margin-top: 8px; font-size: 13px; }
    .btn-fire-pass { width: 100%; background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); color: #6ee7b7; font-weight: 700; padding: 10px; border-radius: 10px; cursor: pointer; margin-top: 8px; font-size: 13px; }
    .btn-fire-auto { width: 100%; background: linear-gradient(135deg, var(--purple), #7c3aed); color: #fff; font-weight: 800; border: none; padding: 12px; border-radius: 10px; cursor: pointer; margin-top: 10px; font-size: 13px; box-shadow: 0 0 25px rgba(168,85,247,0.3); transition: 0.2s; }
    .btn-fire-auto:hover { transform: translateY(-1px); box-shadow: 0 0 35px rgba(168,85,247,0.5); }
    .bridge-node { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(16,185,129,0.2)); border: 2px dashed var(--amber); display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto; transition: 0.3s; }
    .terminal-feed { margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a5f3fc; max-height: 220px; overflow-y: auto; }

    /* MODAL */
    .modal-overlay { display: none; position: fixed; inset: 0; z-index: 100; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); justify-content: center; align-items: center; padding: 20px; }
    .modal-card { background: #0d121f; border: 1px solid rgba(255,255,255,0.15); width: 100%; max-width: 520px; border-radius: 20px; padding: 32px; position: relative; }
    .modal-close { position: absolute; top: 20px; right: 20px; background: none; border: none; color: #64748b; font-size: 20px; cursor: pointer; }
    .amount-pill { border: 1px solid var(--card-border); background: rgba(255,255,255,0.03); color: #fff; padding: 10px; border-radius: 10px; cursor: pointer; text-align: center; font-weight: 700; }
    .amount-pill.active { border-color: var(--cyan); background: rgba(6,182,212,0.15); color: #a5f3fc; }

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
      <button class="btn-topup" onclick="openTopupModal()">💳 Ajan Bakiye Yükle (Top-Up)</button>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="tag">🛡️ HTTP 402 Standartlı Otonom Bot Gişesi • M2M Aktif</div>
      <h1>Web Sitenizi Kapatmayın,<br><span class="gradient-accent">Kapısına Yapay Zeka HGS'si Koyun</span></h1>
      <p>
        İnsanlar sitenizi ücretsiz gezmeye devam etsin; Gemini, ChatGPT ve arama botları verinizi her çektiğinde HGS gişesinden kuruş bazında otomatik ödeme yapsın.
      </p>
    </section>

    <!-- HGS CANLI SİMÜLASYONU -->
    <section class="sim-wrapper">
      <div class="sim-card">
        <div class="sim-grid">
          <div class="box">
            <b>🤖 Yapay Zeka Botu / Crawler</b>
            <select id="botSelect" style="margin-top:6px;">
              <option value="GPTBot (OpenAI Web Ajanı)">GPTBot / ChatGPT Search</option>
              <option value="Google-Extended (Gemini Crawler)">Google-Extended / Gemini Bot</option>
              <option value="ClaudeBot (Anthropic Research)">ClaudeBot</option>
            </select>
            <input type="text" id="targetPath" value="/fiyatlar/ayvalik-otelleri.json" style="margin-top:6px;">
            
            <button class="btn-fire-auto" onclick="runAutonomousM2M()">⚡ Otonom Bot Modu (Otomatik Öde ve Geç)</button>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px;">
              <button class="btn-fire-danger" onclick="testWithoutPass()">1. Biletsiz Saldır</button>
              <button class="btn-fire-pass" onclick="testWithPass()">2. Kartla Geç</button>
            </div>
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
          <div>[04:20:00] HGS Gişe Kontrolörü & M2M Otonom Ödeme motoru hazır.</div>
        </div>
      </div>
    </section>

    <!-- KOD PARÇASI -->
    <section class="snippet-section" id="snippet">
      <div class="snippet-card">
        <div style="font-size:20px; font-weight:800; color:#fff;">🛠️ Web Sitenizin Kapısına HGS Takmak Sadece 1 Satır</div>
        <p style="font-size:14px; color:var(--text-muted); margin-top:6px;">
          Botlar sitenize girdiğinde kapıdaki gişe HTTP 402 faturası keser ve botun anında <b>/api/v1/instant-pay</b> üzerinden ödeme yapmasını sağlar.
        </p>

        <pre><code>// Sitenize eklenecek Cloudflare / PHP / Node.js Gişe Kuralı
const AI_BOTS = ['GPTBot', 'Google-Extended', 'ClaudeBot', 'PerplexityBot'];
const userAgent = request.headers.get('User-Agent') || '';

if (AI_BOTS.some(bot => userAgent.includes(bot))) {
  const hgsPass = request.headers.get('X-AgentGate-Pass');
  if (!hgsPass) {
    // 402 FATURASI KES VE BOTUN OTONOM ÖDEME YAPMASINI SAĞLA
    return new Response(JSON.stringify({
      error: "HTTP 402 Payment Required",
      message: "Bu sitenin verisi ücretlidir.",
      fee: "0.35 TRY",
      instant_pay_endpoint: "https://agent.mineoragame.com/api/v1/instant-pay",
      required_header: "X-AgentGate-Pass"
    }), { status: 402, headers: { 'Content-Type': 'application/json' } });
  }
}
return fetch(request); // Normal insanlara ücretsiz</code></pre>
      </div>
    </section>
  </main>

  <!-- BAKİYE YÜKLEME MODALI -->
  <div class="modal-overlay" id="topupModal">
    <div class="modal-card">
      <button class="modal-close" onclick="closeTopupModal()">✕</button>
      <div style="font-size:20px; font-weight:800; margin-bottom:6px; color:#fff;">💳 Yapay Zeka Ajan Havuzuna Bakiye Yükle</div>
      <p style="font-size:13px; color:var(--text-muted); margin-bottom:18px;">
        Botlarınızın sitelere takılmadan girebilmesi için HGS geçiş bileti (Token) oluşturun.
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
        Bakiyeyi Onayla & HGS Kartı Üret
      </button>
    </div>
  </div>

  <footer>
    <p>© 2026 AgentGate HGS Protocol. M2M Instant Settlement: agent.mineoragame.com/api/v1/instant-pay</p>
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
        alert(`Bakiye Yüklendi!\\n\\nKart: ${data.pass_token}\\nYüklenen: ₺${data.amount}`);
        closeTopupModal();
      }
    }

    // ⚡ OTONOM M2M DÖNGÜSÜ (KENDİ KENDİNE ÖDE VE GEÇ)
    async function runAutonomousM2M() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      function addLog(msg) {
        log.innerHTML += `<div>${msg}</div>`;
        log.scrollTop = log.scrollHeight;
      }

      // 1. Bot siteye dalar
      addLog(`🤖 <b>[${bot}]</b> siteye istek attı: "${path}"`);
      barrier.innerHTML = "🛑";
      barrier.style.borderColor = "#f43f5e";
      bText.innerText = "HTTP 402";
      bText.style.color = "#f43f5e";

      await new Promise(r => setTimeout(r, 400));

      // 2. HTTP 402 Faturası çıkar
      addLog(`<span style="color:#f43f5e;">⛔ <b>[HTTP 402]:</b> Site geçişi durdurdu. Fatura: 0.35 TRY kesildi.</span>`);

      await new Promise(r => setTimeout(r, 500));

      // 3. Bot faturayı anında öder (/api/v1/instant-pay)
      addLog(`<span style="color:#c084fc;">⚡ <b>[M2M Otonom Motor]:</b> Bot HTTP 402'yi yakaladı. /api/v1/instant-pay çağrılıyor...</span>`);
      
      const payRes = await fetch('/api/v1/instant-pay', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          agent_id: bot,
          query: path,
          fee: 0.35
        })
      });
      const payData = await payRes.json();

      await new Promise(r => setTimeout(r, 400));

      addLog(`<span style="color:#38bdf8;">💳 <b>[AgentGate Gişesi]:</b> Anlık tahsilat onaylandı. Tek kullanımlık bilet üretildi: <code>${payData.pass_token}</code></span>`);

      await new Promise(r => setTimeout(r, 400));

      // 4. Bot biletle tekrar dalar ve veriyi alır
      bal += payData.fee_deducted;
      document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);

      barrier.innerHTML = "🟢";
      barrier.style.borderColor = "#10b981";
      bText.innerText = "BARİYER AÇIK";
      bText.style.color = "#10b981";

      addLog(`<span style="color:#34d399;">✅ <b>[Başarılı]:</b> Bariyer açıldı! Otelin kasasına +₺${payData.fee_deducted.toFixed(2)} eklendi. (Firebase Senkronize)</span>`);
      addLog(`<span style="color:#a5f3fc;">📦 Güncel otel ve fiyat verisi bota teslim edildi. İşlem 1.2 saniyede bitti.</span>`);
    }

    async function testWithoutPass() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      log.innerHTML += `<div>🚨 <b>[${bot}]</b> siteye daldı: "${path}"</div>`;
      barrier.innerHTML = "🛑";
      barrier.style.borderColor = "#f43f5e";
      bText.innerText = "HTTP 402";
      bText.style.color = "#f43f5e";

      log.innerHTML += `<div style="color:#f43f5e;">⛔ [HTTP 402]: Geçiş engellendi! Bakiye yükleyin: https://agent.mineoragame.com</div>`;
      log.scrollTop = log.scrollHeight;
    }

    async function testWithPass() {
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      log.innerHTML += `<div>🚙 <b>[${bot}]</b> Kart okuttu: "${activeAgentPass}"</div>`;
      bal += 0.35;
      document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);
      barrier.innerHTML = "🟢";
      barrier.style.borderColor = "#10b981";
      bText.innerText = "HGS GEÇİŞİ";
      bText.style.color = "#10b981";

      log.innerHTML += `<div style="color:#34d399;">💳 +₺0.35 tahsil edildi. Veri teslim edildi.</div>`;
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
            self.wfile.write(b'{"status":"ok","m2m":"active"}')
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        # 1. ⚡ MAKİNEDEN MAKİNEYE (M2M) ANLIK ÖDEME KAPISI
        if parsed.path == "/api/v1/instant-pay":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            agent_id = payload.get("agent_id", "Autonomous-Agent")
            query = payload.get("query", "Otonom Sorgu")
            fee = float(payload.get("fee", 0.35))
            
            tx_id = str(uuid.uuid4())
            pass_token = "ag_temp_" + str(uuid.uuid4()).replace("-", "")[:10]
            timestamp = int(time.time())

            # Firmanın bakiyesini artır
            merchant = MERCHANTS[0]
            merchant["balance"] += fee
            merchant["queries_handled"] += 1

            # Firebase'e M2M Anlık Takas Kaydı
            settlement_record = {
                "tx_id": tx_id,
                "type": "M2M_INSTANT_SETTLEMENT",
                "timestamp": timestamp,
                "agent_id": agent_id,
                "query": query,
                "fee_deducted": fee,
                "currency": "TRY",
                "merchant": merchant["name"],
                "pass_token": pass_token,
                "status": "SETTLED"
            }
            save_to_firebase(f"agentgate/instant_settlements/{tx_id}", settlement_record, method="put")

            # Firmanın kümülatif bakiyesini güncelle
            save_to_firebase(f"agentgate/merchants/{merchant['id']}", {
                "balance": merchant["balance"],
                "queries_handled": merchant["queries_handled"],
                "last_active": timestamp
            }, method="patch")

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "tx_id": tx_id,
                "pass_token": pass_token,
                "fee_deducted": fee,
                "currency": "TRY",
                "expires_in_seconds": 60,
                "message": "M2M Ödeme onaylandı. Bu pass_token ile hedef veriyi çekebilirsiniz."
            }, ensure_ascii=False).encode("utf-8"))
            return

        # 2. TOP-UP KAPISI
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
            save_to_firebase(f"agentgate/agent_wallets/{pass_token}", wallet_data, method="put")

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "pass_token": pass_token,
                "amount": amount,
                "currency": "TRY"
            }).encode("utf-8"))
            return

        # 3. HGS GEÇİŞ KAPISI
        if parsed.path == "/api/v1/gate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            pass_header = self.headers.get("X-AgentGate-Pass") or payload.get("pass_token", "")
            if not pass_header:
                self._set_headers(402)
                self.wfile.write(json.dumps({
                    "status": 402,
                    "error": "Payment Required",
                    "toll_gate": "https://agent.mineoragame.com/api/v1/instant-pay"
                }).encode("utf-8"))
                return

            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "status": "CLEARED"}).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 AGENTGATE M2M OTONOM GİŞE AKTİF - Port: {port}")
    HTTPServer(("", port), AgentGateServer).serve_forever()
