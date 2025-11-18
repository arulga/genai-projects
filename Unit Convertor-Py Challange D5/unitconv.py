"""
Flask Unit Converter (single-file)
Features:
- Currency: INR <-> USD (live rate fetched server-side)
- Temperature: C <-> F
- Length: cm <-> inch
- Weight: kg <-> lb
- Real-time results on the page using JavaScript (no page reload)

How to run
1. Create a virtualenv (recommended) and install requirements:
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows
   pip install flask requests

2. Run:
   python flask_unit_converter.py

3. Open http://127.0.0.1:5000 in your browser

Notes
- The app calls a public exchange-rate API server-side. If the API fails, a fallback rate is used.
- The HTML is embedded with render_template_string to keep this a single file app.
"""
from flask import Flask, jsonify, render_template_string, request
import requests
import time

app = Flask(__name__)

# Cache the exchange rate for a short time to avoid hitting API repeatedly
CACHED = {
    "rate": None,
    "ts": 0
}
CACHE_TTL = 300  # seconds
FALLBACK_USD_TO_INR = 84.0

EXCHANGE_API_URL = "https://api.exchangerate.host/latest?base=USD&symbols=INR"


def fetch_usd_to_inr():
    """Fetch USD -> INR rate with simple caching and fallback."""
    now = time.time()
    if CACHED["rate"] is not None and now - CACHED["ts"] < CACHE_TTL:
        return CACHED["rate"]

    try:
        resp = requests.get(EXCHANGE_API_URL, timeout=5)
        data = resp.json()
        rate = float(data.get("rates", {}).get("INR", FALLBACK_USD_TO_INR))
    except Exception:
        rate = FALLBACK_USD_TO_INR

    CACHED["rate"] = rate
    CACHED["ts"] = now
    return rate


