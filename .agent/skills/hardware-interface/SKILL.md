---
name: hardware-interface
description: Hardware interfacing patterns for ATtiny85 including ADC voltage scaling, analog button multiplexing, and NeoPixel visual feedback for debugging without serial.
---

# Hardware Interface Patterns

This skill teaches you how to interface with hardware peripherals on the ATtiny85 synthesizer, including potentiometers, buttons, and NeoPixels.

## Pin Assignments

| Pin | Function | Notes |
|-----|----------|-------|
| PB0 (Pin 5) | NeoPixel Data | NEOPIXELPIN |
| PB1 (Pin 6) | Speaker/PWM | OC1A output |
| PB2 (Pin 7) | Detune Pot | A2 / POTI_DETUNE |
| PB3 (Pin 2) | Buttons | A3 / BUTTON_PIN (multiplexed) |
| PB4 (Pin 3) | Pitch Pot | A1 / POTI_PITCH |
| PB5 (Pin 1) | RESET | Not available for I/O |

## ADC Voltage Scaling

### The Problem
The ATtiny85 runs on LiPo battery (3.7V), but potentiometers connect to a voltage divider that outputs max 2.6V. Raw `analogRead()` won't reach 1023.

### The Solution: `analogReadScaled()`

```cpp
#define Vcc  37  // 3.7V (LiPo battery)
#define Vdiv 26  // 2.6V (max voltage on analog pins)

uint16_t analogReadScaled(uint8_t channel) {
    uint16_t value = analogRead(channel);
    value = value * Vcc / Vdiv;  // Scale to full range
    if (value > 1023) value = 1023;  // Clamp
    return value;
}
```

### Usage
```cpp
// ❌ Don't use raw analogRead for pots
uint16_t raw = analogRead(POTI_PITCH);  // Max ~713

// ✅ Use scaled read
uint16_t scaled = analogReadScaled(POTI_PITCH);  // Full 0-1023
```

## Button Multiplexing

### Hardware Design
Multiple buttons share one analog pin (A3) via a resistor voltage divider. Each button produces a different voltage:

```
Vcc ───┬─── R1 ─── Button1 ─── GND
       │
       ├─── R2 ─── Button2 ─── GND
       │
       └─────────── A3 (BUTTON_PIN)
```

### Voltage Thresholds

```cpp
#define Vbutton_releaseLevel  450  // No button pressed
#define Vbutton_left          380  // Left button only
#define Vbutton_right         300  // Right button only
#define Vbutton_both          224  // Both buttons
#define Vbutton_pressedLevel  Vbutton_left

#define BUTTON_NONE   0
#define BUTTON_LEFT   1
#define BUTTON_RIGHT  2
```

### Button Detection State Machine

```cpp
uint8_t wasButtonPressed() {
    static uint8_t buttonPressed = false;
    static uint8_t buttonState = BUTTON_NOTPRESSED;
    static uint8_t buttonMaxValue = 0;
    uint8_t buttonReturnValue = BUTTON_NONE;
    uint16_t pinVoltage = analogRead(BUTTON_PIN);
    
    // Hysteresis for noise rejection
    if (pinVoltage > Vbutton_releaseLevel) buttonPressed = false;
    if (pinVoltage < Vbutton_pressedLevel) buttonPressed = true;
    
    switch (buttonState) {
        case BUTTON_NOTPRESSED:
            buttonMaxValue = 0;
            if (buttonPressed) buttonState = BUTTON_PRESSED;
            break;
            
        case BUTTON_PRESSED:
            if (buttonPressed) {
                // Detect which button(s)
                uint8_t buttonValue = BUTTON_NONE;
                if (pinVoltage < Vbutton_both) 
                    buttonValue = BUTTON_LEFT + BUTTON_RIGHT;
                else if (pinVoltage < Vbutton_right) 
                    buttonValue = BUTTON_RIGHT;
                else if (pinVoltage < Vbutton_left) 
                    buttonValue = BUTTON_LEFT;
                    
                if (buttonValue > buttonMaxValue) 
                    buttonMaxValue = buttonValue;
            } else {
                // Button released - return detected value
                buttonState = BUTTON_NOTPRESSED;
                buttonReturnValue = buttonMaxValue;
            }
            break;
    }
    return buttonReturnValue;
}
```

