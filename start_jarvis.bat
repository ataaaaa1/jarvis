@echo off
title JARVIS
cd /d "%~dp0"
echo =======================================
echo    J.A.R.V.I.S - Calistiriliyor
echo =======================================
echo.
echo [Kontrol 1/4] Python araniyor...
where python >nul 2>nul
if %errorlevel% equ 0 goto PYOK
echo [HATA] Python bulunamadi!
echo.
echo COZUM: 1) python.org acin
echo        2) Download Python butonuna tiklayin
echo        3) Kurulumda en altta "Add python.exe to PATH" kutusunu
echo           ISARETLEYIN, sonra Install Now tiklayin
echo        4) Bilgisayari yeniden baslatin
echo.
pause
exit /b 1
:PYOK
python --version
echo [OK] Python bulundu.
echo.
echo [Kontrol 2/4] Dosyalar kontrol ediliyor...
if exist run.py goto DOSYA2
echo [HATA] run.py bulunamadi!
echo Bu .bat dosyasinin yaninda run.py olmali. ZIP'i dogru cikardiniz mi?
pause
exit /b 1
:DOSYA2
if exist "jarvis\server.py" goto DOSYA3
echo [HATA] jarvis klasoru bulunamadi!
echo ZIP'i dogru cikardiniz mi? Icinde "jarvis" klasoru olmali.
pause
exit /b 1
:DOSYA3
echo [OK] Dosyalar tamam.
echo.
echo [Kontrol 3/4] Gerekli paketler kuruluyor (websockets)...
python -m pip install -q -r requirements.txt
echo [OK] Paket kurulumu bitti.
echo.
echo [Kontrol 4/4] Sunucu baslatiliyor...
echo.
echo Kapatmak icin CTRL+C veya pencereyi kapatin.
echo.
ipconfig | findstr /c:"IPv4"
echo.
echo Telefondan acmak icin (telefon ve PC AYNI Wi-Fi'da olmali):
echo   http://BILGISAYAR-IP:8765/?token=<ustteki Token>
echo.
echo Once PC'de test edin: http://127.0.0.1:8765/?token=<Token>
echo Windows Guvenlik Duvari sorarsa "Ozellik aglara izin ver"i isaretleyin.
echo.
python run.py --host 0.0.0.0 --port 8765
echo.
echo JARVIS durdu.
pause
