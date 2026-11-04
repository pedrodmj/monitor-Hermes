import json, os, re, sys
import requests

URL = ("https://www.hermes.com/br/pt/category/artigos-de-couro/"
       "bolsas-e-bolsas-clutch/bolsas-e-bolsas-clutch-femininas/"
       "?facet_line=picotin_lock")
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
STATE = "state.json"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": msg}, timeout=30)

state = None
if os.path.exists(STATE):
    with open(STATE) as f:
        state = json.load(f)

def save(products, blocked):
    with open(STATE, "w") as f:
        json.dump({"products": products, "blocked": blocked}, f)

try:
    r = requests.get(URL, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"})
    r.raise_for_status()
    items = sorted(set(re.findall(
        r"/br/pt/product/([a-z0-9-]+-H[0-9A-Z]+)/", r.text)))
except Exception as e:
    if not state or not state.get("blocked"):
        send(f"⚠️ Não consegui ler a página da Hermès: {e}")
    save(state["products"] if state else None, True)
    sys.exit(0)

known = state["products"] if state else None
if known is None:
    send(f"✅ Monitoramento iniciado. {len(items)} produto(s) agora.")
else:
    for slug in sorted(set(items) - set(known)):
        send("🆕 Novo produto na Hermès!\n"
             f"https://www.hermes.com/br/pt/product/{slug}/")
    if state.get("blocked"):
        send("✅ Voltei a conseguir ler a página.")
save(items, False)
