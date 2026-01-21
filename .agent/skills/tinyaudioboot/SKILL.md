---
name: tinyaudioboot
description: TinyAudioBoot firmware upload workflow using WAV audio files instead of traditional ISP programming. Covers hex2wav conversion and audio upload troubleshooting.
---

# TinyAudioBoot Firmware Upload

This skill teaches you how to upload firmware to ATtiny85 using the TinyAudioBoot bootloader, which uses audio signals (WAV files) instead of traditional USB/ISP programming.

> **Note**: For PlatformIO CLI issues (e.g., `pio` not found), see the [`platformio`](../platformio/SKILL.md) skill.

## How It Works

```
┌──────────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│ Source Code  │───▶│ firmware.hex │───▶│ firmware.wav  │───▶│ ATtiny85   │
│ (.cpp)       │    │ (Intel HEX)  │    │ (Audio File)  │    │ via audio  │
└──────────────┘    └──────────────┘    └───────────────┘    └────────────┘
     PlatformIO         hex2wav           Audio playback       Bootloader
      compile          converter            (speakers)          decodes
```

## Build Commands

```bash
pio run                    # Build + auto-generate WAV
pio run --target upload    # Build and play WAV (requires audio hardware)
pio run --target clean     # Clean build
```

## hex2wav Configuration

### Auto-Detection (Recommended)

Set in [`platformio.ini`](../../../platformio.ini):
```ini
custom_hex2wav_cmd = auto
custom_hex2wav_auto_play = no
```

The post-build script auto-detects OS and selects the correct hex2wav binary:

| OS | Auto-Selected Binary | Auto-Selected Player |
|----|---------------------|---------------------|
| Windows | `tools/hex2wav/windows/hex2wav.exe` | `start /wait {wav}` |
| macOS | `tools/hex2wav/macosx/hex2wav` | `afplay {wav}` |
| Linux 64-bit | `tools/hex2wav/linux/hex2wav64_bin` | `aplay -q {wav}` |
| Linux 32-bit | `tools/hex2wav/linux/hex2wav32_bin` | `aplay -q {wav}` |

### Manual Override

If auto-detection doesn't work, specify manually:

| OS | Command |
|----|---------|
| Linux 64-bit | `tools/hex2wav/linux/hex2wav64_bin {hex} {wav}` |
| Linux 32-bit | `tools/hex2wav/linux/hex2wav32_bin {hex} {wav}` |
| macOS | `tools/hex2wav/macosx/hex2wav {hex} {wav}` |
| Windows | `tools/hex2wav/windows/hex2wav.exe {hex} {wav}` |
| Java (any OS) | `java -jar tools/hex2wav/hex2wav.jar -i {hex} -o {wav}` |

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
- **Use auto mode**: Set `custom_hex2wav_cmd = auto` in platformio.ini
- **Check post-script output**: Look for errors in build log
- **Verify hex2wav binary**: Run manually to test
- **Check permissions**: Binary must be executable (Linux/macOS)

### Wrong OS Binary
Use `custom_hex2wav_cmd = auto` to avoid OS mismatch issues. If manual mode:
```bash
# Check binary architecture (Linux/macOS)
file tools/hex2wav/linux/hex2wav64_bin

# Make executable if needed (Linux/macOS)
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
# Set in platformio.ini:
custom_hex2wav_auto_play = no

pio run
# Then manually inspect .pio/build/attiny85/firmware.wav
```
