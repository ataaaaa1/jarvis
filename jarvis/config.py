"""Yapılandırma: ortam değişkenleri + .env"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def _env_bool(name: str, default: bool = False) -> bool:
    return _env(name, str(default)).lower() in ("1", "true", "yes", "on")

def load_dotenv(path: Path | None = None) -> None:
    p = path or (ROOT / ".env")
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 8765
    token: str = ""
    allow_shell: bool = False
    allow_dangerous: bool = False
    lang: str = "tr-TR"
    wake_word: str = "jarvis"
    data_dir: Path = DATA_DIR
    allowed_dirs: list[Path] = field(default_factory=lambda: [Path.home()])
    openweather_api_key: str = ""
    apps: dict[str, str] = field(default_factory=dict)
    # --- LLM (opsiyonel) ---
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout: int = 30
    llm_max_history: int = 20
    # --- Güvenlik / özellik ---
    rate_limit_per_min: int = 120
    require_confirm_dangerous: bool = True
    log_dir: Path = field(default_factory=lambda: ROOT / "logs")

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        apps = {}
        for part in _env("JARVIS_APPS", "").split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                apps[k.strip()] = v.strip()
        return cls(
            host=_env("JARVIS_HOST", "0.0.0.0"),
            port=int(_env("JARVIS_PORT", "8765")),
            token=_env("JARVIS_TOKEN", ""),
            allow_shell=_env_bool("JARVIS_ALLOW_SHELL", False),
            allow_dangerous=_env_bool("JARVIS_ALLOW_DANGEROUS", False),
            lang=_env("JARVIS_LANG", "tr-TR"),
            wake_word=_env("JARVIS_WAKE_WORD", "jarvis"),
            openweather_api_key=_env("OPENWEATHER_API_KEY", ""),
            apps=apps,
            llm_provider=_env("JARVIS_LLM_PROVIDER", ""),
            llm_api_key=_env("JARVIS_LLM_API_KEY", "") or _env("OPENAI_API_KEY", ""),
            llm_base_url=_env("JARVIS_LLM_BASE_URL", ""),
            llm_model=_env("JARVIS_LLM_MODEL", "gpt-4o-mini"),
            llm_timeout=int(_env("JARVIS_LLM_TIMEOUT", "30")),
            llm_max_history=int(_env("JARVIS_LLM_MAX_HISTORY", "20")),
            rate_limit_per_min=int(_env("JARVIS_RATE_LIMIT", "120")),
            require_confirm_dangerous=_env_bool("JARVIS_REQUIRE_CONFIRM", True),
        )

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider) or bool(self.llm_api_key)

    def ensure_token(self) -> str:
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(24)
            env = ROOT / ".env"
            txt = env.read_text(encoding="utf-8") if env.exists() else ""
            lines = [l for l in txt.splitlines() if not l.startswith("JARVIS_TOKEN=")]
            lines.append(f"JARVIS_TOKEN={self.token}")
            env.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return self.token
