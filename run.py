#!/usr/bin/env python3
"""JARVIS başlatıcı."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    ap = argparse.ArgumentParser(description="JARVIS — Kişisel yapay zekâ asistanı")
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--command", "-c", help="Tek seferlik komut çalıştır (örn: 'saat kaç')")
    ap.add_argument("--speak", action="store_true", help="Yanıtı sesli oku")
    args = ap.parse_args()

    from jarvis.config import Config, load_dotenv
    load_dotenv()
    cfg = Config.from_env()
    if args.host:
        cfg.host = args.host
    if args.port:
        cfg.port = args.port
    cfg.data_dir.mkdir(parents=True, exist_ok=True)

    from jarvis.memory import Memory
    from jarvis.brain import Brain
    from jarvis.router import Router
    brain = Brain(cfg, Memory(cfg.data_dir / "memory.json"))
    router = Router(brain)

    if args.command:
        reply = router.handle(args.command)
        print(reply)
        if args.speak:
            from jarvis.voice import speak
            speak(reply, cfg.lang)
        return

    from jarvis.server import amain
    import asyncio
    print("JARVIS başlatılıyor…")
    asyncio.run(amain())

if __name__ == "__main__":
    main()
