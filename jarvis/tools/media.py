"""Medya, zaman, bilgi ve yardımcı araçlar."""
from __future__ import annotations
import json, math, random, subprocess, urllib.parse, urllib.request
from datetime import datetime

def time_now() -> str:
    return f"Şu an {datetime.now().strftime('%H:%M')}, {datetime.now().strftime('%d %B %Y %A')}"

def date_today() -> str:
    return datetime.now().strftime("%d %B %Y %A")

import sys
IS_WIN = sys.platform.startswith("win")

def volume(level: int | None = None) -> str:
    try:
        if IS_WIN:
            if level is not None:
                subprocess.run(["powershell", "-Command",
                                f"(New-Object -ComObject SndVolSO).SetMasterVolume({level},0)"],
                               timeout=10, check=False)
                return f"Ses seviyesi % {level} yaptım."
            return "Windows ses seviyesi okunamadı (bilgi amaçlı)."
        if level is not None:
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"], timeout=5)
            return f"Ses seviyesi % {level} yaptım."
        out = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "Ses bilgisi yok."
    except Exception:
        return "Ses kontrolü bu sistemde yok."

def mute(m: bool = True) -> str:
    try:
        if IS_WIN:
            return "Windows'ta ses sessize alma için medya tuşlarını kullanın."
        subprocess.run(["pactl", "set-mute", "@DEFAULT_SINK@", "1" if m else "0"], timeout=5)
        return "Sesi kapattım." if m else "Sesi açtım."
    except Exception:
        return "Ses kontrolü yok."

def wifi_toggle(on: bool = True) -> str:
    try:
        if IS_WIN:
            import ctypes
            val = 1 if on else 0
            ctypes.windll.wlanapi.WLANCloseHandle
            return "Windows'ta Wi-Fi kontrolü için WLAN API gerekli — el ile açın." if not on else "Wi-Fi zaten açık varsayılıyor."
        subprocess.run(["nmcli", "radio", "wifi", "on" if on else "off"], timeout=10)
        return "Wi-Fi açıldı." if on else "Wi-Fi kapatıldı."
    except Exception:
        return "Wi-Fi kontrolü yok."

def brightness(level: int = 50) -> str:
    try:
        if IS_WIN:
            subprocess.run(["powershell", "-Command",
                            f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"],
                           timeout=10, check=False)
            return f"Parlaklık % {level} (WMI)."
        subprocess.run(["brightnessctl", "set", f"{level}%"], timeout=5)
        return f"Parlaklık % {level}."
    except Exception:
        return "Parlaklık kontrolü yok."

def weather(city: str, api_key: str = "") -> str:
    if not api_key:
        return "Hava durumu için OPENWEATHER_API_KEY gerekli. Ücretsiz anahtar: openweathermap.org"
    try:
        url = ("https://api.openweathermap.org/data/2.5/weather?q="
               + urllib.parse.quote(city) + "&appid=" + api_key + "&units=metric&lang=tr")
        d = json.loads(urllib.request.urlopen(url, timeout=10).read())
        w = d["weather"][0]["description"]
        t = round(d["main"]["temp"]); feels = round(d["main"]["feels_like"])
        return f"{city}: {t}°C, {w}. Hissedilen {feels}°C."
    except Exception as e:
        return f"Hava durumu alınamadı: {e}"

def search_web(query: str) -> str:
    return (f"Arama: '{query}'\nDuckDuckGo: https://duckduckgo.com/?q={urllib.parse.quote(query)}\n"
            f"Google: https://www.google.com/search?q={urllib.parse.quote(query)}")

def calculate(expr: str) -> str:
    allowed_expr = "".join(c for c in expr if c in "0123456789+-*/().,% ")
    try:
        result = eval(allowed_expr, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
        return f"{expr} = {result}"
    except Exception as e:
        return f"Hesaplanamadı: {e}"

def roll_dice(sides: int = 6) -> str:
    return f"Zar attım: {random.randint(1, sides)} (d{sides})"

def joke() -> str:
    jokes = [
        "Bilgisayar neden doktora gitti? Virüsü vardı!",
        "Programcı neden karanlıkta çalışır? Çünkü böcekler ışıktan korkar.",
        "Neden bilgisayar müzesine gitmedim? Çünkü her şeyin formatı var.",
        "Klavye neden intihar etmek istedi? Çünkü hayatı tuşlarla doluydu.",
        "Wi-Fi sinyalim zayıf, sanırım router'ın canı sıkkın.",
    ]
    return random.choice(jokes)

def screenshot(path: str = "screenshot.png") -> str:
    if IS_WIN:
        try:
            subprocess.run(["powershell", "-Command",
                            f"Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; "
                            f"$b=[System.Drawing.Bitmap]::new([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
                            f"$g=[System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$b.Size); $b.Save('{path}'); $g.Dispose(); $b.Dispose()"],
                           timeout=10, check=True)
            return f"Ekran görüntüsü alındı: {path}"
        except Exception as e:
            return f"Ekran görüntüsü alınamadı: {e}"
    for cmd in (["scrot", path], ["import", "-window", "root", path],
                ["gnome-screenshot", "-f", path]):
        try:
            subprocess.run(cmd, timeout=10, check=True)
            return f"Ekran görüntüsü alındı: {path}"
        except Exception:
            continue
    return "Ekran görüntüsü alınamadı (scrot/ImageMagick/gnome-screenshot gerekli)."

def play_audio(path: str) -> str:
    import shutil, os
    if IS_WIN:
        try:
            os.startfile(path)  # type: ignore[attr-defined]
            return f"Çalıyorum: {path}"
        except Exception as e:
            return f"Ses oynatılamadı: {e}"
    for exe, args in (("mpv", ["mpv", path]), ("ffplay", ["ffplay", "-nodisp", "-autoexit", path])):
        if shutil.which(exe):
            try:
                subprocess.run(args, timeout=30, check=False)
                return f"Çalıyorum: {path}"
            except Exception:
                pass
    return "Ses oynatılamadı (mpv/ffplay gerekli, dosya var mı kontrol edin)."

def open_folder(path: str) -> str:
    try:
        if IS_WIN:
            import os
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", path], check=False, timeout=5)
        return f"Klasörü açıyorum: {path}"
    except Exception as e:
        return f"Açılamadı: {e}"

def bluetooth_toggle(on: bool = True) -> str:
    try:
        if IS_WIN:
            return "Windows'ta Bluetooth için Ayarlar > Bluetooth'u kullanın."
        subprocess.run(["bluetoothctl", "power", "on" if on else "off"], timeout=10)
        return "Bluetooth açıldı." if on else "Bluetooth kapatıldı."
    except Exception:
        return "Bluetooth kontrolü yok."

def lock_screen() -> str:
    if IS_WIN:
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], timeout=5, check=True)
            return "Ekran kilitlendi."
        except Exception:
            return "Ekran kilitlenemedi."
    for cmd in (["loginctl", "lock-session"], ["gnome-screensaver-command", "-l"], ["xscreensaver-command", "-lock"]):
        try:
            subprocess.run(cmd, timeout=5, check=True)
            return "Ekran kilitlendi."
        except Exception:
            continue
    return "Ekran kilitlenemedi."

def web_fetch(url: str, max_chars: int = 3000) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "replace")
        return html[:max_chars]
    except Exception as e:
        return f"Sayfa alınamadı: {e}"
