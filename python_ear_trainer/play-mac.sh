#!/usr/bin/env bash
#
# play-mac.sh - launch the Ear Trainer GUI in Docker on macOS.
#
# Bridges two things from the container to your Mac:
#   1. Audio  -> host PulseAudio server over TCP (port 4713)
#   2. Display -> host XQuartz X server (TCP port 6000, display :0)
#
# Usage:
#   ./play-mac.sh /path/to/soundfont.sf2
#
# One-time setup before this works:
#   brew install pulseaudio
#   brew install --cask xquartz
#   Open XQuartz -> Settings -> Security -> tick "Allow connections from
#     network clients", then quit and reopen XQuartz (or log out/in).

set -euo pipefail

IMAGE="ear-trainer"
PULSE_PORT=4713

SOUNDFONT="${1:-}"
if [[ -z "$SOUNDFONT" ]]; then
    echo "Usage: $0 /path/to/soundfont.sf2" >&2
    exit 1
fi
if [[ ! -f "$SOUNDFONT" ]]; then
    echo "Soundfont not found: $SOUNDFONT" >&2
    exit 1
fi
SOUNDFONT="$(cd "$(dirname "$SOUNDFONT")" && pwd)/$(basename "$SOUNDFONT")"

# --- 1. Audio: start PulseAudio and load the TCP module ---------------------
if ! pactl info >/dev/null 2>&1; then
    echo "Starting PulseAudio..."
    pulseaudio --start
fi
# Load the TCP module if it isn't already loaded; capture the module index so we
# can unload it again on exit (keeps the host audio config clean).
PULSE_MODULE=""
if ! pactl list short modules | grep -q "module-native-protocol-tcp.*port=$PULSE_PORT"; then
    PULSE_MODULE="$(pactl load-module module-native-protocol-tcp \
        port="$PULSE_PORT" auth-ip-acl=127.0.0.1)"
fi

# --- 2. Display: start XQuartz and allow the local connection ---------------
open -a XQuartz
# give XQuartz a moment to bring up its listener on first launch
sleep 2
export DISPLAY=:0
xhost + 127.0.0.1 >/dev/null

cleanup() {
    [[ -n "$PULSE_MODULE" ]] && pactl unload-module "$PULSE_MODULE" 2>/dev/null || true
    xhost - 127.0.0.1 >/dev/null 2>&1 || true
}
trap cleanup EXIT

# --- 3. Run the container ----------------------------------------------------
docker run --rm -it \
    -e DISPLAY=host.docker.internal:0 \
    -e PULSE_SERVER="tcp:host.docker.internal:$PULSE_PORT" \
    -v "$SOUNDFONT":/sf.sf2:ro \
    "$IMAGE" /sf.sf2
