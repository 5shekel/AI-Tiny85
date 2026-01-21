# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build Commands

```bash
pio run                    # Build + auto-generate WAV for audio upload
pio run --target upload    # Build and play WAV (requires audio hardware)
pio run --target clean     # Clean build
```

## Non-Obvious Project Specifics

- **Audio Upload**: Firmware uploads via WAV audio through TinyAudioBoot bootloader, NOT traditional ISP programming
- **Source Selection**: Edit `build_src_filter` in [`platformio.ini`](platformio.ini:41) to switch active source file (only one .cpp active at a time)
- **Custom Options**: Use `custom_` prefix for platformio.ini options (e.g., `custom_hex2wav_cmd`) to avoid PlatformIO warnings
- **OS Configuration**: `custom_hex2wav_cmd` must be configured per OS (Linux/macOS/Windows variants in platformio.ini comments)

## Code Patterns

- **Timers**: Timer1 uses 64MHz PLL for PWM audio output; Timer0 runs 10kHz synthesis interrupt
- **ADC Scaling**: Use [`analogReadScaled()`](src/vco_1voct.cpp:91) for potentiometers - compensates for LiPo voltage divider (Vcc=3.7V, Vdiv=2.6V)
- **Delays**: Use [`my_delay()`](src/vco_1voct.cpp:131) instead of delay() - uses ISR ticks since millis() unreliable with custom timers
- **Buttons**: Single analog pin (A3) multiplexes multiple buttons via voltage divider thresholds
- **PROGMEM**: All lookup tables (sine, note increments) stored in flash using PROGMEM + `pgm_read_*`

## Code Style

- AVR includes: `<avr/pgmspace.h>`, `<avr/interrupt.h>`, `<avr/power.h>`
- `volatile` for ISR-shared variables
- Direct timer register manipulation for precise audio timing
- No dynamic allocation (8KB flash, 512B RAM constraint)

## Agent Configuration

For mode-specific rules, see [`.agent/rules.md`](.agent/rules.md) which contains:
- [`code.md`](.agent/rules/code.md) - Coding patterns and utilities
- [`debug.md`](.agent/rules/debug.md) - Debug and troubleshooting guidance
- [`ask.md`](.agent/rules/ask.md) - Documentation context
- [`architect.md`](.agent/rules/architect.md) - Architecture constraints

## Skills

Domain-specific expertise is available in [`.agent/skills/`](.agent/skills.md):
- [`attiny85-embedded`](.agent/skills/attiny85-embedded/SKILL.md) - Memory constraints, AVR patterns
- [`audio-synthesis`](.agent/skills/audio-synthesis/SKILL.md) - DSP, timer PWM, waveform generation
- [`tinyaudioboot`](.agent/skills/tinyaudioboot/SKILL.md) - WAV-based firmware upload
- [`hardware-interface`](.agent/skills/hardware-interface/SKILL.md) - ADC scaling, buttons, NeoPixels
