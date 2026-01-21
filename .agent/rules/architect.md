# Architect Mode Rules (Non-Obvious Only)

- **Severe constraints**: 8KB flash, 512B RAM - no STL, no dynamic allocation, minimal abstractions
- **Timer coupling**: Timer0 and Timer1 are tightly coupled for audio synthesis - cannot be repurposed
- **ISR bottleneck**: 10kHz synthesis ISR must complete in <100µs - avoid function calls in ISR
- **Single source model**: Only one .cpp compiles at a time via `build_src_filter` - not a multi-file project
- **Audio upload dependency**: All source files must produce <8KB hex for TinyAudioBoot compatibility
- **Analog multiplexing**: Pots and buttons share ADC pins via voltage dividers - pin changes require hardware redesign
- **PLL requirement**: 64MHz PLL for Timer1 PWM is mandatory for acceptable audio quality