@app.route("/rate")
def rate_endpoint():
    """Return latest USD->INR rate as JSON."""
    rate = fetch_usd_to_inr()
    return jsonify({"usd_to_inr": rate})


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Unit Converter</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px; }
    .card { border: 1px solid #e6e6e6; padding: 18px; border-radius: 8px; margin-bottom: 12px; max-width:520px }
    label { display:block; margin-bottom:6px; font-weight:600 }
    input[type="number"] { width:100%; padding:8px; font-size:16px; margin-bottom:8px }
    .row { display:flex; gap:8px; align-items:center }
    button { padding:8px 12px; font-size:14px }
    .result { font-weight:700; margin-top:6px }
    small.muted { color:#666 }
  </style>
</head>
<body>
  <h1>Unit Converter 🔄</h1>
  <div class="card" id="currency">
    <label>Currency (INR ↔ USD)</label>
    <div class="row">
      <select id="cur-mode">
        <option value="inr2usd">INR → USD</option>
        <option value="usd2inr">USD → INR</option>
      </select>
      <input id="cur-amount" type="number" step="any" placeholder="Enter amount">
      <button onclick="convertCurrency()">Convert</button>
    </div>
    <div class="result" id="cur-result">—</div>
    <small class="muted" id="rate-info">Fetching rate…</small>
  </div>

  <div class="card">
    <label>Temperature (°C ↔ °F)</label>
    <div class="row">
      <select id="temp-mode">
        <option value="c2f">°C → °F</option>
        <option value="f2c">°F → °C</option>
      </select>
      <input id="temp-amount" type="number" step="any" placeholder="Enter temperature">
      <button onclick="convertTemp()">Convert</button>
    </div>
    <div class="result" id="temp-result">—</div>
  </div>

  <div class="card">
    <label>Length (cm ↔ inch)</label>
    <div class="row">
      <select id="len-mode">
        <option value="cm2in">cm → inch</option>
        <option value="in2cm">inch → cm</option>
      </select>
      <input id="len-amount" type="number" step="any" placeholder="Enter value">
      <button onclick="convertLen()">Convert</button>
    </div>
    <div class="result" id="len-result">—</div>
  </div>

  <div class="card">
    <label>Weight (kg ↔ lb)</label>
    <div class="row">
      <select id="wt-mode">
        <option value="kg2lb">kg → lb</option>
        <option value="lb2kg">lb → kg</option>
      </select>
      <input id="wt-amount" type="number" step="any" placeholder="Enter value">
      <button onclick="convertWt()">Convert</button>
    </div>
    <div class="result" id="wt-result">—</div>
  </div>

<script>
let usdToInr = null;
async function fetchRate(){
  try{
    const r = await fetch('/rate');
    const j = await r.json();
    usdToInr = Number(j.usd_to_inr);
    document.getElementById('rate-info').textContent = `1 USD = ${usdToInr} INR`;
  }catch(e){
    usdToInr = null;
    document.getElementById('rate-info').textContent = 'Rate unavailable (using fallback in server)';
  }
}

function toFixedSmart(n){
  if(Math.abs(n) < 0.01) return n.toExponential(4);
  return Number(n.toFixed(4));
}

function convertCurrency(){
  const mode = document.getElementById('cur-mode').value;
  const val = Number(document.getElementById('cur-amount').value);
  if(!isFinite(val)) { document.getElementById('cur-result').textContent = 'Enter a valid number'; return; }
  if(usdToInr === null){
    // still allow local conversion by requesting server-side rate synchronously
    fetchRate().then(()=> doCurConvert(val, mode));
  }else{
    doCurConvert(val, mode);
  }
}

function doCurConvert(val, mode){
  if(usdToInr === null){
    document.getElementById('cur-result').textContent = 'Rate unavailable. Try again later.'; return;
  }
  if(mode === 'inr2usd'){
    const out = val / usdToInr;
    document.getElementById('cur-result').textContent = `${val} INR = ${toFixedSmart(out)} USD`;
  } else {
    const out = val * usdToInr;
    document.getElementById('cur-result').textContent = `${val} USD = ${toFixedSmart(out)} INR`;
  }
}

function convertTemp(){
  const mode = document.getElementById('temp-mode').value;
  const val = Number(document.getElementById('temp-amount').value);
  if(!isFinite(val)) { document.getElementById('temp-result').textContent = 'Enter a valid number'; return; }
  if(mode === 'c2f'){
    const out = (val * 9/5) + 32;
    document.getElementById('temp-result').textContent = `${val} °C = ${toFixedSmart(out)} °F`;
  } else {
    const out = (val - 32) * 5/9;
    document.getElementById('temp-result').textContent = `${val} °F = ${toFixedSmart(out)} °C`;
  }
}

function convertLen(){
  const mode = document.getElementById('len-mode').value;
  const val = Number(document.getElementById('len-amount').value);
  if(!isFinite(val)) { document.getElementById('len-result').textContent = 'Enter a valid number'; return; }
  if(mode === 'cm2in'){
    const out = val / 2.54;
    document.getElementById('len-result').textContent = `${val} cm = ${toFixedSmart(out)} inch`;
  } else {
    const out = val * 2.54;
    document.getElementById('len-result').textContent = `${val} inch = ${toFixedSmart(out)} cm`;
  }
}

function convertWt(){
  const mode = document.getElementById('wt-mode').value;
  const val = Number(document.getElementById('wt-amount').value);
  if(!isFinite(val)) { document.getElementById('wt-result').textContent = 'Enter a valid number'; return; }
  if(mode === 'kg2lb'){
    const out = val * 2.2046226218;
    document.getElementById('wt-result').textContent = `${val} kg = ${toFixedSmart(out)} lb`;
  } else {
    const out = val / 2.2046226218;
    document.getElementById('wt-result').textContent = `${val} lb = ${toFixedSmart(out)} kg`;
  }
}

// fetch rate on load
fetchRate();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


if __name__ == '__main__':
    app.run(debug=True)
