@echo off
chcp 65001 >nul
title JARVIS
cd /d "%~dp0"
> jarvis_log.txt echo ================ JARVIS LOG ================
echo Tarih: %date% %time%>> jarvis_log.txt
echo Bulundugun klasor: %cd%>> jarvis_log.txt
echo ===========================================>> jarvis_log.txt
echo.
echo =======================================
echo    J.A.R.V.I.S - Calistiriliyor
echo =======================================
echo.
echo [Kontrol 1/4] Python araniyor...
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo [HATA] Python bulunamadi!>> jarvis_log.txt
  echo.
  echo [HATA] Python bulunamadi!
  echo Lutfen python.org adresinden Python 3.11+ kurun.
  echo Kurulumda mutlaka "Add python.exe to PATH" kutusunu isaretleyin!
  echo.
  echo COZUM: python.org -> Download Python -> kurarken alttaki
  echo "Add python.exe to PATH" kutusunu ISARETLEYIN -> Install
  echo.
  pause
  exit /b 1
)
python --version
python --version >> jarvis_log.txt
python -c "import sys; print(sys.executable)" >> jarvis_log.txt
echo [OK] Python bulundu.
echo.

echo [Kontrol 2/4] Dosyalar kontrol ediliyor...
if not exist run.py (
  echo [HATA] run.py bulunamadi!>> jarvis_log.txt
  echo [HATA] run.py bulunamadi!
  echo Bu .bat dosyasinin yaninda run.py ve jarvis klasoru olmali.
  echo ZIP'i dogru cikardiniz mi kontrol edin.
  pause
  exit /b 1
)
if not exist jarvis\server.py (
  echo [HATA] jarvis klasoru bulunamadi!>> jarvis_log.txt
  echo [HATA] jarvis\server.py bulunamadi!
  echo ZIP'i dogru cikardiniz mi kontrol edin. Icinde "jarvis" klasoru olmali.
  pause
  exit /b 1
)
echo [OK] Dosyalar tamam.
echo.

echo [Kontrol 3/4] Gerekli paketler kuruluyor (websockets)...
python -m pip install -q -r requirements.txt >> jarvis_log.txt 2>&1
echo [OK] Paket kurulumu bitti (hata varsa jarvis_log.txt'ye bakin).
echo.

echo [Kontrol 4/4] Sunucu baslatiliyor...
echo.
echo Kapatmak icin CTRL+C veya pencereyi kapatin.
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
echo Bilgisayar IP adresiniz: %IP%
echo.
echo Telefondan acmak icin (telefon ve PC AYNI Wi-Fi'da olmali):
echo   http://%IP%:8765/?token=<ustteki Token>
echo.
echo Once PC'de test edin: http://127.0.0.1:8765/?token=<Token>
echo Windows Guvenlik Duvari sorarsa "Ozellik aglara izin ver"i isaretleyin.
echo.
python run.py --host 0.0.0.0 --port 8765 >> jarvis_log.txt 2>&1

echo.
echo JARVIS durdu. Hatayi gormek icin jarvis_log.txt dosyasini acin.
type jarvis_log.txt
pause
