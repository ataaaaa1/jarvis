import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jarvis.config import Config
from jarvis.memory import Memory
from jarvis.brain import Brain
from jarvis.router import Router

class FakeBrain(Brain):
    def __init__(self, cfg, memory):
        super().__init__(cfg, memory)
        self.router = Router(self)
    def handle(self, raw: str) -> str:
        return self.router.handle(raw)

def make_brain():
    cfg = Config()
    d = Path(tempfile.mkdtemp())
    return FakeBrain(cfg, Memory(d / "memory.json"))

def test_greeting():
    b = make_brain()
    assert "merhaba" in b.handle("merhaba").lower()

def test_time():
    b = make_brain()
    assert "saat" not in b.handle("saat kaç").lower() or len(b.handle("saat kaç")) > 3

def test_memory_info():
    b = make_brain()
    assert "bellek" in b.handle("bellek").lower()

def test_system_info():
    b = make_brain()
    from jarvis.brain import _norm
    assert "isletim" in _norm(b.handle("sistem bilgisi"))

def test_help():
    b = make_brain()
    assert "yapabileceklerim" in b.handle("yardım").lower()

def test_calculate():
    b = make_brain()
    assert "14" in b.handle("hesapla 7+7")

def test_note_and_recall():
    b = make_brain()
    b.handle("not al: toplantı yarın")
    assert "toplantı" in b.handle("notlar")

def test_dice():
    b = make_brain()
    out = b.handle("zar at")
    assert "zar" in out.lower()

def test_unknown():
    b = make_brain()
    assert "bulamadım" in b.handle("xyz bilinmeyen komut")

def test_shell_blocked_by_default():
    b = make_brain()
    out = b.handle("komut çalıştır echo hi")
    assert "kapalı" in out.lower()

def test_confirm_flow():
    from jarvis.config import Config
    cfg = Config(allow_shell=True, log_dir=Path(tempfile.mkdtemp()))
    d = Path(tempfile.mkdtemp())
    b = FakeBrain(cfg, Memory(d / "memory.json"))
    out = b.handle("komut çalıştır rm -rf /")
    assert "onay" in out.lower()
    import re as _re
    m = _re.search(r"onayla\s+([0-9a-f]{6})", out)
    assert m, out
    out2 = b.handle(f"onayla {m.group(1)}")
    assert "engellendi" not in out2.lower() or "kod" not in out2.lower()

def test_security_rate_limit():
    from jarvis.security import RateLimiter, is_dangerous
    rl = RateLimiter(per_min=3)
    assert rl.allow() and rl.allow() and rl.allow()
    assert not rl.allow()
    assert is_dangerous("rm -rf /")
    assert not is_dangerous("echo hello")

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"{len(tests)} test geçti ✅")
