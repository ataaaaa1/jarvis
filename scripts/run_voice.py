#!/usr/bin/env python3
"""Yerel sesli mod: mikrofonla konuş, hoparlörden dinle (desktop)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    from jarvis.config import Config
    from jarvis.memory import Memory
    from jarvis.brain import Brain
    from jarvis.router import Router
    from jarvis.voice import listen, speak, tts_available

    cfg = Config.from_env()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    brain = Brain(cfg, Memory(cfg.data_dir / "memory.json"))
    router = Router(brain)

    print("JARVIS sesli mod — 'çık' veya 'kapat' ile bitirin.")
    if not tts_available():
        print("(Uyarı: TTS bulunamadı — yanıtlar yazılacak, sesli okunmayacak)")
    try:
        while True:
            print("Dinliyorum…")
            text = listen(cfg.lang)
            if not text:
                print("(anlayamadım, tekrar deneyin)")
                continue
            print(f"Siz: {text}")
            if text.strip().lower() in ("çık", "cik", "kapat", "görüşürüz"):
                speak("Görüşmek üzere, efendim.", cfg.lang)
                break
            reply = router.handle(text)
            print(f"JARVIS: {reply}")
            speak(reply, cfg.lang)
    except KeyboardInterrupt:
        print("\nKapanıyorum.")

if __name__ == "__main__":
    main()
