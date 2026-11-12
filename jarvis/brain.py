"""Komut beyin: Türkçe doğal dil -> araç/eylem yönlendirme."""
from __future__ import annotations
import re
import unicodedata
from .tools import media, system

def _norm(s: str) -> str:
    s = s.replace("İ", "i").lower().strip()
    s = unicodedata.normalize("NFC", s)
    table = str.maketrans({
        "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S",
        "ı": "i", "İ": "I", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C",
    })
    return s.translate(table)

def _arg_int(text: str, default: int) -> int:
    m = re.search(r"\d+", text)
    return int(m.group()) if m else default

def _arg_after(text: str, keywords: list[str], default: str = "") -> str:
    words = text.split()
    for kw in keywords:
        if kw in words:
            idx = words.index(kw)
            rest = " ".join(words[idx + 1:]).strip()
            if rest:
                return rest
    return default

class Brain:
    def __init__(self, cfg, memory):
        self.cfg = cfg
        self.mem = memory
        from .security import ConfirmManager
        self.confirm = ConfirmManager()

    def handle(self, raw: str) -> str:
        t = _norm(raw)
        if not t:
            return "Sizi dinliyorum, efendim. Nasıl yardımcı olabilirim?"
        # -- Selamlama / kapanış --
        if t in ("merhaba", "selam", "hey", "gunaydin", "iyi aksamlar", "hello", "hi"):
            return "Merhaba efendim. Sistemler online. Size nasıl yardımcı olabilirim?"
        if t in ("tesekkurler", "sagol", "eyvallah", "thank you"):
            return "Rica ederim efendim. Başka bir şey ister misiniz?"
        if t in ("gorusuruz", "hoşçakal", "kapat", "bye"):
            return "Görüşmek üzere efendim. Kapanıyorum."
        if "nasilsin" in t or "iyi misin" in t:
            return "Çok iyiyim efendim, teşekkür ederim. Tüm modüllerim çalışıyor."
        if "yardim" in t:
            return self._help()
        # -- Zaman --
        if "saat" in t or "zaman" in t:
            return media.time_now()
        if "tarih" in t or "bugun" in t:
            return media.date_today()
        # -- Sistem bilgisi --
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
        # -- Dosya --
        if t.startswith("listele") or ("klasor" in t and "listele" in t):
            return system.list_files(_arg_after(t, ["listele"], "."))
        if t.startswith("oku"):
            return system.read_file(_arg_after(t, ["oku"]))
        if t.startswith("yaz"):
            parts = t.split(":", 1)
            if len(parts) == 2:
                path, content = parts[0].replace("yaz", "").strip(), parts[1].strip()
                return system.write_file(path, content)
            return "Yazmak için format: yaz <yol>: <içerik>"
        if "klasor olustur" in t or "yeni klasor" in t or t.startswith("klasor ac"):
            return system.make_dir(_arg_after(t, ["olustur", "ac", "klasor"]))
        if t.startswith("sil"):
            return system.delete_file(_arg_after(t, ["sil"]))
        if "yeniden adlandir" in t or "yeniden isimlendir" in t:
            return "Format: yeniden adlandır <eski> -> <yeni>"
        if "bul" in t and ("dosya" in t or "klasor" in t or "ara" in t):
            return system.find_file(_arg_after(t, ["ara", "bul"]))
        # -- Tarayıcı / uygulama --
        if t.startswith("ac") and ("http" in t or "www" in t or ".com" in t or ".org" in t):
            return system.open_url(_arg_after(t, ["ac"]))
        if "tarayici" in t and "ac" in t:
            return system.open_url(_arg_after(t, ["ac"]))
        if "uygulama ac" in t:
            return system.open_app(_arg_after(t, ["ac"]), self.cfg.apps)
        # -- Medya / donanım --
        if "ses" in t:
            if "kapat" in t:
                return media.mute(True)
            if "ac" in t:
                return media.mute(False)
            m = re.search(r"%?\s*(\d+)", t)
            return media.volume(int(m.group(1)) if m else None)
        if "wifi" in t:
            return media.wifi_toggle("kapat" not in t)
        if "parlaklik" in t:
            m = re.search(r"%?\s*(\d+)", t)
            return media.brightness(int(m.group(1)) if m else 50)
        if "ekran goruntusu" in t:
            return media.screenshot(_arg_after(t, ["al"], "jarvis_screenshot.png"))
        # -- Bilgi --
        if "hava durumu" in t or t.startswith("hava"):
            city = _arg_after(t, ["durumu", "hava"], "istanbul")
            return media.weather(city, self.cfg.openweather_api_key)
        if "hesapla" in t or t.startswith("hesap"):
            return media.calculate(_arg_after(t, ["hesapla", "hesap"]))
        if "zar" in t:
            return media.roll_dice(_arg_int(t, 6))
        if "espri" in t:
            return media.joke()
        # -- Web --
        if "ara" in t or t.startswith("webde ara"):
            return media.search_web(_arg_after(t, ["ara"]))
        if "sayfasi getir" in t or "web sayfasi" in t:
            return media.web_fetch(_arg_after(t, ["getir"]))
        # -- Hafıza --
        if t.startswith("not al"):
            return self.mem.add_note(raw.split(":", 1)[-1].strip() or raw[6:].strip())
        if t.startswith("notlar"):
            notes = self.mem.list_notes()
            return "\n".join(f"- {n['text']}" for n in notes) if notes else "Not yok."
        if "hatirla" in t and "=" in t:
            k, v = t.split("=", 1)
            return self.mem.set_fact(k.replace("hatirla", "").strip(), v.strip())
        if t.startswith("hatirla") or t.startswith("unutma"):
            facts = self.mem.all_facts()
            return "\n".join(f"{k} = {v}" for k, v in facts.items()) if facts else "Hatırda kayıt yok."
        if t.startswith("hatirlat"):
            secs = _arg_int(t, 60)
            text = re.sub(r"\d+\s*(sn|saniye)?", "", t).replace("hatirlat", "").strip() or "Hatırlatma"
            return self.mem.add_reminder(text, secs)
        # -- Komut --
        if "calistir" in t or t.startswith("komut"):
            return system.run_command(_arg_after(t, ["calistir", "komut"]), self.cfg)
        return self._fallback(t, raw)

    def _fallback(self, t: str, raw: str) -> str:
        return (f"'{raw}' için bir eylem bulamadım. 'yardım' yazarak yapabileceklerimi görebilirsiniz. "
                f"Örnek: 'sistem bilgisi', 'bellek', 'saat', 'tarayıcıda aç ...'")

    def _help(self) -> str:
        return ("Yapabileceklerim:\n"
                "• saat / tarih / sistem bilgisi / cpu / bellek / disk / pil / süreç / ağ\n"
                "• listele ~ / oku <dosya> / yaz <yol>: <içerik> / yeni klasör <yol>\n"
                "• tarayıcıda aç <url> / uygulama aç <ad>\n"
                "• ses %50 / sesi kapat / wifi kapat / parlaklık %70\n"
                "• hava durumu <şehir> / hesapla 12+34 / zar at / espri yap\n"
                "• ekran görüntüsü al / web sayfası getir <url>\n"
                "• not al: <metin> / hatırla: <anahtar> = <değer> / hatırlat: <metin> (<sn> sn)\n"
                "• komut çalıştır <shell> (yalnızca JARVIS_ALLOW_SHELL=1 ise)")
