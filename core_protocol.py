import os
import json
import time
import uuid
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

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

def get_from_firebase(path):
    if not FIREBASE_SECRET:
        return None
    url = f"{FIREBASE_DB_URL}/{path}.json?auth={FIREBASE_SECRET}"
    try:
        r = requests.get(url, timeout=3)
        return r.json()
    except Exception:
        return None

# ==========================================================
# FİRMALAR & İŞLEM GEÇMİŞİ
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

RECENT_TRANSACTIONS = [
    {"time": "04:31:12", "agent": "GPTBot / OpenAI", "query": "İstanbul - Londra 15 Ekim", "fee": 0.35, "status": "ÖDENDİ"},
    {"time": "04:28:45", "agent": "Google-Extended / Gemini", "query": "Bodrum 2 kişilik butik otel", "fee": 0.50, "status": "ÖDENDİ"},
    {"time": "04:22:04", "agent": "ClaudeBot / Anthropic", "query": "RTX 4070 ekran kartı stok", "fee": 0.15, "status": "ÖDENDİ"},
    {"time": "04:19:30", "agent": "PerplexityBot", "query": "Antalya her şey dahil resort", "fee": 0.50, "status": "ÖDENDİ"}
]

AGENT_PASSES = {
    "ag_pass_demo123": {
        "agent_name": "OpenAI GPTBot Kurumsal Havuzu",
        "balance": 500.00,
        "currency": "TRY"
    }
}

OPENAPI_SPEC = {
    "openapi": "3.0.1",
    "info": {
        "title": "AgentGate AI Micropayment Toll Gate (HGS)",
        "description": "Yapay zeka modellerinin web sitelerinden canlı veri çekerken HTTP 402 geçiş biletiyle ödeme yaptığı takas protokolü.",
        "version": "v1.5.0"
    },
    "servers": [{"url": "https://agent.mineoragame.com"}],
    "paths": {
        "/api/v1/gate": {
            "post": {
                "summary": "HGS Otoban Gişesi Geçişi",
                "responses": {"200": {"description": "Geçiş onaylandı."}, "402": {"description": "Ödeme Gerekli."}}
            }
        },
        "/api/v1/instant-pay": {
            "post": {
                "summary": "M2M Anlık Mikro Ödeme",
                "responses": {"200": {"description": "Ödeme tamamlandı."}}
            }
        }
    }
}

# ==========================================================
# ORTAK CSS & ŞABLONLAR
# ==========================================================
COMMON_CSS = """
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
header { position: relative; z-index: 10; max-width: 1200px; margin: 0 auto; padding: 22px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.04); }
.logo { display: flex; align-items: center; gap: 10px; font-size: 22px; font-weight: 800; text-decoration: none; color: #fff; }
.logo-badge { background: linear-gradient(135deg, var(--emerald), var(--cyan)); color: #000; font-weight: 900; font-size: 13px; padding: 4px 10px; border-radius: 8px; }
.nav-links { display: flex; align-items: center; gap: 20px; }
.nav-links a { color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; transition: color 0.2s; }
.nav-links a:hover, .nav-links a.active { color: #fff; }
.btn-nav-portal { background: rgba(255,255,255,0.06); border: 1px solid var(--card-border); color: #fff; font-weight: 600; padding: 8px 16px; border-radius: 10px; font-size: 13px; cursor: pointer; text-decoration: none; transition: 0.2s; }
.btn-nav-portal:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.2); }
"""

