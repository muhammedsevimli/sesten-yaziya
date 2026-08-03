"""sesten-yaziya · dikte modu: HER uygulamada bas-konuş, metin imlecin olduğu yere yazılsın.

Kullanım:
    python dikte.py                (F8: kaydı başlat/durdur · Esc: çık)
    python dikte.py --tus f9       (kısayolu değiştir)
    python dikte.py --panoya       (imlece yazma, yalnız panoya kopyala)
    python dikte.py --model medium

Akış: WhatsApp, mail, doküman, neredeysen orada kal. F8'e bas, konuş, tekrar F8.
Metin çevrilir ve imlecin olduğu alana kendiliğinden yapışır. Her şey bilgisayarında
çalışır, ses hiçbir yere gitmez.

Not: Windows'ta ek izin gerekmez. Linux'ta `keyboard` kütüphanesi root ister.
"""

import argparse
import queue
import sys
import time

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

ORNEKLEME = 16000


class Dikte:
    def __init__(self, model, panoya_modu: bool):
        self.model = model
        self.panoya_modu = panoya_modu
        self.kayitta = False
        self.kuyruk: "queue.Queue[np.ndarray]" = queue.Queue()
        self.akis = None

    def _dinle(self, parca, *_):
        self.kuyruk.put(parca.copy())

    def baslat_durdur(self):
        import sounddevice as sd

        if not self.kayitta:
            while not self.kuyruk.empty():
                self.kuyruk.get()
            self.akis = sd.InputStream(
                samplerate=ORNEKLEME, channels=1, dtype="float32", callback=self._dinle
            )
            self.akis.start()
            self.kayitta = True
            print("● kayıt... (durdurmak için aynı tuş)")
            return

        self.akis.stop()
        self.akis.close()
        self.kayitta = False

        parcalar = []
        while not self.kuyruk.empty():
            parcalar.append(self.kuyruk.get())
        if not parcalar:
            print("boş kayıt\n")
            return
        ses = np.concatenate(parcalar).flatten()
        if ses.size < ORNEKLEME // 2:
            print("kayıt çok kısa, tekrar dene\n")
            return

        print("çevriliyor...")
        segmentler, _ = self.model.transcribe(ses, language="tr", vad_filter=True, beam_size=5)
        metin = " ".join(s.text.strip() for s in segmentler).strip()
        if not metin:
            print("konuşma algılanamadı\n")
            return

        print(f"→ {metin}\n")
        self._yaz(metin)

    def _yaz(self, metin: str):
        """Metni imlecin olduğu alana bırakır: pano + Ctrl+V (Türkçe için en güvenilir yol),
        ardından eski pano içeriği geri konur. --panoya modunda yalnız kopyalar."""
        import keyboard
        import pyperclip

        if self.panoya_modu:
            pyperclip.copy(metin)
            print("(panoya kopyalandı, Ctrl+V ile yapıştır)\n")
            return

        eski = None
        try:
            eski = pyperclip.paste()
        except Exception:
            pass
        pyperclip.copy(metin)
        time.sleep(0.15)  # pano oturmadan V basılırsa eski içerik yapışıyor
        keyboard.send("ctrl+v")
        if eski is not None:
            time.sleep(0.35)
            try:
                pyperclip.copy(eski)
            except Exception:
                pass


def main() -> None:
    p = argparse.ArgumentParser(description="Her uygulamada Türkçe dikte (bas-konuş-yapışsın).")
    p.add_argument("--model", default="small", help="whisper modeli: small (varsayılan) / medium")
    p.add_argument("--tus", default="f8", help="kayıt kısayolu (varsayılan: f8)")
    p.add_argument("--panoya", action="store_true", help="imlece yazma, yalnız panoya kopyala")
    args = p.parse_args()

    import keyboard
    from faster_whisper import WhisperModel

    print(f"model yükleniyor: {args.model} (ilk çalıştırmada indirilir)")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    d = Dikte(model, args.panoya)
    keyboard.add_hotkey(args.tus, d.baslat_durdur)
    print(f"hazır. istediğin uygulamaya geç → {args.tus.upper()}: kayıt başlat/durdur · Esc: çık\n")
    keyboard.wait("esc")
    print("çıkıldı.")


if __name__ == "__main__":
    main()
