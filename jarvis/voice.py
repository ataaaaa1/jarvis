"""Ses: TTS (Windows SAPI / espeak / pyttsx3 / gTTS) ve STT."""
from __future__ import annotations
import shutil, subprocess, sys

IS_WIN = sys.platform.startswith("win")

def _speak_windows(text: str) -> bool:
    """Windows SAPI üzerinden Türkçe ses; yoksa False döner."""
    try:
        ps = (
            "$s = New-Object -ComObject SAPI.SpVoice; "
            "$s.Rate = 0; "
            "$s.Speak([System.Console]::In.ReadToEnd())"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], input=text.encode("utf-8"),
                       timeout=30, check=True)
        return True
    except Exception:
        return False

def speak(text: str, lang: str = "tr-TR") -> None:
    """Türkçe metni sesli oku. Hiçbir TTS yoksa sessizce geç."""
    if IS_WIN and _speak_windows(text):
        return
    if shutil.which("espeak") or shutil.which("espeak-ng"):
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        try:
            subprocess.run([exe, "-v", "tr", text[:500]], timeout=30, check=False)
            return
        except Exception:
            pass
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return
    except Exception:
        pass
    try:
        from gtts import gTTS
        import io
        audio = io.BytesIO()
        gTTS(text=text, lang="tr").write_to_fp(audio)
        audio.seek(0)
        if shutil.which("mpv"):
            subprocess.run(["mpv", "--no-video", "-"], input=audio.read(), timeout=30)
        elif shutil.which("ffplay"):
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-"], input=audio.read(), timeout=30)
    except Exception:
        pass

def listen(lang: str = "tr-TR", timeout: int = 5) -> str | None:
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=8)
        try:
            return r.recognize_google(audio, language=lang)
        except Exception:
            return None
    except Exception:
        return None

def tts_available() -> bool:
    return bool(shutil.which("espeak") or shutil.which("espeak-ng")) or _has("pyttsx3") or _has("gtts")

def _has(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False
