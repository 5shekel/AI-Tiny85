# ATtiny85 VCO Audio Synthesizer - Minimal Setup

PlatformIO project for ATtiny85 featuring a voltage-controlled oscillator (VCO) with 1V/octave tracking and audio upload via hex2wav.

## Project Overview

**Active Source:** `vco_1voct.cpp` - Dual VCO synthesizer with:
- **1V/octave pitch tracking** (MIDI 24-96 / C1-C7)
- **Dual oscillators** with logarithmic detune control
- **4 waveforms**: Sawtooth, Square, Triangle, Sine
- **NeoPixel visual feedback** (20 LEDs)
- **Button control** for waveform switching

## Hardware

**ATtiny85 Pinout:**
```
        ┌─────┐
  RESET │1   8│ VCC
    PB3 │2   7│ PB2 (SCK)
    PB4 │3   6│ PB1 (MISO / SPEAKER)
    GND │4   5│ PB0 (MOSI / NEOPIXEL)
        └─────┘
```

**Pin Assignments:**
- Pin 0 (PB0) - NeoPixels (20 LEDs)
- Pin 1 (PB1) - Audio Output (Speaker)
- A1 (PB2) - Pitch Control Pot (Right)
- A2 (PB4) - Detune Control Pot (Left)
- A3 (PB3) - Buttons

**Waveform Colors:**
- 🔴 **Red** - Sawtooth
- 🔵 **Blue** - Square
- 🟢 **Green** - Triangle
- 🟣 **Purple** - Sine

## Audio Upload System (hex2wav)

This project uses **TinyAudioBoot** bootloader with hex2wav audio upload:

### How It Works
1. Build creates a `.hex` file
2. `hex2wav` converts it to `.wav` audio file
3. Play the WAV through audio jack into the ATtiny85
4. Bootloader decodes and programs the chip

### Upload Process
```bash
# Build and automatically generate WAV + play it
pio run

# Or manually upload
pio run --target upload
```

The WAV file is automatically played via `aplay`. Connect:
- Audio output → ATtiny85 audio input
- Make sure volume is appropriate

## Building

**Requirements:**
- PlatformIO
- Linux with `aplay` (for audio playback)

**Commands:**
```bash
# Build project
pio run

# Clean build
pio run --target clean
```

**Build Output:**
- Flash: ~3,884 bytes / 8,192 bytes (47%)
- RAM: ~73 bytes / 512 bytes (14%)
- WAV: `.pio/build/attiny85/firmware.wav`

## Configuration

### platformio.ini
- **Clock:** 16MHz external crystal
- **Framework:** Arduino
- **Libraries:** Adafruit NeoPixel (auto-installed)
- **Upload:** Custom hex2wav audio upload

## Minimal Project Structure

```
.
├── src/
│   └── vco_1voct.cpp          # Dual VCO synthesizer (ACTIVE)
├── scripts/
│   └── hex2wav_post.py        # Post-build hex→wav conversion
├── tools/
│   └── hex2wav/
│       ├── linux/             # Linux binaries (64-bit, 32-bit)
│       ├── macosx/            # macOS binary
│       ├── windows/           # Windows binary
│       └── hex2wav.jar        # Java version (cross-platform)
├── platformio.ini             # PlatformIO configuration
└── README.md                  # This file
```

**What's NOT included (minimal setup):**
- Extra visual/emulator scripts
- Custom include files (not needed for vco_1voct)
- Extra libraries (not needed for vco_1voct)
- Other source files

## Resources

- [8Bit Mixtape NEO](https://github.com/8BitMixtape/8Bit-Mixtape-NEO)
- [TinyAudioBoot](https://github.com/ChrisMicro/TinyAudioBoot)
- [hex2wav Tool](https://github.com/ATtinyTeenageRiot/hex2wav)
- [ATtiny85 Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf)


