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

Works on Windows, macOS and Linux. Python 3.10+, no GPU required. The model downloads once on
first run (small ≈ 500 MB), fully offline after that.

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

Dictation in any app (the Wispr Flow-style flow): stay wherever you are — chat, email, docs.
Press F8, speak, press F8 again; the text is typed right where your cursor is:

```bash
python dikte.py
```

Prefer staying in the terminal? Simple mic mode (Enter to start/stop, text to screen + clipboard):

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
- Dictation types after you stop recording (transcription takes a moment), not while you speak.
  No streaming, no tray icon, no polished UI; that polish is what the paid tools charge for.
- No speaker diarization.
- `dikte.py` permissions: nothing needed on Windows. On macOS the first run asks for microphone
  access + ticking Terminal under System Settings → Privacy & Security → Accessibility (once,
  no sudo; pasting uses Cmd+V automatically). On Linux it works under X11; if your Wayland
  desktop restricts global hotkeys, use `--panoya` (clipboard-only) mode.

## Do whatever you want

MIT licensed. Use it, modify it, productize it, deploy it for clients, sell it as a service.
No permission needed.

PRs welcome; let's grow it together.

---

Decisions and build prompts for 38 SaaS tools ("can you build it yourself?"):
[muhammedsevimli.com/saas-promptlari](https://muhammedsevimli.com/saas-promptlari)

Independent project; no affiliation with or endorsement by any brand mentioned. Built together
with Claude and Codex.
