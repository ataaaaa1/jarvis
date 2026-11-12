#!/usr/bin/env python3
"""Windows/macOS/Linux uyumlu kurulum sihirbazı."""
import os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    print("==> JARVIS kurulumu")
    exe = sys.executable
    print(f"Python: {exe} ({sys.version.split()[0]})")
    subprocess.run([exe, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")],
                   check=False)
    env = ROOT / ".env"
    if not env.exists():
        shutil.copy(ROOT / ".env.example", env)
        print(".env oluşturuldu (token ilk çalışmaya kadar boş bırakın)")
    else:
        print(".env mevcut")
    print("==> Testler")
    r = subprocess.run([exe, str(ROOT / "tests/test_brain.py")])
    if r.returncode != 0:
        print("Testler başarısız — logları kontrol edin")
        return 1
    print("==> Tamam")
    print("Başlat:  python run.py")
    print("Telefon: http://<bilgisayar-IP>:8765/?token=<.env'deki JARVIS_TOKEN>")
    print("Telegram (isteğe bağlı): .env'e TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID yazın")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
