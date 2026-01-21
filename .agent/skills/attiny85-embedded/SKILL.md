---
name: attiny85-embedded
description: ATtiny85 microcontroller development patterns, memory constraints, and AVR-specific coding practices for severely resource-constrained embedded systems.
---

# ATtiny85 Embedded Development

This skill teaches you how to write efficient, correct code for the ATtiny85 microcontroller with extreme resource constraints.

## Hardware Constraints

| Resource | Limit | Impact |
|----------|-------|--------|
| Flash | 8KB | No large libraries, minimal code |
| RAM | 512 bytes | No dynamic allocation, small variables |
| Clock | 16MHz (8MHz internal) | Limited processing per cycle |
| Pins | 6 GPIO (5 usable) | Pin multiplexing required |

## Core Patterns

### 1. No Dynamic Allocation
```cpp
// ❌ NEVER do this
char* buffer = new char[64];
String myString = "hello";

// ✅ Use static allocation
char buffer[64];
const char myString[] PROGMEM = "hello";
```

### 2. PROGMEM for Constants
All lookup tables and constant data must be stored in flash:
```cpp
// ✅ Correct: Store in flash
const byte sine256[] PROGMEM = { 0, 3, 6, 9, ... };
uint8_t value = pgm_read_byte(&sine256[index]);

const uint16_t frequencies[] PROGMEM = { 214, 227, 241, ... };
uint16_t freq = pgm_read_word(&frequencies[index]);
```

### 3. Volatile for ISR-Shared Variables
Any variable accessed by both ISR and main code must be volatile:
```cpp
volatile uint16_t phase = 0;
volatile uint16_t ticks = 0;

ISR(TIMER0_COMPA_vect) {
    ticks++;  // Modified in ISR
    phase += phase_increment;
}

void loop() {
    uint16_t current_ticks;
    cli(); current_ticks = ticks; sei();  // Atomic read
}
```

### 4. Atomic Access for Multi-Byte Variables
16-bit and larger variables need atomic access:
```cpp
// ✅ Proper atomic read
uint8_t sreg = SREG;
cli();
uint16_t local_copy = shared_16bit_variable;
SREG = sreg;
```

### 5. Direct Register Manipulation
Use direct register access for precise timing:
```cpp
// Timer configuration (no Arduino abstractions)
TCCR0A = 3 << WGM00;           // CTC mode
TCCR0B = 1 << WGM02 | 2 << CS00; // Prescaler 8
TIMSK = 1 << OCIE0A;           // Enable interrupt
OCR0A = 199;                   // Compare value
```

## Required Includes

```cpp
#include <Arduino.h>
#include <avr/pgmspace.h>    // PROGMEM, pgm_read_*
#include <avr/interrupt.h>   // ISR, cli(), sei()
#include <avr/power.h>       // clock_prescale_set
```

## Clock Configuration

```cpp
void setup() {
    #if defined(__AVR_ATtiny85__)
    if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
    #endif
}
```

## Memory Optimization Tips

1. Use `uint8_t` instead of `int` where possible (saves 1 byte per variable)
2. Prefer `static` local variables over globals when scope allows
3. Use bit fields for boolean flags: `struct { uint8_t flag1:1; uint8_t flag2:1; }`
4. Avoid function calls in tight loops - use `inline` or macros
5. Check flash/RAM usage: `.pio/build/attiny85/firmware.elf` with `avr-size`

## Build Verification

Always check resource usage:
```bash
pio run  # Shows flash/RAM usage in output
# Flash: 47% used, RAM: 14% used (typical)
```

If approaching limits, consider:
- Removing unused code
- Simplifying algorithms
- Moving constants to PROGMEM
- Using smaller data types
