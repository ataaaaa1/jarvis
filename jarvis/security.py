"""Güvenlik: token, rate-limit, denetim kaydı, onay, tehlikeli komut."""
from __future__ import annotations
import hmac, json, re, time
from collections import defaultdict, deque
from pathlib import Path

DANGEROUS_PATTERNS = [
    r"\brm\s+-rf?\s+/", r"\brm\s+-rf?\s+~", r"\bmkfs\b",
    r"\bdd\s+.*of=/dev/", r":\s*\(\)\s*\{", r"\bshutdown\b",
    r"\breboot\b", r"\bhalt\b", r"\bpoweroff\b",
    r"\bcp\s+.*\s+/etc/", r"\bmv\s+.*\s+/etc/",
    r"curl.*\|\s*(sudo\s+)?(sh|bash)", r"wget.*\|\s*(sudo\s+)?(sh|bash)",
    r">\s*/etc/passwd", r">\s*/etc/shadow", r"\bchmod\s+777\s+/",
    r"\bchown\s+.*\s+/etc/", r"\bkill\s+-9\s+1\b",
    r"\btruncate\s+-s\s*0\b",
]

def is_dangerous(cmd: str) -> bool:
    return any(re.search(p, cmd, re.I) for p in DANGEROUS_PATTERNS)

def check_token(provided: str | None, expected: str) -> bool:
    if not provided or not expected:
        return False
    return hmac.compare_digest(provided.strip(), expected.strip())

def sanitize_path(user_path: str, allowed: list) -> str | None:
    p = Path(user_path).expanduser().resolve()
    for base in allowed:
        try:
            p.relative_to(Path(base).expanduser().resolve())
            return str(p)
        except ValueError:
            continue
    return None

class RateLimiter:
    def __init__(self, per_min: int = 120):
        self.per_min = per_min
        self.hits: dict[str, deque] = defaultdict(deque)
    def allow(self, key: str = "default") -> bool:
        now = time.time()
        q = self.hits[key]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= self.per_min:
            return False
        q.append(now)
        return True

class AuditLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
    def log(self, actor: str, action: str, detail: str = ""):
        rec = {"ts": time.time(), "actor": actor, "action": action, "detail": detail[:500]}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

class ConfirmManager:
    """Tehlikeli eylemler için tek seferlik onay kodu."""
    def __init__(self, ttl: int = 120):
        self.ttl = ttl
        self.pending: dict[str, tuple[str, float]] = {}
    def request(self, action: str) -> str:
        import secrets
        code = secrets.token_hex(3)
        self.pending[code] = (action, time.time() + self.ttl)
        return code
    def consume(self, code: str) -> str | None:
        item = self.pending.pop(code, None)
        if not item:
            return None
        action, exp = item
        return action if time.time() <= exp else None
