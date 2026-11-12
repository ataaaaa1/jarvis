@echo off
chcp 65001 >nul
title JARVIS
cd /d "%~dp0"
echo =======================================
echo    J.A.R.V.I.S - Calistiriliyor
echo =======================================

where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [HATA] Python bulunamadi!
  echo Lutfen python.org adresinden Python 3.11+ kurun.
  echo Kurulumda mutlaka "Add python.exe to PATH" kutusunu isaretleyin!
  pause
  exit /b 1
)

python --version
echo.

echo [1/2] Gerekli paketler kuruluyor...
python -m pip install -q -r requirements.txt
echo.

echo [2/2] Sunucu baslatiliyor...
echo Kapatmak icin CTRL+C veya pencereyi kapatin.
echo.
echo Telefondan acmak icin: http://<BILGISAYAR-IP>:8765/?token=<Token>
echo   - Bilgisayar IP'si icin cmd'de "ipconfig" yazın.
echo   - Windows Guvenlik Duvari acilirsa "Ozellik aglara izin ver"i isaretleyin.
echo.
python run.py --host 0.0.0.0 --port 8765

echo.
echo JARVIS durdu. Kontrol icin BASLAT.txt'ye bakin.
pause
