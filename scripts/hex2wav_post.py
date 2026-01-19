"""
PlatformIO post-build hook to convert firmware.hex -> firmware.wav for TinyAudioBoot / 8BitMixtape.
Place this file at: scripts/hex2wav_post.py

Configure hex2wav_cmd in platformio.ini, e.g.:
  hex2wav_cmd = /home/dusjagr/.arduino15/packages/8BitMixtape/hardware/avr/0.0.28/tools/hex2wav/linux/hex2wav {hex} {wav}
or:
  hex2wav_cmd = node /path/to/hex2wav.js --in {hex} --out {wav}
  hex2wav_cmd = python3 /path/to/hex2wav.py -i {hex} -o {wav}
  hex2wav_cmd = java -jar /path/to/TinyAudioBoot.jar -i {hex} -o {wav}
"""

import os
import shlex
import subprocess
from SCons.Script import Import

Import("env")  # provided by PlatformIO


def _log(msg: str) -> None:
    print("[hex2wav] " + msg)


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
        v = env.GetProjectOption(f"custom_{name}")
        if v is None:
            v = env.GetProjectOption(name, default)
        return v

    hex2wav_cmd = (_getopt("hex2wav_cmd", "") or "").strip()
    auto_play_opt = (_getopt("hex2wav_auto_play", "no") or "no").strip().lower()
    auto_play = auto_play_opt in ("1", "yes", "true", "on")
    player_cmd = _getopt("hex2wav_player_cmd", "aplay -q {wav}")

    if not hex2wav_cmd:
        _log("No 'hex2wav_cmd' configured in platformio.ini -> skipping WAV generation.")
        _log(f"HEX: {hex_path}")
        _log("Set e.g.: hex2wav_cmd = /path/to/hex2wav {hex} {wav}")
        return

    # Expand placeholders and split to argv safely
    fmt_cmd = hex2wav_cmd.format(hex=hex_path, wav=wav_path)
    cmd_list = shlex.split(fmt_cmd)

    rc = _run_cmd(cmd_list)
    if rc != 0 or not os.path.exists(wav_path):
        _log(f"Failed to create WAV at {wav_path}")
        return

    _log(f"WAV created: {wav_path}")

    if auto_play:
        fmt_player = player_cmd.format(hex=hex_path, wav=wav_path)
        play_list = shlex.split(fmt_player)
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

    # Read options from platformio.ini
    hex2wav_cmd = env.GetProjectOption("hex2wav_cmd", default="").strip()
    auto_play = env.GetProjectOption("hex2wav_auto_play", default="no").strip().lower() in ("1", "yes", "true", "on")
    player_cmd = env.GetProjectOption("hex2wav_player_cmd", default="aplay -q {wav}")

    if not hex2wav_cmd:
        _log("No 'hex2wav_cmd' configured in platformio.ini -> skipping WAV generation.")
        _log(f"HEX: {hex_path}")
        return 0

    fmt_cmd = hex2wav_cmd.format(hex=hex_path, wav=wav_path)
    cmd_list = shlex.split(fmt_cmd)
    _log("[alias] Running: " + " ".join(cmd_list))
    rc = _run_cmd(cmd_list)
    if rc != 0:
        _log(f"[alias] hex2wav failed with code {rc}")
        return rc

    if auto_play:
        fmt_player = player_cmd.format(hex=hex_path, wav=wav_path)
        play_list = shlex.split(fmt_player)
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
