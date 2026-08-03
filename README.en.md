# sesten-yaziya (speech-to-text, Turkish-first)

Speak, get Turkish text. Transcribes audio files and your microphone into Turkish, with per-word
timestamps and ready-to-use subtitle files. Everything runs on your own machine: no audio leaves
your computer, no subscription.

I originally built this for myself: every subtitle on my videos has come out of this system for
months. Generic English-first models turn Turkish audio into soup; this ships with the model and
settings that actually work for Turkish.

## Install

```bash
git clone https://github.com/muhammedsevimli/sesten-yaziya
cd sesten-yaziya
pip install -r requirements.txt
```

Python 3.10+, no GPU required. The model downloads once on first run (small ≈ 500 MB), fully
offline after that.

## Use

Try the bundled sample right away:

```bash
python sesyaz.py ornek/ornek-ses.mp3
```

Transcribe your own file or a folder:

```bash
python sesyaz.py recording.mp3
python sesyaz.py recordings/
```

Microphone dictation (Enter to start/stop):

```bash
python mikrofon.py
```

## Output

Written to `cikti/`:

| File | What it is |
|---|---|
| `<name>.txt` | plain text |
| `<name>.srt` | subtitles built from word timings; drops straight into CapCut/Premiere/YouTube |
| `<name>.kelimeler.json` | per-word start/end times, for building your own tooling |

## Honest notes

- Default model is `small`: fast, good enough for most recordings. If it stumbles, try
  `--model medium` (bigger download, slower, noticeably more accurate).
- Punctuation is decent, not perfect.
- No speaker diarization, no system-wide live dictation integration. That polish is what the
  paid tools actually charge for; this repo gives you the core for free.

## Do whatever you want

MIT licensed. Use it, modify it, productize it, deploy it for clients, sell it as a service.
No permission needed.

PRs welcome; let's grow it together.

---

Decisions and build prompts for 38 SaaS tools ("can you build it yourself?"):
[muhammedsevimli.com/saas-promptlari](https://muhammedsevimli.com/saas-promptlari)

Independent project; no affiliation with or endorsement by any brand mentioned. Built together
with Claude and Codex.
