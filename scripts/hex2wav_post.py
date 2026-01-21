"""
PlatformIO post-build hook to convert firmware.hex -> firmware.wav for TinyAudioBoot / 8BitMixtape.
Place this file at: scripts/hex2wav_post.py

Configure hex2wav_cmd in platformio.ini, e.g.:
  custom_hex2wav_cmd = auto  ; auto-detect OS and use bundled hex2wav
  custom_hex2wav_cmd = tools/hex2wav/linux/hex2wav64_bin {hex} {wav}
  custom_hex2wav_cmd = tools/hex2wav/windows/hex2wav.exe {hex} {wav}
  custom_hex2wav_cmd = tools/hex2wav/macosx/hex2wav {hex} {wav}
  custom_hex2wav_cmd = java -jar tools/hex2wav/hex2wav.jar -i {hex} -o {wav}
"""

import os
import platform
import shlex
import subprocess
import sys
from SCons.Script import Import

Import("env")  # provided by PlatformIO

# Project root (where platformio.ini lives)
PROJECT_DIR = env.subst("$PROJECT_DIR")


def _log(msg: str) -> None:
    print("[hex2wav] " + msg)


def _get_auto_hex2wav_config():
    """Auto-detect OS and return (hex2wav_cmd_template, player_cmd_template)."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        hex2wav = "tools/hex2wav/windows/hex2wav.exe {hex} {wav}"
        player = "start /wait {wav}"
    elif system == "darwin":  # macOS
        hex2wav = "tools/hex2wav/macosx/hex2wav {hex} {wav}"
        player = "afplay {wav}"
    else:  # Linux and others
        # Detect 32-bit vs 64-bit
        if "64" in machine or machine in ("x86_64", "amd64", "aarch64"):
            hex2wav = "tools/hex2wav/linux/hex2wav64_bin {hex} {wav}"
        else:
            hex2wav = "tools/hex2wav/linux/hex2wav32_bin {hex} {wav}"
        player = "aplay -q {wav}"
    
    _log(f"Auto-detected OS: {system} ({machine}) -> {hex2wav.split()[0]}")
    return hex2wav, player


def _run_cmd(cmd_list, cwd=None) -> int:
    try:
        _log("Running: " + " ".join(cmd_list))
        res = subprocess.run(cmd_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(res.stdout)
        return res.returncode
    except FileNotFoundError:
        _log(f"Command not found: {cmd_list[0]}")
        return 127


def post_action_hex_to_wav(target, source, env):
    # Source is the built .hex
    t0 = str(target[0]) if target else ""
    s0 = str(source[0]) if source else ""
    # In normal post-action, target is the .hex; in our custom alias, source is the .hex
    if t0.lower().endswith('.hex'):
        hex_path = t0
    else:
        hex_path = s0
    build_dir = os.path.dirname(hex_path)
    progname = env.get("PROGNAME", "firmware")

    wav_name = f"{progname}.wav"
    wav_path = os.path.join(build_dir, wav_name)

    # Read options from platformio.ini (prefer custom_ names to avoid warnings, fallback to legacy)
    def _getopt(name, default):
        # Try custom_ prefixed option first, then legacy name
        v = env.GetProjectOption(f"custom_{name}", default=None)
        if v is None:
            v = env.GetProjectOption(name, default=default)
        return v

    hex2wav_cmd = (_getopt("hex2wav_cmd", "") or "").strip()
    auto_play_opt = (_getopt("hex2wav_auto_play", "no") or "no").strip().lower()
    auto_play = auto_play_opt in ("1", "yes", "true", "on")
    player_cmd = (_getopt("hex2wav_player_cmd", "") or "").strip()

    # Auto-detect hex2wav binary and player if "auto" or not specified
    if not hex2wav_cmd or hex2wav_cmd.lower() == "auto":
        hex2wav_cmd, auto_player = _get_auto_hex2wav_config()
        if not player_cmd:
            player_cmd = auto_player
    elif not player_cmd:
        # Default player based on OS
        _, player_cmd = _get_auto_hex2wav_config()

    # Expand placeholders and split to argv safely
    # Use posix=False on Windows to preserve backslash paths
    fmt_cmd = hex2wav_cmd.format(hex=hex_path, wav=wav_path)
    cmd_list = shlex.split(fmt_cmd, posix=(sys.platform != 'win32'))

    rc = _run_cmd(cmd_list)
    if rc != 0 or not os.path.exists(wav_path):
        _log(f"Failed to create WAV at {wav_path}")
        return

    _log(f"WAV created: {wav_path}")

    if auto_play:
        fmt_player = player_cmd.format(hex=hex_path, wav=wav_path)
        play_list = shlex.split(fmt_player, posix=(sys.platform != 'win32'))
        _log("Auto-playing WAV...")
        _run_cmd(play_list)


# Register the post-build action immediately when this script is imported
env.AddPostAction("$BUILD_DIR/${PROGNAME}.hex", post_action_hex_to_wav)

def run_hex2wav_alias(target, source, env):
    """Force hex->wav conversion and optional playback on demand.

    This is used by the custom target:
        pio run -t wav
    and runs regardless of whether the HEX was rebuilt.
    """
    # Resolve paths based on current env
    hex_path = env.subst("$BUILD_DIR/${PROGNAME}.hex")
    wav_path = env.subst("$BUILD_DIR/${PROGNAME}.wav")

    # Read options from platformio.ini (prefer custom_ prefixed options)
    def _getopt(name, default):
        # Try custom_ prefixed option first, then legacy name
        v = env.GetProjectOption(f"custom_{name}", default=None)
        if v is None:
            v = env.GetProjectOption(name, default=default)
        return v

    hex2wav_cmd = (_getopt("hex2wav_cmd", "") or "").strip()
    auto_play = (_getopt("hex2wav_auto_play", "no") or "no").strip().lower() in ("1", "yes", "true", "on")
    player_cmd = (_getopt("hex2wav_player_cmd", "") or "").strip()

    # Auto-detect hex2wav binary and player if "auto" or not specified
    if not hex2wav_cmd or hex2wav_cmd.lower() == "auto":
        hex2wav_cmd, auto_player = _get_auto_hex2wav_config()
        if not player_cmd:
            player_cmd = auto_player
    elif not player_cmd:
        _, player_cmd = _get_auto_hex2wav_config()

    fmt_cmd = hex2wav_cmd.format(hex=hex_path, wav=wav_path)
    cmd_list = shlex.split(fmt_cmd, posix=(sys.platform != 'win32'))
    _log("[alias] Running: " + " ".join(cmd_list))
    rc = _run_cmd(cmd_list)
    if rc != 0:
        _log(f"[alias] hex2wav failed with code {rc}")
        return rc

    if auto_play:
        fmt_player = player_cmd.format(hex=hex_path, wav=wav_path)
        play_list = shlex.split(fmt_player, posix=(sys.platform != 'win32'))
        _log("[alias] Auto-playing WAV...")
        _run_cmd(play_list)
    return 0


# Provide a custom target that always regenerates/plays on demand without depending on a rebuild
try:
    from SCons.Script import AlwaysBuild
    alias = env.Alias("wav", [], run_hex2wav_alias)
    AlwaysBuild(alias)
except Exception as e:
    _log(f"Could not create custom target 'wav': {e}")
