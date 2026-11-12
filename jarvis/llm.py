"""LLM sağlayıcıları (OpenAI-uyumlu + Ollama + Anthropic). Stdlib HTTP, anahtar yoksa None."""
from __future__ import annotations
import json, urllib.request, urllib.error

SYSTEM_PROMPT = (
    "Sen JARVIS'sin, Türkçe konuşan kişisel bir yapay zekâ asistanı. "
    "Kısa, doğal ve nazik cevap ver. Kullanıcının makinesiyle ilgili somut bilgileri "
    "bilmediğinde tahmin etme, 'bilmiyorum' de. Format: düz metin, madde işaretleri "
    "gerektiğinde. 'Efendim' hitabını doğal ölçüde kullan."
)

def chat(cfg, messages: list[dict]) -> str | None:
    provider = (cfg.llm_provider or "").lower()
    if not provider and cfg.llm_api_key:
        provider = "openai"
    if provider == "ollama":
        return _ollama(cfg, messages)
    if provider == "anthropic":
        return _anthropic(cfg, messages)
    return _openai(cfg, messages)

def _post(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def _openai(cfg, messages) -> str | None:
    base = cfg.llm_base_url or "https://api.openai.com/v1"
    try:
        d = _post(f"{base.rstrip('/')}/chat/completions",
                  {"model": cfg.llm_model, "messages": messages},
                  {"Authorization": f"Bearer {cfg.llm_api_key}"}, cfg.llm_timeout)
        return d["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"LLM hatası: {e}"

def _ollama(cfg, messages) -> str | None:
    base = cfg.llm_base_url or "http://localhost:11434"
    try:
        d = _post(f"{base.rstrip('/')}/api/chat",
                  {"model": cfg.llm_model, "messages": messages, "stream": False}, {}, cfg.llm_timeout)
        return d["message"]["content"].strip()
    except Exception as e:
        return f"Ollama hatası: {e}"

def _anthropic(cfg, messages) -> str | None:
    system = messages[0]["content"] if messages and messages[0]["role"] == "system" else SYSTEM_PROMPT
    rest = messages[1:] if messages and messages[0]["role"] == "system" else messages
    try:
        d = _post("https://api.anthropic.com/v1/messages",
                  {"model": cfg.llm_model, "max_tokens": 1024, "system": system, "messages": rest},
                  {"x-api-key": cfg.llm_api_key, "anthropic-version": "2023-06-01"}, cfg.llm_timeout)
        return d["content"][0]["text"].strip()
    except Exception as e:
        return f"Anthropic hatası: {e}"
