# sesten-yaziya

Konuş, Türkçe yazsın. Ses dosyalarını ve mikrofonu Türkçe metne çevirir; kelime kelime zaman
damgası verir, altyazı dosyasını hazır çıkarır. Her şey kendi bilgisayarında çalışır, ses hiçbir
sunucuya gitmez, abonelik yok.

Bunu kendim için kurmuştum: bütün videolarımın altyazısı aylardır bu sistemden çıkıyor. İngilizce
modeller Türkçe sesi çorbaya çeviriyordu, doğru model ve doğru ayarlarla uğraşıp çözdüm. O
dertlerin hepsi burada çözülmüş halde geliyor.

## Kurulum

```bash
git clone https://github.com/muhammedsevimli/sesten-yaziya
cd sesten-yaziya
pip install -r requirements.txt
```

Windows, macOS ve Linux'ta çalışır. Python 3.10+ yeterli, GPU şart değil. Model ilk çalıştırmada
bir kere iner (small ≈ 500 MB), sonrası tamamen çevrimdışı.

## Kullanım

Örnek sesle hemen dene (repoda hazır):

```bash
python sesyaz.py ornek/ornek-ses.mp3
```

Kendi dosyanı ya da klasörünü çevir:

```bash
python sesyaz.py kayit.mp3
python sesyaz.py kayitlar/
```

Her uygulamada dikte (Wispr Flow akışı): WhatsApp'ta, mailde, dokümanda, neredeysen orada kal.
F8'e bas, konuş, tekrar F8; metin imlecin olduğu yere kendiliğinden yazılır:

```bash
python dikte.py
```

Terminalde kalmak istersen basit mikrofon modu da var (Enter: başlat/durdur, metin ekrana + panoya):

```bash
python mikrofon.py
```

## Çıktılar

`cikti/` klasörüne üçü birden yazılır:

| Dosya | Ne işe yarar |
|---|---|
| `<ad>.txt` | düz metin |
| `<ad>.srt` | altyazı; satırlar kelime zamanlarından kurulur, CapCut/Premiere/YouTube'a direkt atılır |
| `<ad>.kelimeler.json` | kelime kelime başlangıç/bitiş süreleri (kendi sistemini kuracaklara) |

## Dürüst notlar

- Varsayılan model `small`: hızlı, çoğu kayıtta yeterli. Zor kayıtta kelime hatası yaparsa
  `--model medium` dene, belirgin daha isabetli (indirmesi daha büyük, çevirmesi daha yavaş).
- Noktalama mükemmel değil; uzun metinlerde elden bir geçirmek gerekebilir.
- Dikte modu konuşurken değil, kaydı durdurunca yazar (çeviri kısa bir an sürer). Anlık akış,
  tepsi simgesi, cilalı arayüz yok; paralı araçların parası o cilaya gidiyor, iş burada.
- Konuşmacı ayrımı yok.
- `dikte.py` izinleri: Windows'ta hiçbir şey gerekmez. macOS ilk çalıştırmada mikrofon izni +
  Sistem Ayarları → Gizlilik ve Güvenlik → Erişilebilirlik'te Terminal'i işaretlemeni ister
  (bir kere, sudo gerekmez; Mac'te yapıştırma otomatik Cmd+V ile yapılır). Linux X11'de çalışır,
  Wayland'da global kısayol kısıtlıysa `--panoya` modunu kullan.
- Beğenmediysen ya da kendine göre kurmak istersen bu sistemin prompt'u da açık:
  [muhammedsevimli.com/saas-promptlari/wispr-flow](https://muhammedsevimli.com/saas-promptlari/wispr-flow)

## İstediğini yap

Lisans MIT. Kendine kur, değiştir, ürünleştir, müşterine kur, hizmet olarak sat. İzin istemene
gerek yok.

Geliştirmek istersen PR gönder, birlikte büyütelim. Issue da açabilirsin.

---

38 SaaS aracının "kendin kurabilir misin" kararları ve kurulum promptları:
[muhammedsevimli.com/saas-promptlari](https://muhammedsevimli.com/saas-promptlari)

Bu proje bağımsızdır; adı geçen hiçbir markayla bağlantısı, sponsorluğu yoktur. Claude ve Codex
ile birlikte kuruldu. · English: [README.en.md](README.en.md)
