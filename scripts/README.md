# JARVIS Scripts

| Dosya | Amaç |
|---|---|
| `install.sh` | Debian/Ubuntu tek komut kurulum (venv + araçlar + test) |
| `install.py` | Çapraz platform (Windows/macOS/Linux) kurulum |
| `run_voice.py` | Mikrofondan sesli komut, hoparlörden yanıt (masaüstü) |
| `telegram_bot.py` | Telegram üzerinden kontrol (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID) |
| `jarvis.service` | systemd servisi — `__KULLANICI__` ve `__JARVIS_YOLU__` değiştirip `/etc/systemd/system/`'e kopyalayın, `systemctl enable --now jarvis` |
