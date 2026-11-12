#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> JARVIS kurulumu"
python3 -m venv .venv 2>/dev/null || true
if [ -x .venv/bin/pip ]; then PIP=.venv/bin/pip; else PIP="pip3"; fi
$PIP install -q -r requirements.txt 2>/dev/null || echo "pip install başarısız (ağ yoksa stdlib ile çalışır)"
if [ ! -f .env ]; then cp .env.example .env; echo ".env oluşturuldu"; fi
echo "==> Sistem araçları (debian/ubuntu)"
sudo apt-get update -qq && sudo apt-get install -y -qq \
  espeak-ng scrot mpv brightnessctl nmcli 2>/dev/null || echo "Bazı araçlar atlandı"
python3 tests/test_brain.py
echo "==> Tamam. Başlatmak için: python3 run.py   (telefonda http://<IP>:8765/?token=...)"
