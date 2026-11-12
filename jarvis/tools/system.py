"""Sistem araçları: bilgi, süreç, ağ, dosya. Windows/Linux/macOS uyumlu."""
from __future__ import annotations
import os, platform, shutil, socket, subprocess, sys
from pathlib import Path

IS_WIN = sys.platform.startswith("win")

def system_info() -> str:
    try:
        up_str = "bilinmiyor"
        if not IS_WIN:
            up = int(float(Path("/proc/uptime").read_text().split()[0]))
            up_str = f"{up//3600}sa {up%3600//60}dk"
        os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"
        user = os.environ.get("USERNAME") or os.environ.get("USER", "?")
        return (f"İşletim sistemi: {os_name}\n"
                f"Bilgisayar adı: {socket.gethostname()}\nÇalışma süresi: {up_str}\nKullanıcı: {user}")
    except Exception as e:
        return f"Sistem bilgisi alınamadı: {e}"

def cpu_info() -> str:
    try:
        if hasattr(os, "getloadavg"):
            load = os.getloadavg()
            return f"CPU yük (1/5/15 dk): {load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}\nÇekirdek: {os.cpu_count()}"
        return f"CPU: {platform.processor() or 'bilinmiyor'}\nÇekirdek: {os.cpu_count()}"
    except Exception as e:
        return f"CPU bilgisi alınamadı: {e}"

def memory_info() -> str:
    try:
        if IS_WIN:
            import ctypes
            class S(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            s = S(); s.dwLength = ctypes.sizeof(S)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
            total = s.ullTotalPhys // (1024**2); avail = s.ullAvailPhys // (1024**2)
            used = total - avail
            return f"Bellek: {used} MB / {total} MB (%{s.dwMemoryLoad} kullanılıyor, {avail} MB boş)"
        info = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            info[k] = int(v.strip().split()[0]) // 1024
        total, avail = info.get("MemTotal", 0), info.get("MemAvailable", 0)
        used = total - avail
        pct = round(used / total * 100) if total else 0
        return f"Bellek: {used} MB / {total} MB (%{pct} kullanılıyor, {avail} MB boş)"
    except Exception as e:
        return f"Bellek bilgisi alınamadı: {e}"

def disk_info() -> str:
    lines = []
    roots = ["C:\\", str(Path.home())] if IS_WIN else ["/", str(Path.home())]
    for p in roots:
        try:
            t, u, f = shutil.disk_usage(p)
            lines.append(f"{p}: {u//(1024**3)} GB / {t//(1024**3)} GB (%{round(u/t*100)})")
        except Exception:
            pass
    return "\n".join(lines) or "Disk bilgisi alınamadı."

def battery_info() -> str:
    if IS_WIN:
        try:
            import ctypes
            class PS(ctypes.Structure):
                _fields_ = [("ACLineStatus", ctypes.c_ulong), ("Flag", ctypes.c_ulong),
                            ("LifePercent", ctypes.c_ulong), ("LifeTime", ctypes.c_ulong),
                            ("LifeFullTime", ctypes.c_ulong)]
            ps = PS()
            ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(ps))
            return f"Pil: %{ps.LifePercent} ({'AC bağlı' if ps.ACLineStatus else 'pil'} )"
        except Exception:
            return "Pil bilgisi alınamadı."
    try:
        for ps in Path("/sys/class/power_supply").glob("BAT*"):
            return f"Pil: %{(ps/'capacity').read_text().strip()} ({(ps/'status').read_text().strip()})"
    except Exception:
        pass
    return "Pil bilgisi bu cihazda yok."

def list_processes(limit: int = 10) -> str:
    try:
        if IS_WIN:
            out = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True, timeout=5)
            lines = out.stdout.splitlines()[1:1 + limit]
            return "\n".join(l[:110] for l in lines) or "Süreç yok."
        out = subprocess.run(["ps", "aux", "--sort=-%cpu"], capture_output=True, text=True, timeout=5)
        lines = out.stdout.splitlines()[1:1 + limit]
        return "\n".join(l[:110] for l in lines) or "Süreç yok."
    except Exception as e:
        return f"Süreçler listelenemedi: {e}"

def network_info() -> str:
    try:
        return f"Bilgisayar adı: {socket.gethostname()}\nIP: {socket.gethostbyname(socket.gethostname())}"
    except Exception as e:
        return f"Ağ bilgisi alınamadı: {e}"

