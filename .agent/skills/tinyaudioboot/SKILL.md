---
name: tinyaudioboot
description: TinyAudioBoot firmware upload workflow using WAV audio files instead of traditional ISP programming. Covers hex2wav conversion, PlatformIO integration, and troubleshooting.
---

# TinyAudioBoot Firmware Upload

This skill teaches you how to upload firmware to ATtiny85 using the TinyAudioBoot bootloader, which uses audio signals (WAV files) instead of traditional USB/ISP programming.

## How It Works

```
┌──────────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│ Source Code  │───▶│ firmware.hex │───▶│ firmware.wav  │───▶│ ATtiny85   │
│ (.cpp)       │    │ (Intel HEX)  │    │ (Audio File)  │    │ via audio  │
└──────────────┘    └──────────────┘    └───────────────┘    └────────────┘
     PlatformIO         hex2wav           Audio playback       Bootloader
      compile          converter            (speakers)          decodes
```

## Build Process

### Standard Build (Generates WAV)
```bash
pio run
# Output:
# .pio/build/attiny85/firmware.hex  (Intel HEX file)
# .pio/build/attiny85/firmware.wav  (Audio upload file)
```

### Build and Play (Requires Audio Hardware)
```bash
pio run --target upload
# Builds, converts to WAV, and plays via audio system
```

### Clean Build
```bash
pio run --target clean
```

## PlatformIO Configuration

### [`platformio.ini`](../../../platformio.ini) Key Settings

```ini
[env:attiny85]
platform = atmelavr
board = attiny85
framework = arduino
board_build.f_cpu = 16000000L

; Post-build script for hex2wav conversion
extra_scripts = scripts/hex2wav_post.py

; hex2wav command (OS-specific)
custom_hex2wav_cmd = tools/hex2wav/linux/hex2wav64_bin {hex} {wav}

; Auto-play after build
custom_hex2wav_auto_play = yes
custom_hex2wav_player_cmd = aplay -q {wav}

; Custom upload protocol
upload_protocol = custom
upload_command = tools/hex2wav/linux/hex2wav64_bin $SOURCE .pio/build/${PIOENV}/${PROGNAME}.wav && aplay -q .pio/build/${PIOENV}/${PROGNAME}.wav
```

### OS-Specific hex2wav Commands

| OS | Command |
|----|---------|
| Linux 64-bit | `tools/hex2wav/linux/hex2wav64_bin {hex} {wav}` |
| Linux 32-bit | `tools/hex2wav/linux/hex2wav32_bin {hex} {wav}` |
| macOS | `tools/hex2wav/macosx/hex2wav {hex} {wav}` |
| Windows | `tools/hex2wav/windows/hex2wav.exe {hex} {wav}` |
| Java (any OS) | `java -jar tools/hex2wav/hex2wav.jar -i {hex} -o {wav}` |

### OS-Specific Player Commands

| OS | Command |
|----|---------|
| Linux (ALSA) | `aplay -q {wav}` |
| Linux (PulseAudio) | `paplay {wav}` |
| macOS | `afplay {wav}` |
| Windows | `start /wait "" {wav}` |

## Post-Build Script

The [`scripts/hex2wav_post.py`](../../../scripts/hex2wav_post.py) script:
1. Runs after successful compilation
2. Invokes hex2wav converter with correct paths
3. Optionally plays the WAV file
4. Reports conversion status

## hex2wav Tool Locations

```
tools/hex2wav/
├── hex2wav.jar           # Java version (cross-platform)
├── linux/
│   ├── hex2wav           # Script wrapper
│   ├── hex2wav32_bin     # 32-bit Linux binary
│   └── hex2wav64_bin     # 64-bit Linux binary
├── macosx/
│   └── hex2wav           # macOS binary
└── windows/
    └── hex2wav.exe       # Windows binary
```

## Upload Procedure

### Prerequisites
1. ATtiny85 must be running TinyAudioBoot bootloader
2. Audio output connected to ATtiny85 input
3. Sufficient volume level (typically 80-100%)
4. Bootloader must be in "listening" mode

### Physical Setup
```
Computer Audio Out ────┬──── GND
                       │
                       └──── ATtiny85 Audio Input Pin
```

### Steps
1. Build the firmware: `pio run`
2. Activate bootloader on ATtiny85 (usually power cycle with button held)
3. Play the WAV file: `pio run --target upload` or play manually
4. Wait for upload to complete (visual indicator on device)

## Troubleshooting

### Upload Fails (No Response)
- **Check volume level**: Must be 80-100%
- **Verify audio connection**: Ensure proper wiring
- **Bootloader active**: Device must be in bootloader mode
- **Try headphone jack**: Some speakers add processing

### Upload Fails (Partial)
- **Reduce volume slightly**: Clipping can corrupt signal
- **Check for interference**: Move away from noise sources
- **Verify HEX file**: Check `.pio/build/attiny85/firmware.hex` exists

### WAV Not Generated
- **Check post-script output**: Look for errors in build log
- **Verify hex2wav binary**: Run manually to test
- **Check permissions**: Binary must be executable

### Wrong OS Binary
```bash
# Check binary architecture
file tools/hex2wav/linux/hex2wav64_bin
# Should match your system

# Make executable if needed
chmod +x tools/hex2wav/linux/hex2wav64_bin
```

## Firmware Size Constraint

**Critical**: Firmware must fit in <8KB (minus bootloader space):

```bash
# Check size after build
# Look for "Flash: XX% used" in build output

# If too large, reduce code:
# - Remove unused features
# - Use PROGMEM for constants
# - Optimize algorithms
```

## Testing Without Hardware

```bash
# Generate WAV without playing
# Edit platformio.ini:
custom_hex2wav_auto_play = no

pio run
# Then manually inspect .pio/build/attiny85/firmware.wav
```

## Custom Upload Options

Using `custom_` prefix avoids PlatformIO warnings:

```ini
; Good (no warnings)
custom_hex2wav_cmd = ...
custom_hex2wav_auto_play = yes

; Bad (triggers warnings)
hex2wav_cmd = ...
```