### Usage
```cpp
void loop() {
    uint8_t btn = wasButtonPressed();
    if (btn != BUTTON_NONE) {
        if (btn == BUTTON_LEFT) { /* left action */ }
        if (btn == BUTTON_RIGHT) { /* right action */ }
        if (btn == (BUTTON_LEFT + BUTTON_RIGHT)) { /* both */ }
    }
}
```

## NeoPixel Visual Feedback

### Why NeoPixels?
ATtiny85 has no serial port for debugging. NeoPixels provide visual feedback using just one pin.

### Setup
```cpp
#include <Adafruit_NeoPixel.h>

#define NUMPIXELS 20
#define NEOPIXELPIN 0

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(
    NUMPIXELS, NEOPIXELPIN, NEO_GRB + NEO_KHZ800);

void setup() {
    pinMode(NEOPIXELPIN, OUTPUT);
    pixels.begin();
    pixels.setBrightness(100);  // 0-255
}
```

### Debug Patterns

```cpp
// Show state with color
void showState(uint8_t state) {
    uint32_t colors[] = {
        pixels.Color(255, 0, 0),    // Red: State 0
        pixels.Color(0, 255, 0),    // Green: State 1
        pixels.Color(0, 0, 255),    // Blue: State 2
        pixels.Color(255, 255, 0),  // Yellow: State 3
    };
    pixels.fill(colors[state % 4]);
    pixels.show();
}

// Show value as brightness
void showValue(uint16_t value) {
    uint8_t brightness = map(value, 0, 1023, 0, 255);
    pixels.fill(pixels.Color(brightness, brightness, brightness));
    pixels.show();
}

// Error indicator (blink red)
void showError() {
    for (int i = 0; i < 5; i++) {
        pixels.fill(pixels.Color(255, 0, 0));
        pixels.show();
        my_delay(200);
        pixels.clear();
        pixels.show();
        my_delay(200);
    }
}
```

### Waveform Indicator (From Project)
```cpp
uint32_t color = 0;
switch(current_waveform) {
    case WAVE_SAW:      color = pixels.Color(255, 0, 0);     break; // Red
    case WAVE_SQUARE:   color = pixels.Color(0, 0, 255);     break; // Blue
    case WAVE_TRIANGLE: color = pixels.Color(0, 255, 0);     break; // Green
    case WAVE_SINE:     color = pixels.Color(255, 0, 255);   break; // Purple
}
pixels.fill(color);
pixels.show();
```

## Custom Delay Function

### The Problem
Arduino's `delay()` and `millis()` rely on Timer0, which is reconfigured for audio synthesis. They don't work correctly.

### The Solution: Tick-Based Delay

```cpp
volatile uint16_t ticks = 0;  // Incremented in ISR @ 10kHz

// 1 tick = 100µs, so ms * 10 = ticks needed
void my_delay(uint16_t ms) {
    uint16_t duration = ms * 10;
    uint16_t start;
    
    // Atomic read of start time
    uint8_t sreg = SREG;
    cli();
    start = ticks;
    SREG = sreg;
    
    while (1) {
        uint16_t current;
        sreg = SREG;
        cli();
        current = ticks;
        SREG = sreg;
        
        if ((uint16_t)(current - start) >= duration) break;
    }
}
```

### Usage
```cpp
// ❌ Don't use Arduino delay
delay(100);  // Broken due to Timer0 reconfiguration

// ✅ Use custom delay
my_delay(100);  // Works correctly (100ms)
```

## EMA Smoothing for ADC

Exponential Moving Average reduces noise on potentiometer readings:

```cpp
uint16_t smoothedRead(uint8_t channel) {
    static uint32_t accumulator = 0;
    static bool first_run = true;
    
    uint16_t rawVal = analogReadScaled(channel);
    
    if (first_run) {
        accumulator = (uint32_t)rawVal << 4;  // Initialize
        first_run = false;
    }
    
    // EMA with factor 1/16
    accumulator = accumulator - (accumulator >> 4) + rawVal;
    return accumulator >> 4;
}
```

## Hardware Constraints

1. **Pin sharing**: Only 5 usable GPIO pins - multiplex where possible
2. **No serial debug**: Use NeoPixels for visual feedback
3. **ADC resolution**: 10-bit (0-1023), but voltage divider limits range
4. **Button debouncing**: Hardware RC or software state machine required
5. **NeoPixel timing**: `pixels.show()` disables interrupts briefly - avoid during critical audio