def list_files(path: str = ".") -> str:
    try:
        p = Path(path).expanduser().resolve()
        items = sorted(p.iterdir(), key=lambda x: x.name.lower())
        out = [f"[{'D' if it.is_dir() else 'F'}] {it.name}" for it in items[:60]]
        if len(items) > 60:
            out.append(f"... ve {len(items)-60} öğe daha")
        return f"{p} içeriği:\n" + "\n".join(out) if out else f"{p} boş."
    except Exception as e:
        return f"Klasör okunamadı: {e}"

def read_file(path: str, max_chars: int = 4000) -> str:
    try:
        t = Path(path).expanduser().read_text(encoding="utf-8", errors="replace")
        return t[:max_chars] + (f"\n... ({len(t)-max_chars} karakter daha)" if len(t) > max_chars else "")
    except Exception as e:
        return f"Dosya okunamadı: {e}"

def write_file(path: str, content: str) -> str:
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Yazdım: {p} ({len(content)} karakter)"
    except Exception as e:
        return f"Yazılamadı: {e}"

def make_dir(path: str) -> str:
    try:
        Path(path).expanduser().mkdir(parents=True, exist_ok=True)
        return f"Klasör hazır: {path}"
    except Exception as e:
        return f"Oluşturulmadı: {e}"

def delete_file(path: str) -> str:
    try:
        p = Path(path).expanduser()
        shutil.rmtree(p) if p.is_dir() else p.unlink()
        return f"Sildim: {path}"
    except Exception as e:
        return f"Silinemedi: {e}"

def rename_file(src: str, dst: str) -> str:
    try:
        Path(src).expanduser().rename(Path(dst).expanduser())
        return f"Yeniden adlandırdım: {src} -> {dst}"
    except Exception as e:
        return f"Adlandırılamadı: {e}"

def open_url(url: str) -> str:
    try:
        if IS_WIN:
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", url], check=False, timeout=5)
        return f"Tarayıcıda açıyorum: {url}"
    except Exception as e:
        return f"Açılamadı: {e}"

def open_app(app: str, apps: dict | None = None) -> str:
    cmd = (apps or {}).get(app, app)
    try:
        if IS_WIN:
            os.startfile(cmd)  # type: ignore[attr-defined]
        else:
            subprocess.Popen([cmd])
        return f"Uygulamayı açıyorum: {app}"
    except Exception as e:
        return f"Açılamadı: {e}"

def find_file(pattern: str, start: str = ".") -> str:
    try:
        if IS_WIN:
            hits = []
            for p in Path(start).expanduser().rglob(pattern):
                hits.append(str(p))
                if len(hits) >= 20:
                    break
            return "\n".join(hits) if hits else "Bulunamadı."
        out = subprocess.run(["find", start, "-name", pattern, "-maxdepth", "4"],
                             capture_output=True, text=True, timeout=10)
        hits = out.stdout.strip().splitlines()[:20]
        return "\n".join(hits) if hits else "Bulunamadı."
    except Exception as e:
        return f"Aranamadı: {e}"

def run_command(cmd: str, cfg, confirm_code: str = "", confirm_manager=None) -> str:
    from ..security import is_dangerous
    if not cfg.allow_shell:
        return ("Shell komutları kapalı. Açmak için .env'e JARVIS_ALLOW_SHELL=1 ekleyin. Varsayılan kapalı.")
    if is_dangerous(cmd) and not cfg.allow_dangerous:
        if cfg.require_confirm_dangerous and confirm_manager is not None:
            if not confirm_code:
                code = confirm_manager.request(cmd)
                return (f"⚠ Tehlikeli komut: `{cmd}`\nOnay emri: `onayla {code}` (2 dk geçerli, tek kullanımlık)")
            ok = confirm_manager.consume(confirm_code)
            if ok is None:
                return "Onay kodu geçersiz veya süresi doldu."
            if ok != cmd:
                return "Onay kodu bu komut için değil."
        else:
            return f"Tehlikeli komut engellendi: {cmd}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout or "")[:3000]
        err = (r.stderr or "")[:1000]
        return (out + ("\nHata: " + err if err else "")).strip() or f"Komut çalıştı (kod {r.returncode})."
    except subprocess.TimeoutExpired:
        return "Zaman aşımı: komut 30 saniyede bitmedi."
    except Exception as e:
        return f"Komut çalışmadı: {e}"
