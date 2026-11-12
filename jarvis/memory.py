"""Uzun süreli hafıza: notlar, gerçekler, hatırlatıcılar (JSON dosyası)."""
from __future__ import annotations
import json, time, uuid
from pathlib import Path

class Memory:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = {"facts": {}, "notes": [], "reminders": [], "history": []}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                pass

    def _save(self):
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_fact(self, key: str, value: str):
        self._data["facts"][key] = value; self._save()
        return f"Unutmayacağım: {key} = {value}"

    def get_fact(self, key: str) -> str | None:
        return self._data["facts"].get(key)

    def all_facts(self) -> dict:
        return dict(self._data["facts"])

    def add_note(self, text: str) -> str:
        n = {"id": str(uuid.uuid4())[:8], "text": text, "ts": time.time()}
        self._data["notes"].append(n); self._save()
        return f"Not aldım: {text}"

    def list_notes(self) -> list[dict]:
        return list(self._data["notes"])[-20:]

    def add_reminder(self, text: str, delay_sec: int = 60) -> str:
        r = {"id": str(uuid.uuid4())[:8], "text": text, "at": time.time() + delay_sec, "done": False}
        self._data["reminders"].append(r); self._save()
        return f"{delay_sec} saniye sonra hatırlatacağım: {text}"

    def due_reminders(self) -> list[dict]:
        now = time.time()
        due = [r for r in self._data["reminders"] if not r["done"] and r["at"] <= now]
        for r in due:
            r["done"] = True
        if due:
            self._save()
        return due

    def add_history(self, user: str, assistant: str, limit: int = 40):
        self._data["history"].append({"u": user, "a": assistant, "ts": time.time()})
        self._data["history"] = self._data["history"][-limit:]
        self._save()

    def history_messages(self, system_prompt: str, max_msgs: int = 20) -> list[dict]:
        msgs = [{"role": "system", "content": system_prompt}]
        for h in self._data["history"][-max_msgs:]:
            msgs.append({"role": "user", "content": h["u"]})
            msgs.append({"role": "assistant", "content": h["a"]})
        return msgs
