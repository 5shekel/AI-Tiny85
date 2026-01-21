---
name: audio-synthesis
description: Digital audio synthesis techniques for ATtiny85 using phase accumulator synthesis, timer-based PWM output, and waveform generation within strict ISR timing constraints.
---

# Audio Synthesis on ATtiny85

This skill teaches you how to generate audio on the ATtiny85 using DDS (Direct Digital Synthesis) with PWM output.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Timer0 ISR @ 10kHz                      │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Phase Accum │───▶│ Waveform Gen │───▶│ OCR1A (PWM)   │  │
│  │ phase += inc│    │ saw/sq/tri/sin│   │ 8-bit sample  │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
└────────────────────────────────────┬────────────────────────┘
                                     │
                                     ▼
                              Timer1 64MHz PLL
                              PWM Audio Output
                              (Pin 1 / OC1A)
```

## Timer Configuration

### Timer1: PWM Audio Output (64MHz PLL)
```cpp
// Enable 64MHz PLL for high-resolution PWM
PLLCSR = 1 << PCKE | 1 << PLLE;

// Timer1 PWM setup
TIMSK = 0;  // Disable Timer1 interrupts
TCCR1 = 1 << PWM1A |    // Enable PWM on OC1A
        2 << COM1A0 |   // Clear on compare, set at TOP
        1 << CS10;      // No prescaling (64MHz)
pinMode(SPEAKERPIN, OUTPUT);  // Pin 1
```

### Timer0: Synthesis Interrupt (10kHz)
```cpp
// CTC mode with prescaler 8
TCCR0A = 3 << WGM00;           // CTC mode
TCCR0B = 1 << WGM02 | 2 << CS00; // CTC + prescaler 8
TIMSK = 1 << OCIE0A;           // Enable compare interrupt
OCR0A = 199;                   // 16MHz / 8 / 200 = 10kHz
```

## Phase Accumulator Synthesis

The core synthesis technique uses a 16-bit phase accumulator:

```cpp
volatile uint16_t phase = 0;
volatile uint16_t phase_increment = 0;  // Controls frequency

ISR(TIMER0_COMPA_vect) {
    phase += phase_increment;
    uint8_t sample = generate_waveform(phase);
    OCR1A = sample;  // Output to PWM
}
```

### Frequency Calculation
```
phase_increment = (frequency × 65536) / sample_rate
                = (frequency × 65536) / 10000

Example: 440Hz (A4)
  increment = 440 × 65536 / 10000 = 2884
```

### Note Frequency Table
Pre-calculated PROGMEM table for MIDI notes 24-96:
```cpp
const uint16_t note_increments[] PROGMEM = {
    214, 227, 241, 255, 270, 286, ...  // Octave 1 (MIDI 24-35)
    429, 455, 482, 510, 541, 573, ...  // Octave 2 (MIDI 36-47)
    858, 909, 963, ...                  // Octave 3 (MIDI 48-59)
    // etc.
};

// Usage
uint16_t inc = pgm_read_word(&note_increments[noteIndex]);
```

## Waveform Generation

All waveforms derived from the 16-bit phase accumulator:

```cpp
static inline uint8_t get_waveform_sample(uint16_t p, uint8_t wave) {
    uint8_t p_high = p >> 8;  // High byte (0-255)
    
    switch(wave) {
        case WAVE_SAW:
            // Rising ramp
            return p_high;
            
        case WAVE_SQUARE:
            // 50% duty cycle
            return (p_high > 127) ? 255 : 0;
            
        case WAVE_TRIANGLE:
            // Fold at midpoint
            return (p & 0x8000) ? ((uint8_t)(~(p >> 7))) 
                                : ((uint8_t)(p >> 7));
            
        case WAVE_SINE:
            // Lookup table
            return pgm_read_byte(&sine256[p_high]);
    }
}
```

### Sine Table (256 entries)
```cpp
const byte sine256[] PROGMEM = {
    0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 7, 9, 10, 11,
    // ... 256 entries covering 0-255 sine wave
};
```

## ISR Timing Constraint

**Critical**: The ISR must complete in under 100µs (1000 cycles at 10kHz):

```cpp
ISR(TIMER0_COMPA_vect) {
    ticks++;                              // ~2 cycles
    phase += phase_increment;             // ~8 cycles
    phase2 += phase_increment2;           // ~8 cycles
    
    uint8_t s1 = get_waveform(phase);     // ~20-50 cycles
    uint8_t s2 = get_waveform(phase2);    // ~20-50 cycles
    
    OCR1A = (s1 + s2) >> 1;               // ~4 cycles
}
// Total: ~60-120 cycles, well under 1600 limit
```

### ISR Best Practices
1. **No function calls** - use `inline` or direct code
2. **No divisions** - use shifts or lookup tables
3. **No floating point** - use fixed-point math
4. **Minimize memory access** - cache in registers
5. **Single exit point** - avoid early returns

## Dual Oscillator with Detune

```cpp
volatile uint16_t phase, phase2;
volatile uint16_t phase_increment, phase_increment2;

// Calculate detune offset for second oscillator
uint16_t detune_offset = ((uint32_t)base_inc * detuneVal) >> 10;
phase_increment2 = base_inc + detune_offset;

// Mix in ISR
OCR1A = (sample1 + sample2) >> 1;
```

## ADC-Controlled Pitch

```cpp
void loop() {
    uint16_t potVal = analogReadScaled(POTI_PITCH);
    uint8_t noteIndex = map(potVal, 0, 1023, 0, NOTE_COUNT - 1);
    uint16_t inc = pgm_read_word(&note_increments[noteIndex]);
    phase_increment = inc;  // Atomic 16-bit write OK on AVR
    my_delay(10);  // Rate limit, reduce noise
}
```

## EMA Smoothing for Noisy ADC

```cpp
static uint32_t accumulator = 0;
static bool first_run = true;

if (first_run) {
    accumulator = (uint32_t)rawVal << 4;
    first_run = false;
}

accumulator = accumulator - (accumulator >> 4) + rawVal;
uint16_t smoothed = accumulator >> 4;  // Factor 1/16
```

## Audio Quality Tips

1. **Use 64MHz PLL** - Essential for acceptable PWM resolution
2. **10kHz sample rate** - Good balance of quality vs. CPU load
3. **Hardware low-pass filter** - Add RC filter on output for smoother audio
4. **Consistent ISR timing** - Jitter causes audible artifacts
5. **Anti-aliasing** - Keep fundamental below 5kHz (Nyquist)
