"""Komut yönlendirici: kural motoru önce, LLM sonra."""
from __future__ import annotations
import re
from .brain import _norm, _arg_int, _arg_after, Brain
from .tools import media, system
from . import llm

def is_free_form(text: str) -> bool:
    t = _norm(text)
    free = ["neden", "nasil", "ne demek", "anlat", "soyle", "oneri", "tavsiye",
            "hikaye", "siir", "cevir", "ozetle", "acikla", "ornek", "fark ne", "hangisi"]
    return any(k in t for k in free)

class Router:
    def __init__(self, brain: Brain):
        self.brain = brain

    def handle(self, raw: str) -> str:
        cfg = self.brain.cfg
        reply = self._rules(raw)
        if reply is not None:
            self._record(raw, reply); return reply
        if cfg.llm_enabled and is_free_form(raw):
            msgs = self.brain.mem.history_messages(llm.SYSTEM_PROMPT, cfg.llm_max_history)
            msgs.append({"role": "user", "content": raw})
            out = llm.chat(cfg, msgs)
            if out:
                self._record(raw, out); return out
        reply = f"'{raw}' için bir eylem bulamadım, efendim. 'yardım' yazarak yapabileceklerimi görebilirsiniz."
        self._record(raw, reply); return reply

    def _record(self, raw: str, reply: str):
        try:
            self.brain.mem.add_history(raw, reply)
        except Exception:
            pass

    def _rules(self, raw: str) -> str | None:
        t = _norm(raw)
        if not t:
            return "Sizi dinliyorum, efendim. Nasıl yardımcı olabilirim?"
        if t in ("merhaba", "selam", "hey", "gunaydin", "iyi aksamlar", "hello", "hi"):
            return "Merhaba efendim. Sistemler online. Size nasıl yardımcı olabilirim?"
        if t in ("tesekkurler", "sagol", "eyvallah", "thank you"):
            return "Rica ederim efendim. Başka bir şey ister misiniz?"
        if t.startswith("gorusuruz") or t == "kapat" or t == "bye":
            return "Görüşmek üzere efendim. Kapanıyorum."
        if "nasilsin" in t or "iyi misin" in t:
            return "Çok iyiyim efendim, teşekkür ederim. Tüm modüllerim çalışıyor."
        if "yardim" in t:
            return self._help()
        if "saat" in t or "zaman" in t:
            return media.time_now()
        if "tarih" in t or "bugun" in t:
            return media.date_today()
        if "sistem" in t or "bilgisayar bilgisi" in t:
            return system.system_info()
        if "cpu" in t or "islemci" in t:
            return system.cpu_info()
        if "bellek" in t or "ram" in t:
            return system.memory_info()
        if "disk" in t:
            return system.disk_info()
        if "pil" in t or "batarya" in t:
            return system.battery_info()
        if "surec" in t:
            return system.list_processes(_arg_int(t, 10))
        if "ag" in t or "ip" in t:
            return system.network_info()
        r = self._file_rules(t)
        if r is not None:
            return r
        if t.startswith("onayla"):
            return self._run_pending(_arg_after(t, ["onayla"]))
        if "ses" in t:
            if "kapat" in t: return media.mute(True)
            if "ac" in t: return media.mute(False)
            m = re.search(r"%?\s*(\d+)", t)
            return media.volume(int(m.group(1)) if m else None)
        if "wifi" in t:
            return media.wifi_toggle("kapat" not in t)
        if "bluetooth" in t:
            return media.bluetooth_toggle("kapat" not in t)
        if "parlaklik" in t:
            m = re.search(r"%?\s*(\d+)", t)
            return media.brightness(int(m.group(1)) if m else 50)
        if "ekran goruntusu" in t:
            return media.screenshot(_arg_after(t, ["al"], "jarvis_screenshot.png"))
        if "kilitle" in t:
            return media.lock_screen()
        if "cal" in t and ("muzik" in t or "mp3" in t or "wav" in t):
            return media.play_audio(_arg_after(t, ["cal"]))
        if "hava durumu" in t or t.startswith("hava"):
            return media.weather(_arg_after(t, ["durumu", "hava"], "istanbul"), self.brain.cfg.openweather_api_key)
        if "hesapla" in t or t.startswith("hesap"):
            return media.calculate(_arg_after(t, ["hesapla", "hesap"]))
        if "zar" in t:
            return media.roll_dice(_arg_int(t, 6))
        if "espri" in t:
            return media.joke()
        if "ara" in t:
            return media.search_web(_arg_after(t, ["ara"]))
        if "sayfasi getir" in t or "web sayfasi" in t:
            return media.web_fetch(_arg_after(t, ["getir"]))
        return self._memory_rules(t, raw)

    def _memory_rules(self, t: str, raw: str = "") -> str | None:
        if t.startswith("not al"):
            note = raw.split(":", 1)[-1].strip() or t[6:].strip()
            return self.brain.mem.add_note(note)
        if t.startswith("notlar"):
            notes = self.brain.mem.list_notes()
            return "\n".join(f"- {n['text']}" for n in notes) if notes else "Not yok."
        if "hatirla" in t and "=" in t:
            k, v = t.split("=", 1)
            return self.brain.mem.set_fact(k.replace("hatirla", "").strip(), v.strip())
        if t.startswith("hatirla") or t.startswith("unutma"):
            facts = self.brain.mem.all_facts()
            return "\n".join(f"{k} = {v}" for k, v in facts.items()) if facts else "Hatırda kayıt yok."
        if t.startswith("hatirlat"):
            secs = _arg_int(t, 60)
            text = re.sub(r"\d+\s*(sn|saniye)?", "", t).replace("hatirlat", "").strip() or "Hatırlatma"
            return self.brain.mem.add_reminder(text, secs)
        if "calistir" in t or t.startswith("komut"):
            return system.run_command(_arg_after(t, ["calistir", "komut"]), self.brain.cfg,
                                      confirm_manager=self.brain.confirm)
        return None

    def _file_rules(self, t: str) -> str | None:
        if t.startswith("listele") or ("klasor" in t and "listele" in t):
            return system.list_files(_arg_after(t, ["listele"], "."))
        if t.startswith("oku"):
            return system.read_file(_arg_after(t, ["oku"]))
        if t.startswith("yaz"):
            parts = t.split(":", 1)
            if len(parts) == 2:
                return system.write_file(parts[0].replace("yaz", "").strip(), parts[1].strip())
            return "Yazmak için format: yaz <yol>: <içerik>"
        if "klasor olustur" in t or "yeni klasor" in t or t.startswith("klasor ac"):
            return system.make_dir(_arg_after(t, ["olustur", "ac", "klasor"]))
        if t.startswith("sil"):
            return system.delete_file(_arg_after(t, ["sil"]))
        if t.startswith("ac") and ("http" in t or "www" in t or ".com" in t or ".org" in t):
            return system.open_url(_arg_after(t, ["ac"]))
        if "tarayici" in t and "ac" in t:
            return system.open_url(_arg_after(t, ["ac"]))
        if "uygulama ac" in t:
            return system.open_app(_arg_after(t, ["ac"]), self.brain.cfg.apps)
        if "bul" in t and ("dosya" in t or "klasor" in t):
            return system.find_file(_arg_after(t, ["ara", "bul"]))
        return None

    def _run_pending(self, code: str) -> str:
        action = self.brain.confirm.consume(code)
        if action is None:
            return "Onay kodu geçersiz veya süresi doldu."
        return system.run_command(action, self.brain.cfg, confirm_manager=self.brain.confirm)

    def _help(self) -> str:
        return ("Yapabileceklerim:\n"
                "• saat / tarih / sistem bilgisi / cpu / bellek / disk / pil / süreç / ağ\n"
                "• listele ~ / oku <dosya> / yaz <yol>: <içerik> / yeni klasör <yol> / sil <yol>\n"
                "• tarayıcıda aç <url> / uygulama aç <ad>\n"
                "• ses %50 / sesi kapat / wifi kapat / bluetooth kapat / parlaklık %70 / ekran kilitle\n"
                "• hava durumu <şehir> / hesapla 12+34 / zar at / espri yap\n"
                "• ekran görüntüsü al / web sayfası getir <url> / müzik çal <dosya>\n"
                "• not al: <metin> / notlar / hatırla: <anahtar> = <değer> / hatırlat: <metin> <sn> sn\n"
                "• komut çalıştır <shell> (JARVIS_ALLOW_SHELL=1 ise; tehlikeliler onay ister)\n"
                "Serbest sorular (LLM): 'neden…?', 'anlat…', 'çevir…'")
