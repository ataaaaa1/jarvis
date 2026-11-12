"""JARVIS sunucusu: HTTP + WebSocket, telefon kontrollü."""
from __future__ import annotations
import asyncio, json, time
from pathlib import Path
from .brain import Brain
from .config import Config
from .memory import Memory
from .security import check_token, RateLimiter, AuditLog
from .voice import speak
from .router import Router

WEB_DIR = Path(__file__).parent / "web"
clients: set = set()
brain: Brain | None = None
router: Router | None = None
cfg: Config | None = None
limiter: RateLimiter | None = None
audit: AuditLog | None = None

async def broadcast(msg: dict):
    for ws in list(clients):
        try:
            await ws.send(json.dumps(msg, ensure_ascii=False))
        except Exception:
            clients.discard(ws)

async def handle_ws(ws, path=""):
    clients.add(ws)
    try:
        await ws.send(json.dumps({"type": "welcome", "text": "JARVIS çevrimiçi. Emirlerinizi bekliyorum."}))
        async for raw in ws:
            data = json.loads(raw)
            if data.get("type") == "command":
                text = data.get("text", "")
                if not limiter.allow("ws"):
                    reply = "Çok hızlısınız, dakikada daha fazla komut kabul edemem."
                else:
                    reply = router.handle(text) if router else "Beyin hazır değil."
                if audit:
                    audit.log("ws", "command", text)
                await ws.send(json.dumps({"type": "response", "text": reply, "echo": text}))
                await broadcast({"type": "response", "text": reply, "echo": text})
                if data.get("speak"):
                    speak(reply, cfg.lang)
            elif data.get("type") == "ping":
                await ws.send(json.dumps({"type": "pong"}))
    except Exception:
        pass
    finally:
        clients.discard(ws)

async def http_handler(path, headers):
    if path in ("/", "/index.html", ""):
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        return 200, {"Content-Type": "text/html; charset=utf-8"}, html.encode("utf-8")
    if path == "/health":
        body = json.dumps({"status": "ok", "time": time.time()}).encode()
        return 200, {"Content-Type": "application/json"}, body
    if path == "/api/command":
        token = headers.get("x-jarvis-token") or headers.get("Authorization", "").replace("Bearer ", "")
        if not check_token(token, cfg.token):
            return 401, {"Content-Type": "application/json"}, b'{"error":"unauthorized"}'
        if not limiter.allow("api"):
            return 429, {"Content-Type": "application/json"}, b'{"error":"rate_limited"}'
        body = json.loads(headers.get("x-body", "{}"))
        reply = router.handle(body.get("text", ""))
        return 200, {"Content-Type": "application/json"}, json.dumps({"reply": reply}, ensure_ascii=False).encode("utf-8")
    return 404, {"Content-Type": "text/plain"}, b"not found"

def _run_http(host, port, ready):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass
        def do_GET(self):
            code, hdrs, body = asyncio.run(http_handler(self.path.split("?")[0], {k.lower(): v for k, v in self.headers.items()}))
            self.send_response(code)
            for k, v in hdrs.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b"{}"
            hdrs = {k.lower(): v for k, v in self.headers.items()}
            hdrs["x-body"] = raw.decode("utf-8", "replace")
            code, h, body = asyncio.run(http_handler(self.path.split("?")[0], hdrs))
            self.send_response(code)
            for k, v in h.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)
    server = ThreadingHTTPServer((host, port), H)
    ready.set()
    server.serve_forever()

async def _handler(websocket):
    await handle_ws(websocket)

async def amain():
    global brain, cfg, router, limiter, audit
    cfg = Config.from_env()
    token = cfg.ensure_token()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    brain = Brain(cfg, Memory(cfg.data_dir / "memory.json"))
    router = Router(brain)
    limiter = RateLimiter(cfg.rate_limit_per_min)
    audit = AuditLog(cfg.log_dir / "audit.jsonl")
    import threading
    try:
        def _prep():
            try:
                import ctypes
                ctypes.windll.shell32.AddFirewallRule(
                    "JARVIS", 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                    cfg.port, b"")  # best-effort, hata yutulur
            except Exception:
                pass
        threading.Thread(target=_prep, daemon=True).start()
    except Exception:
        pass
    ready = threading.Event()
    threading.Thread(target=_run_http, args=(cfg.host, cfg.port, ready), daemon=True).start()
    ready.wait(5)
    print(f"JARVIS dinliyor: http://{cfg.host}:{cfg.port}")
    print(f"Token: {token}  (telefonda URL'ye ?token=... olarak ekleyin)")
    print(f"Shell komutları: {'AÇIK' if cfg.allow_shell else 'kapalı'}")
    try:
        from websockets import serve
        async with serve(_handler, cfg.host, cfg.port):
            while True:
                await asyncio.sleep(3600)
    except ImportError:
        print("WebSocket yok — HTTP modunda çalışıyor (pip install websockets önerilir)")
        while True:
            await asyncio.sleep(3600)

def main():
    asyncio.run(amain())

if __name__ == "__main__":
    main()
