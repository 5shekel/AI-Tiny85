# Skills

Domain-specific expertise for ATtiny85 audio synthesizer development. Each skill contains detailed instructions in its `SKILL.md` file.

## Available Skills

| Skill | Path | Use When |
|-------|------|----------|
| **ATtiny85 Embedded** | [`skills/attiny85-embedded/`](skills/attiny85-embedded/SKILL.md) | Writing or reviewing code for the ATtiny85 microcontroller |
| **Audio Synthesis** | [`skills/audio-synthesis/`](skills/audio-synthesis/SKILL.md) | Implementing DSP, waveform generation, or timer-based audio |
| **TinyAudioBoot** | [`skills/tinyaudioboot/`](skills/tinyaudioboot/SKILL.md) | Building, uploading, or troubleshooting firmware uploads |
| **Hardware Interface** | [`skills/hardware-interface/`](skills/hardware-interface/SKILL.md) | Working with pots, buttons, NeoPixels, or ADC |
| **PlatformIO** | [`skills/platformio/`](skills/platformio/SKILL.md) | Build system issues, `pio` command not found, project configuration |

## Usage

1. **Automatic**: Skills are referenced based on task context
2. **Explicit**: Request "use the audio-synthesis skill" for specific guidance
3. **Combined**: Multiple skills often apply together

---

### attiny85-embedded

**Description**: Core ATtiny85 development patterns for memory-constrained embedded systems.

**Key Topics**:
- Memory constraints (8KB flash, 512B RAM)
- PROGMEM for lookup tables
- Volatile for ISR-shared variables
- No dynamic allocation patterns
- Direct register manipulation

**Trigger scenarios**:
- Creating new source files
- Reviewing code for memory issues
- Optimizing existing functionality

---

### audio-synthesis

**Description**: Digital audio synthesis techniques for ATtiny85 using phase accumulator synthesis, timer-based PWM output, and waveform generation within strict ISR timing constraints.

**Key Topics**:
- Timer1 64MHz PLL configuration
- Timer0 10kHz synthesis interrupt
- Phase accumulator DDS
- Waveform generation (saw, square, triangle, sine)
- ISR timing constraints (<100µs)

**Trigger scenarios**:
- Adding new waveforms or oscillators
- Modifying audio output
- Debugging timing issues

---

### tinyaudioboot

**Description**: TinyAudioBoot firmware upload workflow using WAV audio files instead of traditional ISP programming.

**Key Topics**:
- hex2wav conversion process
- PlatformIO configuration
- OS-specific setup
- Upload troubleshooting
- Firmware size constraints

**Trigger scenarios**:
- Build failures
- Upload issues
- Configuring new development environment
- Setting up CI/CD

---

### hardware-interface

**Description**: Hardware interfacing patterns for ATtiny85 including ADC voltage scaling, analog button multiplexing, and NeoPixel visual feedback.

**Key Topics**:
- `analogReadScaled()` for voltage divider compensation
- Button multiplexing via voltage thresholds
- NeoPixel visual feedback (debug without serial)
- `my_delay()` instead of `delay()`
- EMA smoothing for ADC

**Trigger scenarios**:
- Adding new controls
- Debugging hardware interactions
- Implementing visual feedback

---

### platformio

**Description**: PlatformIO CLI build system for embedded development, covering installation, PATH configuration, and cross-platform setup.

**Key Topics**:
- Finding PlatformIO executable when `pio` not in PATH
- Windows: `C:\Users\<user>\.platformio\penv\Scripts\platformio.exe`
- Linux/macOS: `~/.platformio/penv/bin/platformio`
- Project configuration (`platformio.ini`)
- Custom options with `custom_` prefix
- Source file selection with `build_src_filter`

**Trigger scenarios**:
- `pio` command not found
- Build system configuration
- Setting up new development environment
- Cross-platform build issues

## Skill Format

Each skill follows the [Anthropic Agent Skills specification](https://github.com/anthropics/skills/tree/main/spec):

```
skills/
└── skill-name/
    └── SKILL.md     # YAML frontmatter + markdown instructions
```

### SKILL.md Structure

```yaml
---
name: skill-name
description: Brief description of what this skill does
---

# Skill Title

[Detailed instructions, examples, and guidelines]
```

## Related Documentation

- [`AGENTS.md`](../AGENTS.md) - Project overview and build commands
- [`rules.md`](rules.md) - Mode-specific rules
