# play-windows.ps1 - launch the Ear Trainer GUI in Docker on Windows.
#
# Bridges two things from the container to your Windows host:
#   1. Audio   -> host PulseAudio server over TCP (port 4713)
#   2. Display -> host X server (VcXsrv), display :0
#
# Usage:
#   .\play-windows.ps1 -SoundFont C:\path\to\soundfont.sf2
#
# One-time setup before this works:
#   - Install PulseAudio for Windows (e.g. pulseaudio.exe) and adjust $PulseExe below.
#     Its config must enable TCP, for example in etc\pulse\default.pa:
#       load-module module-native-protocol-tcp port=4713 auth-ip-acl=127.0.0.1
#   - Install VcXsrv and adjust $VcXsrvExe below. Launch it once via XLaunch with
#     "Disable access control" checked, or let this script start it that way.

param(
    [Parameter(Mandatory = $true)]
    [string]$SoundFont
)

$ErrorActionPreference = "Stop"

$Image     = "ear-trainer"
$PulsePort = 4713
# Adjust these paths to match your installs:
$PulseExe  = "C:\pulseaudio\bin\pulseaudio.exe"
$VcXsrvExe = "C:\Program Files\VcXsrv\vcxsrv.exe"

if (-not (Test-Path $SoundFont)) {
    Write-Error "Soundfont not found: $SoundFont"
    exit 1
}
$SoundFont = (Resolve-Path $SoundFont).Path

# --- 1. Audio: ensure PulseAudio is running ---------------------------------
if (-not (Get-Process -Name "pulseaudio" -ErrorAction SilentlyContinue)) {
    if (Test-Path $PulseExe) {
        Write-Host "Starting PulseAudio..."
        Start-Process -FilePath $PulseExe -ArgumentList "--exit-idle-time=-1" -WindowStyle Hidden
        Start-Sleep -Seconds 2
    } else {
        Write-Warning "PulseAudio not found at $PulseExe - start it manually (TCP port $PulsePort)."
    }
}

# --- 2. Display: ensure an X server (VcXsrv) is running ----------------------
if (-not (Get-Process -Name "vcxsrv" -ErrorAction SilentlyContinue)) {
    if (Test-Path $VcXsrvExe) {
        Write-Host "Starting VcXsrv..."
        # :0  -> display 0
        # -ac -> disable access control (allow the container to connect)
        Start-Process -FilePath $VcXsrvExe -ArgumentList ":0 -multiwindow -ac -clipboard"
        Start-Sleep -Seconds 2
    } else {
        Write-Warning "VcXsrv not found at $VcXsrvExe - start your X server manually."
    }
}

# --- 3. Run the container ----------------------------------------------------
docker run --rm -it `
    -e DISPLAY=host.docker.internal:0 `
    -e PULSE_SERVER="tcp:host.docker.internal:$PulsePort" `
    -v "${SoundFont}:/sf.sf2:ro" `
    $Image /sf.sf2