# ==========================================================
# 1. SAYFA: TOPARLANMIŞ VİTRİN & SİMÜLATÖR (HTML_LANDING)
# ==========================================================
HTML_LANDING = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgentGate | Otonom Yapay Zeka Mikro Gişe Protokolü</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    {COMMON_CSS}
    .hero {{ position: relative; z-index: 1; max-width: 950px; margin: 55px auto 35px; text-align: center; padding: 0 20px; }}
    .tag {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: var(--emerald); padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 22px; }}
    h1 {{ font-size: clamp(34px, 5.2vw, 56px); font-weight: 800; letter-spacing: -1.5px; line-height: 1.15; margin-bottom: 18px; }}
    .gradient-accent {{ background: linear-gradient(135deg, var(--emerald) 0%, var(--cyan) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero p {{ font-size: 17px; color: var(--text-muted); max-width: 740px; margin: 0 auto; }}

    .sim-wrapper {{ position: relative; z-index: 1; max-width: 1100px; margin: 0 auto 70px; padding: 0 20px; }}
    .sim-card {{ background: var(--card-bg); backdrop-filter: blur(20px); border: 1px solid var(--card-border); border-radius: 24px; padding: 32px; box-shadow: 0 30px 60px rgba(0,0,0,0.5); }}
    .sim-grid {{ display: grid; grid-template-columns: 1.1fr 130px 1fr; gap: 20px; align-items: center; }}
    @media(max-width: 850px) {{ .sim-grid {{ grid-template-columns: 1fr; }} }}
    .box {{ background: rgba(8, 12, 20, 0.8); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; }}
    select, input {{ width: 100%; background: rgba(255,255,255,0.04); border: 1px solid var(--card-border); color: #fff; padding: 10px 14px; border-radius: 10px; margin-top: 6px; font-family: inherit; }}
    .btn-fire-auto {{ width: 100%; background: linear-gradient(135deg, var(--purple), #7c3aed); color: #fff; font-weight: 800; border: none; padding: 12px; border-radius: 10px; cursor: pointer; margin-top: 12px; font-size: 13px; box-shadow: 0 0 25px rgba(168,85,247,0.3); transition: 0.2s; }}
    .bridge-node {{ width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(16,185,129,0.2)); border: 2px dashed var(--amber); display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto; transition: 0.3s; }}
    .terminal-feed {{ margin-top: 24px; background: #04060a; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a5f3fc; max-height: 200px; overflow-y: auto; }}

    .snippet-section {{ max-width: 1100px; margin: 0 auto 80px; padding: 0 20px; position: relative; z-index: 1; }}
    .snippet-card {{ background: rgba(12, 17, 29, 0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 28px; }}
    pre {{ background: #020408; padding: 16px; border-radius: 12px; overflow-x: auto; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 13px; margin-top: 12px; border: 1px solid rgba(255,255,255,0.05); }}

    footer {{ border-top: 1px solid var(--card-border); padding: 40px 20px; text-align: center; font-size: 13px; color: var(--text-muted); }}
  </style>
</head>
<body>
  <div class="grid-bg"></div>

  <header>
    <a href="/" class="logo">
      <div class="logo-badge">AGENTGATE</div>
      <span>Protocol</span>
    </a>
    <div class="nav-links">
      <a href="#simulator" class="active">Simülatör</a>
      <a href="#snippet">HGS Kodu</a>
      <a href="/openapi.json" target="_blank" style="color:var(--cyan);">OpenAPI</a>
      <a href="/dashboard" class="btn-nav-portal">🏢 Firma Paneli (Giriş)</a>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="tag">🛡️ HTTP 402 Standartlı Yapay Zeka Gişesi</div>
      <h1>Web Sitenizi Kapatmayın,<br><span class="gradient-accent">Kapısına Yapay Zeka HGS'si Koyun</span></h1>
      <p>
        İnsanlar sitenizi ücretsiz gezmeye devam etsin; Gemini, ChatGPT ve arama botları verinizi her çektiğinde HGS gişesinden kuruş bazında otomatik ödeme yapsın.
      </p>
    </section>

    <!-- SİMÜLATÖR -->
    <section class="sim-wrapper" id="simulator">
      <div class="sim-card">
        <div class="sim-grid">
          <div class="box">
            <b>🤖 Yapay Zeka Botu (Sorgulayan)</b>
            <select id="botSelect" style="margin-top:6px;">
              <option value="GPTBot (OpenAI Ajanı)">GPTBot / ChatGPT Search</option>
              <option value="Google-Extended (Gemini)">Google-Extended / Gemini Bot</option>
              <option value="ClaudeBot (Anthropic)">ClaudeBot</option>
            </select>
            <input type="text" id="targetPath" value="/fiyatlar/ayvalik-otelleri.json" style="margin-top:6px;">
            <button class="btn-fire-auto" onclick="runAutonomousM2M()">⚡ Otonom Bot Modu (Durdur, Öde ve Geç)</button>
          </div>

          <div style="text-align:center;">
            <div class="bridge-node" id="gateBarrier">🚧</div>
            <div style="font-size:11px; color:var(--amber); font-weight:700; margin-top:8px;" id="barrierText">HGS GİŞESİ</div>
          </div>

          <div class="box">
            <b>🏢 Veri Sağlayıcı Firma (Kasa)</b>
            <div style="font-size:13px; color:var(--text-muted); margin-top:8px;">Firma: <b>SkyWings & Otel Havuzu</b></div>
            <div style="font-size:13px; color:var(--emerald);">Bot Tarifesi: <b>0.35 TL / sorgu</b></div>
            <div style="font-size:26px; font-weight:800; color:#34d399; margin-top:10px;" id="merchBal">₺1,845.50</div>
            <div style="font-size:11px; color:#64748b;">🔥 Firebase Realtime Kasa</div>
          </div>
        </div>

        <div class="terminal-feed" id="termLog">
          <div>[04:40:00] HGS Gişe Kontrolörü & M2M Otonom Ödeme motoru hazır.</div>
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

if (AI_BOTS.some(bot => userAgent.includes(bot))) {{
  const hgsPass = request.headers.get('X-AgentGate-Pass');
  if (!hgsPass) {{
    // 402 FATURASI KES VE BOTUN OTONOM ÖDEME YAPMASINI SAĞLA
    return new Response(JSON.stringify({{
      error: "HTTP 402 Payment Required",
      message: "Bu sitenin verisi ücretlidir.",
      fee: "0.35 TRY",
      instant_pay_endpoint: "https://agent.mineoragame.com/api/v1/instant-pay",
      required_header: "X-AgentGate-Pass"
    }}), {{ status: 402, headers: {{ 'Content-Type': 'application/json' }} }});
  }}
}}
return fetch(request); // Normal insanlara ücretsiz</code></pre>
      </div>
    </section>
  </main>

  <footer>
    <p>© 2026 AgentGate Protocol. Resmi Gişe: agent.mineoragame.com | <a href="/dashboard" style="color:var(--emerald);">Firma Paneli</a></p>
  </footer>

  <script>
    let bal = 1845.50;

    async function runAutonomousM2M() {{
      const bot = document.getElementById('botSelect').value;
      const path = document.getElementById('targetPath').value;
      const log = document.getElementById('termLog');
      const barrier = document.getElementById('gateBarrier');
      const bText = document.getElementById('barrierText');

      function addLog(msg) {{
        log.innerHTML += `<div>${{msg}}</div>`;
        log.scrollTop = log.scrollHeight;
      }}

      addLog(`🤖 <b>[${{bot}}]</b> siteye daldı: "${{path}}"`);
      barrier.innerHTML = "🛑";
      barrier.style.borderColor = "#f43f5e";
      bText.innerText = "HTTP 402";
      bText.style.color = "#f43f5e";

      await new Promise(r => setTimeout(r, 450));
      addLog(`<span style="color:#f43f5e;">⛔ <b>[HTTP 402]:</b> Site geçişi durdurdu. Fatura: 0.35 TRY kesildi.</span>`);

      await new Promise(r => setTimeout(r, 500));
      addLog(`<span style="color:#c084fc;">⚡ <b>[M2M Otonom]:</b> Bot anlık ödeme yapıyor... /api/v1/instant-pay</span>`);

      const res = await fetch('/api/v1/instant-pay', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{ agent_id: bot, query: path, fee: 0.35 }})
      }});
      const data = await res.json();

      await new Promise(r => setTimeout(r, 400));
      bal += data.fee_deducted;
      document.getElementById('merchBal').innerText = '₺' + bal.toFixed(2);

      barrier.innerHTML = "🟢";
      barrier.style.borderColor = "#10b981";
      bText.innerText = "GEÇİŞ ONAYLANDI";
      bText.style.color = "#10b981";

      addLog(`<span style="color:#34d399;">✅ <b>Bariyer Açıldı:</b> Otelin kasasına +₺${{data.fee_deducted.toFixed(2)}} eklendi. (Firebase Senkronize)</span>`);
      addLog(`<span style="color:#a5f3fc;">📦 Güncel veri bota teslim edildi. İşlem 1.1 sn.</span>`);
    }}
  </script>
</body>
</html>"""

# ==========================================================
# 2. SAYFA: FİRMA KASA & RAPOR PANELİ (HTML_DASHBOARD)
# ==========================================================
HTML_DASHBOARD = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgentGate | Firma Yönetim & Kasa Paneli</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    {COMMON_CSS}
    .dash-container {{ max-width: 1100px; margin: 40px auto 80px; padding: 0 20px; position: relative; z-index: 1; }}
    .stats-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }}
    .stat-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 18px; padding: 24px; }}
    .stat-label {{ font-size: 13px; color: var(--text-muted); font-weight: 600; margin-bottom: 6px; }}
    .stat-value {{ font-size: 32px; font-weight: 800; color: #fff; }}
    .stat-sub {{ font-size: 12px; color: var(--emerald); margin-top: 6px; }}

    .card-main {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 20px; padding: 28px; margin-bottom: 30px; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
    .card-title {{ font-size: 18px; font-weight: 700; color: #fff; }}

    table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }}
    th {{ color: var(--text-muted); padding: 12px 14px; border-bottom: 1px solid var(--card-border); font-weight: 600; }}
    td {{ padding: 14px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #e2e8f0; }}
    tr:hover td {{ background: rgba(255,255,255,0.02); }}

    .badge-paid {{ background: rgba(16,185,129,0.15); color: #34d399; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; }}
    .btn-withdraw {{ background: linear-gradient(135deg, var(--emerald), #059669); color: #000; border: none; font-weight: 700; padding: 10px 20px; border-radius: 10px; cursor: pointer; transition: 0.2s; }}
    .btn-withdraw:hover {{ box-shadow: 0 0 20px var(--emerald-glow); transform: translateY(-1px); }}

    .merchant-selector {{ background: rgba(255,255,255,0.04); border: 1px solid var(--card-border); color: #fff; padding: 8px 14px; border-radius: 10px; font-size: 13px; outline: none; }}
  </style>
</head>
<body>
  <div class="grid-bg"></div>

  <header>
    <a href="/" class="logo">
      <div class="logo-badge">AGENTGATE</div>
      <span>Firma Paneli</span>
    </a>
    <div class="nav-links">
      <a href="/">← Ana Sayfa</a>
      <select class="merchant-selector" id="dashSelect" onchange="switchMerchant()">
        <option value="0">SkyWings Uçuş & Bilet API</option>
        <option value="1">Ege & Akdeniz Rezervasyon Havuzu</option>
        <option value="2">TeknoMarket Stok & Fiyat</option>
      </select>
    </div>
  </header>

  <main class="dash-container">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
      <div>
        <h1 style="font-size:26px; font-weight:800;" id="mName">SkyWings Uçuş & Bilet API</h1>
        <p style="font-size:13px; color:var(--text-muted);" id="mDomain">skywings.com.tr • Canlı HGS Gişesi Aktif</p>
      </div>
      <button class="btn-withdraw" onclick="requestPayout()">💳 Bakiyeyi Banka Hesabıma Çek</button>
    </div>

    <!-- İSTATİSTİK KARTLARI -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Toplam Gişe Geliri (Kasa)</div>
        <div class="stat-value" style="color:#34d399;" id="mBal">₺1,845.50</div>
        <div class="stat-sub">🔥 Firebase Anlık Defter</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Yanıtlanan Yapay Zeka Sorgusu</div>
        <div class="stat-value" id="mQueries">5,273</div>
        <div class="stat-sub">Gemini, ChatGPT, Claude</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Sorgu Başına Tarife</div>
        <div class="stat-value" id="mRate">₺0.35</div>
        <div class="stat-sub">HGS Kuruş Takası</div>
      </div>
    </div>

    <!-- SON İŞLEMLER TABLOSU -->
    <div class="card-main">
      <div class="card-header">
        <div class="card-title">⚡ Son Yapay Zeka Sorguları & Hakedişler</div>
        <div style="font-size:12px; color:var(--emerald);">CANLI AKIŞ AKTİF</div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Saat</th>
            <th>Sorgulayan Yapay Zeka</th>
            <th>Çekilen Veri / Arama</th>
            <th>Kazanılan Tutar</th>
            <th>Durum</th>
          </tr>
        </thead>
        <tbody id="txTable">
          <!-- Dinamik doldurulacak -->
        </tbody>
      </table>
    </div>

    <!-- ENTEGRASYON BİLGİSİ -->
    <div class="card-main" style="background:rgba(8,12,20,0.6);">
      <div style="font-size:15px; font-weight:700; margin-bottom:8px;">🔑 Firmanıza Özel HGS API Anahtarı</div>
      <div style="background:#020408; padding:12px; border-radius:10px; font-family:'JetBrains Mono',monospace; font-size:13px; color:#38bdf8; display:flex; justify-content:space-between; align-items:center;">
        <span id="mApiKey">ag_live_skywings_pass_88291a</span>
        <button style="background:none; border:none; color:var(--text-muted); cursor:pointer;" onclick="alert('Kopyalandı!')">Kopyala</button>
      </div>
    </div>
  </main>

  <script>
    const merchants = [
      {{ name: "SkyWings Uçuş & Bilet API", domain: "skywings.com.tr", bal: 1845.50, queries: 5273, rate: 0.35, key: "ag_live_skywings_pass" }},
      {{ name: "Ege & Akdeniz Rezervasyon", domain: "egerezervasyon.com", bal: 3120.00, queries: 6240, rate: 0.50, key: "ag_live_egeresort_pass" }},
      {{ name: "TeknoMarket Stok & Fiyat", domain: "teknomarket.internal", bal: 980.25, queries: 6535, rate: 0.15, key: "ag_live_teknoradar_pass" }}
    ];

    const sampleTxs = [
      {{ time: "04:42:10", agent: "Google Gemini 1.5", query: "İstanbul - Londra 15 Ekim", fee: 0.35 }},
      {{ time: "04:39:25", agent: "OpenAI GPTBot", query: "Antalya 2 kişilik oda", fee: 0.50 }},
      {{ time: "04:35:12", agent: "Claude 3.5 Sonnet", query: "Ankara otobüs seferleri", fee: 0.35 }},
      {{ time: "04:30:04", agent: "Perplexity Search", query: "Canlı bilet fiyatları", fee: 0.35 }}
    ];

    function switchMerchant() {{
      const idx = document.getElementById('dashSelect').value;
      const m = merchants[idx];
      document.getElementById('mName').innerText = m.name;
      document.getElementById('mDomain').innerText = m.domain + ' • Canlı HGS Gişesi Aktif';
      document.getElementById('mBal').innerText = '₺' + m.bal.toFixed(2);
      document.getElementById('mQueries').innerText = m.queries.toLocaleString();
      document.getElementById('mRate').innerText = '₺' + m.rate.toFixed(2);
      document.getElementById('mApiKey').innerText = m.key;
      renderTable(m.rate);
    }}

    function renderTable(rate) {{
      const tbody = document.getElementById('txTable');
      tbody.innerHTML = '';
      sampleTxs.forEach(tx => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="color:#64748b; font-family:'JetBrains Mono';">${{tx.time}}</td>
          <td><b>${{tx.agent}}</b></td>
          <td style="color:#94a3b8;">${{tx.query}}</td>
          <td style="color:#34d399; font-weight:700;">+₺${{rate.toFixed(2)}}</td>
          <td><span class="badge-paid">ÖDENDİ</span></td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function requestPayout() {{
      const iban = prompt("Bakiyenizin aktarılacağı şirket IBAN numarasını girin:", "TR00 0000 0000 0000 0000 0000 00");
      if (iban) {{
        alert("Para Çekme Talebiniz Alındı!\\n\\nKasadaki bakiye muhasebe mutabakatının ardından 24 saat içinde hesabınıza aktarılacaktır.");
      }}
    }}

    window.onload = switchMerchant;
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-AgentGate-Pass")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)

        # 1. Ana Sayfa (Toparlanmış Vitrin & Simülatör)
        if parsed.path in ["/", "/index.html"]:
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_LANDING.encode("utf-8"))
            return

        # 2. Firma Kasa & Rapor Paneli (YENİ)
        if parsed.path in ["/dashboard", "/merchant"]:
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
            return

        # 3. OpenAPI Şeması
        if parsed.path == "/openapi.json":
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(OPENAPI_SPEC, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 4. Sağlık Kontrolü
        if parsed.path == "/health":
            self._set_headers(200)
            self.wfile.write(b'{"status":"ok","dashboard":"active"}')
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)

        # 1. M2M Anlık Ödeme Kapısı
        if parsed.path == "/api/v1/instant-pay":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            agent_id = payload.get("agent_id", "Autonomous-Agent")
            query = payload.get("query", "Otonom İstek")
            fee = float(payload.get("fee", 0.35))
            tx_id = str(uuid.uuid4())
            pass_token = "ag_temp_" + str(uuid.uuid4()).replace("-", "")[:10]
            timestamp = int(time.time())

            # Firmanın bakiyesini artır
            merchant = MERCHANTS[0]
            merchant["balance"] += fee
            merchant["queries_handled"] += 1

            # Firebase'e yaz
            save_to_firebase(f"agentgate/instant_settlements/{tx_id}", {
                "tx_id": tx_id,
                "timestamp": timestamp,
                "agent_id": agent_id,
                "query": query,
                "fee_deducted": fee,
                "merchant": merchant["name"],
                "pass_token": pass_token,
                "status": "SETTLED"
            }, method="put")

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "tx_id": tx_id,
                "pass_token": pass_token,
                "fee_deducted": fee,
                "currency": "TRY"
            }, ensure_ascii=False).encode("utf-8"))
            return

        # 2. HGS Kapısı
        if parsed.path == "/api/v1/gate":
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "status": "CLEARED"}).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 AGENTGATE DASHBOARD & HGS AKTİF - Port: {port}")
    HTTPServer(("", port), AgentGateServer).serve_forever()
