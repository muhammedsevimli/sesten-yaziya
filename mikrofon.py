"""sesten-yaziya · mikrofon modu: konuş, Türkçe yazıya çevirsin.

Kullanım:
    python mikrofon.py                 (Enter: kaydı başlat/durdur, q + Enter: çık)
    python mikrofon.py --model medium
    python mikrofon.py --kaydet        (ses kayıtlarını kayitlar/ klasörüne de yazar)

Metin ekrana basılır; pyperclip kuruluysa panoya da kopyalanır
(pip install pyperclip). Her şey bilgisayarında çalışır, ses hiçbir yere gitmez.
"""

import argparse
import queue
import sys
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

ORNEKLEME = 16000  # whisper'ın beklediği örnekleme hızı


def panoya(metin: str) -> bool:
    try:
        import pyperclip

        pyperclip.copy(metin)
        return True
    except Exception:
        return False


def kaydet_wav(ses: np.ndarray, klasor: Path) -> Path:
    klasor.mkdir(parents=True, exist_ok=True)
    yol = klasor / f"kayit-{datetime.now():%Y%m%d-%H%M%S}.wav"
    with wave.open(str(yol), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(ORNEKLEME)
        w.writeframes((ses * 32767).astype(np.int16).tobytes())
    return yol


def kayit_al() -> np.ndarray:
    """Enter'a basılana dek mikrofonu dinler, float32 mono döner."""
    import sounddevice as sd

    kuyruk: "queue.Queue[np.ndarray]" = queue.Queue()

    def dinle(parca, *_):
        kuyruk.put(parca.copy())

    print("kayıt başladı, konuş... (durdurmak için Enter)")
    with sd.InputStream(samplerate=ORNEKLEME, channels=1, dtype="float32", callback=dinle):
        input()
    parcalar = []
    while not kuyruk.empty():
        parcalar.append(kuyruk.get())
    if not parcalar:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(parcalar).flatten()


def main() -> None:
    p = argparse.ArgumentParser(description="Mikrofondan Türkçe dikte.")
    p.add_argument("--model", default="small", help="whisper modeli: small (varsayılan) / medium")
    p.add_argument("--kaydet", action="store_true", help="ses kayıtlarını kayitlar/ altına da yaz")
    args = p.parse_args()

    from faster_whisper import WhisperModel

    print(f"model yükleniyor: {args.model} (ilk çalıştırmada indirilir)")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("hazır. Enter: kayda başla · q + Enter: çık\n")

    while True:
        komut = input("> ")
        if komut.strip().lower() == "q":
            break
        ses = kayit_al()
        if ses.size < ORNEKLEME // 2:  # yarım saniyeden kısa kayıt: boş say
            print("kayıt çok kısa, tekrar dene\n")
            continue
        if args.kaydet:
            print(f"ses yazıldı: {kaydet_wav(ses, Path('kayitlar'))}")
        segmentler, _ = model.transcribe(ses, language="tr", vad_filter=True, beam_size=5)
        metin = " ".join(s.text.strip() for s in segmentler).strip()
        if not metin:
            print("konuşma algılanamadı\n")
            continue
        print(f"\n{metin}\n")
        if panoya(metin):
            print("(panoya kopyalandı)\n")


if __name__ == "__main__":
    main()
