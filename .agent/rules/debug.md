# Debug Mode Rules (Non-Obvious Only)

- No serial debugging available on ATtiny85 - use NeoPixels for visual debug output
- Build output at `.pio/build/attiny85/` - check `firmware.hex` and `firmware.wav`
- WAV file must play through audio jack to ATtiny85 - no USB/UART upload
- Check [`scripts/hex2wav_post.py`](../../scripts/hex2wav_post.py) console output for conversion errors
- If upload fails: verify volume level, audio connection, and bootloader is active
- Flash limit: 8KB (47% used); RAM limit: 512B (14% used) - memory overflow causes silent failures
- Timer conflicts: modifying Timer0/Timer1 breaks audio synthesis without obvious symptoms
