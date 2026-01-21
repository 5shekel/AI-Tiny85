# Code Mode Rules (Non-Obvious Only)

- Use [`analogReadScaled()`](../../src/vco_1voct.cpp:91) for pot readings, NOT raw analogRead() - compensates for LiPo voltage divider
- Use [`my_delay()`](../../src/vco_1voct.cpp:131) instead of delay() - millis() is broken due to custom Timer0 config
- All ISR-shared variables MUST be `volatile`
- Lookup tables MUST use PROGMEM + `pgm_read_byte/word` - no RAM for arrays
- Only ONE source file active at a time - edit `build_src_filter` in [`platformio.ini`](../../platformio.ini:41)
- Timer1 PLL enable (`PLLCSR = 1 << PCKE | 1 << PLLE`) required for 64MHz PWM audio
- Timer0 configured for 10kHz interrupt rate - don't modify without recalculating synthesis
