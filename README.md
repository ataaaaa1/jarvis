# J.A.R.V.I.S — Just A Rather Very Intelligent System

kişisel, Türkçe konuşan, telefondan ve masaüstünden kontrol edilebilen yapay zekâ asistanı (Python 3.11+, stdlib-first).

## Hızlı Başlangıç

```bash
pip install -r requirements.txt        # websockets + opsiyonel ses paketleri
python3 run.py                          # http://0.0.0.0:8765
# Telefonda açın: http://<bilgisayar-IP>:8765/?token=<.env'deki JARVIS_TOKEN>
```

İlk çalıştırmada token otomatik üretilir ve `.env`'e yazılır.

## Tek komutla kurulum

```bash
bash scripts/install.sh      # debian/ubuntu
python scripts/install.py    # tüm platformlar
python scripts/run_voice.py  # masaüstünde sesli mod
```

## Özellikler

- **Komutlar (40+)**: saat/tarih, sistem/CPU/RAM/disk/pil/süreç/ağ, dosya listele-oku-yaz-sil, tarayıcı/uygulama açma, ses/Wi-Fi/Bluetooth/parlaklık, hava durumu (OpenWeather), hesap, ekran görüntüsü, kilitle/me MüziK çal, web arama/sayfa getirme, not/hatırlatma/hatırlama (kalıcı hafıza).
- **LLM modu**: `JARVIS_LLM_PROVIDER=openai|ollama|anthropic` + `JARVIS_LLM_API_KEY` ayarla; kural motoru eşleşmezse sohbet LLM'e gider (konuşma geçmişi saklanır).
- **Telefon paneli**: WebSocket + REST, sesli komut (🎤, Web Speech API), sesli yanıt (speechSynthesis), hızlı butonlar, otomatik yeniden bağlanma.
- **Güvenlik**: token zorunluluğu, rate-limit (dk 120), denetim kaydı (`logs/audit.jsonl`), tehlikeli shell komutları onay kodlu (`onayla <kod>`), shell varsayılan kapalı.
- **Telegram**: `scripts/telegram_bot.py` (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).
- **Oto-başlatma**: `scripts/jarvis.service` (systemd).

## Yapı

```
jarvis/
├── brain.py        # Türkçe normalleştirme + yardımcılar
├── router.py       # kural motoru → LLM → fallback
├── llm.py          # OpenAI-uyumlu / Ollama / Anthropic (stdlib HTTP)
├── memory.py       # notlar, gerçekler, hatırlatmalar, konuşma geçmişi
├── security.py     # token, rate-limit, onay, denetim, tehlikeli komut filtresi
├── voice.py        # TTS (espeak/pyttsx3/gTTS) + STT (SpeechRecognition)
├── server.py       # HTTP + WebSocket, telefon paneli
├── tools/
│   ├── system.py   # sistem/dosya/shell araçları
│   └── media.py    # ses/video/donanım/bilgi araçları
└── web/index.html  # mobil panel
scripts/            # kurulum, sesli mod, telegram, systemd
tests/test_brain.py # 12 test
```

## Test

```bash
python3 tests/test_brain.py
python3 run.py --command "saat kaç"   # tek seferlik
```

## Güvenlik uyarısı

Token sızarsa telefon paneli tam kontrol demektir — token'ı paylaşmayın, mümkünse Tailscale/VPN arkasında çalıştırın. Shell komutları varsayılan kapalıdır; açmak için `.env`'e `JARVIS_ALLOW_SHELL=1`.
