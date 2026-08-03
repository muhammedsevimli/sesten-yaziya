"""sesten-yaziya · ses dosyasını Türkçe yazıya çevirir.

Kullanım:
    python sesyaz.py ses.mp3
    python sesyaz.py kayitlar/            (klasördeki tüm sesler)
    python sesyaz.py ses.mp3 --format srt
    python sesyaz.py ses.mp3 --model medium

Çıktılar (varsayılan üçü birden, cikti/ klasörüne):
    <ad>.txt             düz metin
    <ad>.srt             altyazı (satırlar kelime zamanlarından kurulur)
    <ad>.kelimeler.json  kelime kelime zaman damgası
"""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SES_UZANTILARI = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".flac", ".webm", ".aac", ".wma"}

# Altyazı satırı kuralları: okunabilirlik için kısa tut.
SRT_MAKS_KELIME = 7
SRT_MAKS_SANIYE = 4.0


def zaman_srt(saniye: float) -> str:
    ms = max(0, int(round(saniye * 1000)))
    s, ms = divmod(ms, 1000)
    dk, s = divmod(s, 60)
    saat, dk = divmod(dk, 60)
    return f"{saat:02d}:{dk:02d}:{s:02d},{ms:03d}"


def kelimelerden_srt(kelimeler: list) -> str:
    """Kelime zamanlarından altyazı satırları kurar. Uzun boşluklarda ve
    satır dolunca böler; böylece altyazı konuşmayla birebir akar."""
    bloklar = []
    satir = []
    for k in kelimeler:
        if satir:
            dolu = len(satir) >= SRT_MAKS_KELIME
            uzun = k["bas"] - satir[0]["bas"] >= SRT_MAKS_SANIYE
            ara = k["bas"] - satir[-1]["son"] >= 1.0  # konuşma arası: yeni satır
            if dolu or uzun or ara:
                bloklar.append(satir)
                satir = []
        satir.append(k)
    if satir:
        bloklar.append(satir)

    parcalar = []
    for i, blok in enumerate(bloklar, 1):
        metin = " ".join(k["kelime"] for k in blok)
        parcalar.append(f"{i}\n{zaman_srt(blok[0]['bas'])} --> {zaman_srt(blok[-1]['son'])}\n{metin}\n")
    return "\n".join(parcalar)


def model_yukle(model_adi: str):
    from faster_whisper import WhisperModel

    print(f"model yükleniyor: {model_adi} (ilk çalıştırmada indirilir, sonrası yerelden)")
    # int8: sıradan bir dizüstünde bile rahat çalışsın diye. GPU şart değil.
    return WhisperModel(model_adi, device="cpu", compute_type="int8")


def cevir(model, ses_yolu: Path):
    """Tek dosyayı çevirir; (metin, kelimeler) döner."""
    # language="tr" sabit: otomatik dil tespiti kısa/gürültülü seste yanılıp
    # İngilizce'ye kayabiliyor, bütün proje bu hatayı yaşamamak için var.
    segmentler, bilgi = model.transcribe(
        str(ses_yolu),
        language="tr",
        word_timestamps=True,
        vad_filter=True,
        beam_size=5,
    )
    kelimeler = []
    metin_parcalari = []
    for seg in segmentler:
        metin_parcalari.append(seg.text.strip())
        for k in seg.words or []:
            kelimeler.append({"kelime": k.word.strip(), "bas": round(k.start, 3), "son": round(k.end, 3)})
    return " ".join(p for p in metin_parcalari if p), kelimeler


def dosyayi_isle(model, ses_yolu: Path, cikti_klasoru: Path, biçimler: set) -> None:
    print(f"\nçevriliyor: {ses_yolu.name}")
    metin, kelimeler = cevir(model, ses_yolu)
    if not metin:
        print("  ses bulunamadı ya da konuşma yok, atlandı")
        return

    cikti_klasoru.mkdir(parents=True, exist_ok=True)
    kok = cikti_klasoru / ses_yolu.stem

    if "txt" in biçimler:
        (kok.parent / f"{kok.name}.txt").write_text(metin + "\n", encoding="utf-8")
        print(f"  yazıldı: {kok.name}.txt ({len(metin.split())} kelime)")
    if "srt" in biçimler and kelimeler:
        (kok.parent / f"{kok.name}.srt").write_text(kelimelerden_srt(kelimeler), encoding="utf-8")
        print(f"  yazıldı: {kok.name}.srt")
    if "json" in biçimler and kelimeler:
        (kok.parent / f"{kok.name}.kelimeler.json").write_text(
            json.dumps(kelimeler, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"  yazıldı: {kok.name}.kelimeler.json")


def main() -> None:
    p = argparse.ArgumentParser(description="Ses dosyasını Türkçe yazıya çevirir.")
    p.add_argument("girdi", nargs="+", help="ses dosyası/dosyaları ya da klasör")
    p.add_argument("--model", default="small", help="whisper modeli: small (varsayılan) / medium / large-v3")
    p.add_argument("--cikti", default="cikti", help="çıktı klasörü (varsayılan: cikti)")
    p.add_argument("--format", default="hepsi", choices=["hepsi", "txt", "srt", "json"])
    args = p.parse_args()

    dosyalar = []
    for g in args.girdi:
        yol = Path(g)
        if yol.is_dir():
            dosyalar += sorted(x for x in yol.iterdir() if x.suffix.lower() in SES_UZANTILARI)
        elif yol.is_file():
            dosyalar.append(yol)
        else:
            print(f"bulunamadı: {g}")
    if not dosyalar:
        sys.exit("çevrilecek ses dosyası yok")

    biçimler = {"txt", "srt", "json"} if args.format == "hepsi" else {args.format}
    model = model_yukle(args.model)
    for d in dosyalar:
        dosyayi_isle(model, d, Path(args.cikti), biçimler)
    print("\nbitti.")


if __name__ == "__main__":
    main()
