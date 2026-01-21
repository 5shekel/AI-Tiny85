# Ask Mode Rules (Non-Obvious Only)

- This is embedded audio synthesis for ATtiny85 (8-bit AVR), NOT web/desktop C++
- [`src/vco_1voct.cpp`](../../src/vco_1voct.cpp) is a VCO synthesizer, not a general example
- Upload happens via audio WAV playback to TinyAudioBoot bootloader - see [`README.md`](../../README.md:39)
- Pin assignments documented in [`README.md`](../../README.md:16) hardware section
- Project structure follows 8Bit Mixtape NEO conventions, not standard Arduino
- Technical specs: 16MHz CPU, 64MHz PLL timer, 10kHz synthesis rate, MIDI 24-96 range
