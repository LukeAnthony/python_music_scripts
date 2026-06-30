# Python Ear Trainer (GUI)

A desktop ear-training app. A random pitch, interval, or chord is synthesized
and played, and you identify it through a Tkinter interface. It's a GUI front
end over the original command-line trainer: the music-theory generation and the
fluidsynth audio playback are reused unchanged, with the `input()`/`print()`
prompts replaced by widgets.

## Four games

- **Guess Random Note** – a single pitch is played; name it.
- **Guess Random Interval** – two notes are played; identify both notes and the interval.
- **Guess Random Chord** – a chord is played; identify the root, the chord type, or both.
- **Guess Missing Chord Tone** – a chord plays, then plays again with one note removed; name the missing note.

## Files

| File | Purpose |
| --- | --- |
| `ear_trainer_gui.py` | The application. |
| `Dockerfile` | Builds the container image (`ear-trainer`). |
| `play-mac.sh` | Launches the container on macOS (sets up audio + display bridges). |
| `play-windows.ps1` | Launches the container on Windows. |
| `README.md` | This file. |

You supply your own SoundFont (`.sf2`). Free ones are available from
[musical-artifacts.com](https://musical-artifacts.com/) or the FreePats project.

---

## Option A — Run natively (simplest)

No display or audio bridging needed; fluidsynth talks to your OS directly.

**Requirements:** Python 3, `mingus`, a fluidsynth library, and Tkinter.

```bash
pip install mingus
```

- **macOS:** `brew install fluidsynth` (Tkinter ships with the python.org build; if you use a Homebrew Python you may also need `brew install python-tk`).
- **Windows:** the standard python.org installer includes Tkinter; install a fluidsynth build and ensure it's on your `PATH`.
- **Linux:** `sudo apt install fluidsynth python3-tk`.

Run it:

```bash
python3 ear_trainer_gui.py /path/to/soundfont.sf2
```

If you omit the path, a file picker opens so you can choose the `.sf2`.

---

## Option B — Run in Docker

Useful for a consistent, dependency-free environment. The catch: a container has
no screen and no sound card, so two things are forwarded to your host:

- **Audio** → your host PulseAudio server over TCP (port `4713`).
- **Display** → your host X server, so the Tk window can draw.

The wrapper scripts set both up for you. Audio forwarding matches the CLI
version; the display forwarding is the only new piece.

### Build the image

```bash
docker build -t ear-trainer .
```

### macOS

One-time setup:

```bash
brew install pulseaudio
brew install --cask xquartz
```

Open **XQuartz → Settings → Security** and tick **"Allow connections from
network clients"**, then quit and reopen XQuartz.

Then, each time:

```bash
./play-mac.sh /path/to/soundfont.sf2
```

The script starts PulseAudio, loads its TCP module, starts XQuartz, authorizes
the local connection with `xhost`, runs the container, and cleans up the
PulseAudio module and `xhost` grant on exit.

### Windows

One-time setup:

- Install a PulseAudio build for Windows and enable TCP in its `default.pa`:
  `load-module module-native-protocol-tcp port=4713 auth-ip-acl=127.0.0.1`
- Install **VcXsrv**.
- Edit the `$PulseExe` and `$VcXsrvExe` paths near the top of `play-windows.ps1`
  to match your installs.

Then, each time:

```powershell
.\play-windows.ps1 -SoundFont C:\path\to\soundfont.sf2
```

### How the run command works

Both scripts ultimately run something like:

```bash
docker run --rm -it \
  -e DISPLAY=host.docker.internal:0 \
  -e PULSE_SERVER=tcp:host.docker.internal:4713 \
  -v /path/to/soundfont.sf2:/sf.sf2:ro \
  ear-trainer /sf.sf2
```

`DISPLAY` points the container at the host X server; `PULSE_SERVER` points
fluidsynth at the host audio server. The image sets
`EAR_TRAINER_AUDIO_DRIVER=pulseaudio` so fluidsynth uses the PulseAudio driver
inside the container. On native host runs that variable is unset and fluidsynth
picks the platform default (coreaudio on macOS, etc.).

---

## Using the app

1. On the **Settings** screen, pick a game, the notes and octaves to draw from,
   and any game-specific options (interval/chord types, what to guess,
   inversions). Click **Start**.
2. Click **Play** to hear the question (**Replay** to repeat it).
3. Make your guess with the note buttons and dropdowns, then **Submit** for
   per-component feedback.
4. Click **Next** for a new question. Running stats show at the bottom;
   **Settings** returns you to reconfigure.

---

## Troubleshooting

- **No window appears (Docker):** the X server isn't reachable. On macOS confirm
  XQuartz has "Allow connections from network clients" enabled and that
  `xhost + 127.0.0.1` ran. On Windows confirm VcXsrv is running with access
  control disabled.
- **No sound (Docker):** confirm PulseAudio is running on the host with the TCP
  module loaded on port 4713, and that `PULSE_SERVER` is set in the run command.
- **macOS native, "couldn't find libfluidsynth":** Homebrew's library path may
  not be visible to the system Python's ctypes loader. Point it at the Homebrew
  lib directory, e.g.
  `export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib:$DYLD_FALLBACK_LIBRARY_PATH"`
  before running.
- **"A soundfont file is required":** pass a valid `.sf2` path, or pick one in
  the dialog.

---

## Notes on the code

- The chord game reports the exact chord type you selected (rather than relying
  on `chords.determine`), so inverted voicings are still scored against the name
  you can actually pick.
- Interval scoring covers the tritone in both spellings (`minor fifth` /
  `augmented fourth`) and maps the perfect fifth correctly.
- One known issue is left as-is: `updateStats` rounds the percentage before
  multiplying by 100, so the displayed percent can show float artifacts
  (e.g. `66.99999999999999%`). Reorder to `round(ratio * 100, 2)` if you want to
  fix it.
