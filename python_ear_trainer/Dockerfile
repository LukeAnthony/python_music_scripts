# Ear Trainer GUI - container image
#
# Beyond the CLI version's needs, the GUI adds Tkinter and the X11 client
# library so the window can render on the host's X server.

FROM python:3.11-slim

# System dependencies:
#   fluidsynth         - audio synthesis engine; provides libfluidsynth.so, which
#                        mingus locates via ctypes find_library("fluidsynth")
#   libpulse0 /        - PulseAudio client libs so fluidsynth's "pulseaudio" driver
#   pulseaudio-utils     can stream audio to the host PulseAudio server over TCP
#   python3-tk         - Tkinter (the GUI toolkit); omitted from slim images
#   libx11-6           - X11 client library so the Tk window can draw on the host
RUN apt-get update && apt-get install -y --no-install-recommends \
        fluidsynth \
        libpulse0 \
        pulseaudio-utils \
        python3-tk \
        libx11-6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir mingus

COPY ear_trainer_gui.py /app/

# Force the PulseAudio driver inside the container. (Unset on native host runs so
# fluidsynth picks coreaudio/wasapi/alsa instead.)
ENV EAR_TRAINER_AUDIO_DRIVER=pulseaudio

# The soundfont is provided at run time (mounted in), passed as the first argument.
ENTRYPOINT ["python3", "ear_trainer_gui.py"]
