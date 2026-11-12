#!/usr/bin/env python3
"""Telegram üzerinden JARVIS kontrolü (opsiyonel, stdlib polling)."""
import json, os, sys, urllib.request, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

API = "https://api.telegram.org/bot{token}/{method}"

def call(token, method, **params):
    url = API.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
        return json.loads(r.read())

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token:
        print("TELEGRAM_BOT_TOKEN gerekli (.env'e ekleyin)")
        return 1
    from jarvis.config import Config
    from jarvis.memory import Memory
    from jarvis.brain import Brain
    from jarvis.router import Router
    cfg = Config.from_env()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    router = Router(Brain(cfg, Memory(cfg.data_dir / "memory.json")))
    offset = 0
    print("Telegram botu çalışıyor…")
    while True:
        try:
            updates = call(token, "getUpdates", offset=offset, timeout=25).get("result", [])
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            continue
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message") or {}
            text = (msg.get("text") or "").strip()
            cid = str(msg.get("chat", {}).get("id", ""))
            if not text:
                continue
            if chat_id and cid != chat_id:
                call(token, "sendMessage", chat_id=cid, text="Yetkisiz erişim.")
                continue
            reply = router.handle(text)
            call(token, "sendMessage", chat_id=cid, text=reply[:4000])

if __name__ == "__main__":
    raise SystemExit(main() or 0)
