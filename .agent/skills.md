# Skills Configuration

This project uses [Anthropic's Agent Skills](https://github.com/anthropics/skills) format to teach Claude domain-specific expertise for ATtiny85 audio synthesizer development.

## Available Skills

### Core Development Skills

| Skill | Path | Use When |
|-------|------|----------|
| **ATtiny85 Embedded** | [`skills/attiny85-embedded/`](skills/attiny85-embedded/SKILL.md) | Writing or reviewing code for the ATtiny85 microcontroller |
| **Audio Synthesis** | [`skills/audio-synthesis/`](skills/audio-synthesis/SKILL.md) | Implementing DSP, waveform generation, or timer-based audio |
| **TinyAudioBoot** | [`skills/tinyaudioboot/`](skills/tinyaudioboot/SKILL.md) | Building, uploading, or troubleshooting firmware uploads |
| **Hardware Interface** | [`skills/hardware-interface/`](skills/hardware-interface/SKILL.md) | Working with pots, buttons, NeoPixels, or ADC |

## Skill Details

### attiny85-embedded
**Description**: ATtiny85 microcontroller development patterns, memory constraints, and AVR-specific coding practices for severely resource-constrained embedded systems.

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

## Usage Notes

1. **Automatic Loading**: Claude should reference relevant skills based on task context
2. **Explicit Invocation**: Ask Claude to "use the audio-synthesis skill" for specific guidance
3. **Skill Combination**: Multiple skills often apply together (e.g., attiny85-embedded + audio-synthesis)

## Related Documentation

- [`AGENTS.md`](../AGENTS.md) - Top-level agent guidance
- [`rules/`](rules/) - Mode-specific rules
- [`workflows/`](workflows/) - Multi-step workflow definitions
