# Music Segmenter

A simple desktop app for splitting audio files by timestamps with track names.  
Built with Python and PyQt6.

---

## Requirements

- Python 3.14.3
- [ffmpeg](https://ffmpeg.org/download.html) installed and available in `PATH`

## Installation

```bash
git clone https://github.com/belzEnn/music-segmenter.git
cd audio-splitter
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

---

## Usage

1. **Choose Audio** — select your input audio file (`.mp3`, `.wav`, `.ogg`)
2. **Choose Output Folder** — select where the split tracks will be saved
3. **Enter timestamps** in the text area using this format:

```
00:00 Track One
03:18 Track Two
05:30 Track Three
09:07 Track Four
```

- Timestamps support both `mm:ss` and `hh:mm:ss`
- The track name becomes the output filename — e.g. `Track One.mp3`
- The last track is cut from its timestamp to the end of the file
- Characters forbidden in filenames (`/ \ : * ? " < > |`) are replaced with `_`

4. Click **Split Audio**

---

## Dependencies

| Package      | Version |
|--------------|---------|
| PyQt6        | 6.11.0  |
| PyQt6-Qt6    | 6.11.0  |
| PyQt6_sip    | 13.11.1 |

> ffmpeg is **not** a Python package and must be installed separately on your system.

### Installing ffmpeg

**Windows** — via [winget](https://winget.run/):
```bash
winget install ffmpeg
```
Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to `PATH` manually.

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt install ffmpeg # Debian/Ubuntu
sudo dnf install ffmpeg # Fedora
sudo pacman -S ffmpeg # Arch
```