"""sesten-yaziya · dikte modu: HER uygulamada bas-konuş, metin imlecin olduğu yere yazılsın.

Windows, macOS ve Linux'ta çalışır.

Kullanım:
    python dikte.py                (F8: kaydı başlat/durdur · Esc: çık)
    python dikte.py --basili       (F8'i BASILI TUT, konuş, bırak; Wispr Flow akışı)
    python dikte.py --tus f9       (kısayolu değiştir)
    python dikte.py --yazarak      (yapıştırma yerine karakter karakter yazar, panoya dokunmaz)
    python dikte.py --panoya       (imlece yazma, yalnız panoya kopyala)
    python dikte.py --model medium

Akış: WhatsApp, mail, doküman, neredeysen orada kal. F8'e bas, konuş, tekrar F8.
Metin çevrilir ve imlecin olduğu alana kendiliğinden yapışır. Her şey bilgisayarında
çalışır, ses hiçbir yere gitmez.

macOS notu: ilk çalıştırmada sistem iki izin ister, ikisi de bir kere verilir:
mikrofon izni ve Sistem Ayarları → Gizlilik ve Güvenlik → Erişilebilirlik (gerekirse
bir de Giriş İzleme) altında Terminal'i işaretlemek. Root/sudo GEREKMEZ.
Linux notu: X11'de çalışır; Wayland masaüstlerinde global kısayol kısıtlı olabilir,
o durumda --panoya modunu kullan.
"""

import argparse
import queue
import sys
import time

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

ORNEKLEME = 16000
MAC = sys.platform == "darwin"


class Dikte:
    def __init__(self, model, panoya_modu: bool, yazarak: bool = False):
        self.model = model
        self.panoya_modu = panoya_modu
        self.yazarak = yazarak
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
        """Metni imlecin olduğu alana bırakır: pano + yapıştır kısayolu (Türkçe için en
        güvenilir yol; Mac'te Cmd+V, diğerlerinde Ctrl+V). Eski pano içeriği geri konur.
        --panoya modunda yalnız kopyalar."""
        import pyperclip
        from pynput.keyboard import Controller, Key

        if self.panoya_modu:
            pyperclip.copy(metin)
            kisayol = "Cmd+V" if MAC else "Ctrl+V"
            print(f"(panoya kopyalandı, {kisayol} ile yapıştır)\n")
            return

        if self.yazarak:
            # whisper-writer/foges yöntemi: karakter karakter yazar, panoya hiç dokunmaz.
            # Bazı uygulamalar özel karakterlerde huysuzdur; sorun görürsen varsayılan
            # (yapıştırma) yöntemine dön.
            Controller().type(metin + " ")
            return

        eski = None
        try:
            eski = pyperclip.paste()
        except Exception:
            pass
        pyperclip.copy(metin)
        time.sleep(0.15)  # pano oturmadan yapıştırılırsa eski içerik gidiyor

        klavye = Controller()
        duzenleyici = Key.cmd if MAC else Key.ctrl
        with klavye.pressed(duzenleyici):
            klavye.press("v")
            klavye.release("v")

        if eski is not None:
            time.sleep(0.35)
            try:
                pyperclip.copy(eski)
            except Exception:
                pass


def kisayol_bicimle(tus: str) -> str:
    """'f8' → '<f8>' · tek karakter ('j') olduğu gibi kalır."""
    tus = tus.strip().lower()
    return tus if len(tus) == 1 else f"<{tus}>"


def tus_cozumle(tus: str):
    """'f8' → Key.f8 · 'j' → KeyCode('j') (basılı-tut modu için)."""
    from pynput.keyboard import Key, KeyCode

    tus = tus.strip().lower()
    if len(tus) == 1:
        return KeyCode.from_char(tus)
    try:
        return getattr(Key, tus)
    except AttributeError:
        raise SystemExit(f"bilinmeyen tuş: {tus} (örnek: f8, f9, pause)")


def main() -> None:
    p = argparse.ArgumentParser(description="Her uygulamada Türkçe dikte (bas-konuş-yapışsın).")
    p.add_argument("--model", default="small", help="whisper modeli: small (varsayılan) / medium")
    p.add_argument("--tus", default="f8", help="kayıt kısayolu (varsayılan: f8)")
    p.add_argument("--basili", action="store_true", help="tuşu basılı tut, konuş, bırak (Wispr akışı)")
    p.add_argument("--yazarak", action="store_true", help="yapıştırma yerine karakter karakter yaz")
    p.add_argument("--panoya", action="store_true", help="imlece yazma, yalnız panoya kopyala")
    args = p.parse_args()

    from pynput import keyboard as pk
    from faster_whisper import WhisperModel

    print(f"model yükleniyor: {args.model} (ilk çalıştırmada indirilir)")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    d = Dikte(model, args.panoya, args.yazarak)

    if args.basili:
        # basılı-tut modu: tuş inince kayıt başlar (oto-tekrar kayitta bayrağıyla süzülür),
        # tuş kalkınca durur ve çevirir. Esc çıkar.
        hedef = tus_cozumle(args.tus)

        def inince(k):
            if k == hedef and not d.kayitta:
                d.baslat_durdur()

        def kalkinca(k):
            if k == hedef and d.kayitta:
                d.baslat_durdur()
            if k == pk.Key.esc:
                return False

        print(f"hazır. istediğin uygulamaya geç → {args.tus.upper()} BASILI TUT, konuş, bırak · Esc: çık\n")
        with pk.Listener(on_press=inince, on_release=kalkinca) as dinleyici:
            dinleyici.join()
    else:
        dinleyici = pk.GlobalHotKeys({
            kisayol_bicimle(args.tus): d.baslat_durdur,
            "<esc>": lambda: dinleyici.stop(),
        })
        print(f"hazır. istediğin uygulamaya geç → {args.tus.upper()}: kayıt başlat/durdur · Esc: çık\n")
        dinleyici.start()
        dinleyici.join()
    print("çıkıldı.")


if __name__ == "__main__":
    main()
