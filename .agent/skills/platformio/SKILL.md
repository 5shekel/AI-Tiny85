---
name: platformio
description: PlatformIO CLI build system for embedded development. Covers installation, PATH issues, common commands, and project configuration.
---

# PlatformIO Build System

This skill covers using PlatformIO CLI for building embedded firmware, including common installation and PATH issues across different operating systems.

## Finding PlatformIO Executable

### When `pio` Command Not Found

PlatformIO installed via VSCode extension is not automatically added to PATH. Use the full path:

| OS | Full Path to Executable |
|----|------------------------|
| Windows | `C:\Users\<username>\.platformio\penv\Scripts\platformio.exe` |
| Linux | `~/.platformio/penv/bin/platformio` |
| macOS | `~/.platformio/penv/bin/platformio` |

### Windows Examples (PowerShell - VSCode default)
```powershell
# Using full path with call operator
& "C:\Users\user\.platformio\penv\Scripts\platformio.exe" run

# Using $env:USERPROFILE variable
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run

# Clean and rebuild
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run --target clean; & "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

### Windows Examples (CMD)
```cmd
:: Using full path
C:\Users\user\.platformio\penv\Scripts\platformio.exe run

:: Using %USERPROFILE% variable
%USERPROFILE%\.platformio\penv\Scripts\platformio.exe run
```

### Linux/macOS Examples
```bash
# Using full path
~/.platformio/penv/bin/platformio run

# Using $HOME variable
$HOME/.platformio/penv/bin/platformio run
```

### Adding to PATH (Permanent Fix)

**Windows (PowerShell - VSCode default):**
```powershell
# Add to user PATH
$env:PATH += ";$env:USERPROFILE\.platformio\penv\Scripts"
# Make permanent (run as admin):
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$env:USERPROFILE\.platformio\penv\Scripts", "User")
```

**Windows (CMD):**
```cmd
:: Add to current session
set PATH=%PATH%;%USERPROFILE%\.platformio\penv\Scripts

:: Make permanent via System Properties > Environment Variables
```

**Linux/macOS (bash/zsh):**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.platformio/penv/bin:$PATH"

# Apply immediately
source ~/.bashrc
```

## Common Commands

### Build Commands
```bash
pio run                    # Build all environments
pio run -e attiny85        # Build specific environment
pio run --target clean     # Clean build artifacts
pio run --target upload    # Build and upload
pio run -v                 # Verbose build output
```

### Project Commands
```bash
pio project init           # Initialize new project
pio project config         # Show project configuration
pio pkg install            # Install dependencies
pio pkg update             # Update dependencies
```

### Device Commands
```bash
pio device list            # List connected devices
pio device monitor         # Serial monitor
```

## Project Configuration

### [`platformio.ini`](../../../platformio.ini) Structure

```ini
[platformio]
description = Project description

[env:attiny85]
platform = atmelavr
board = attiny85
framework = arduino
board_build.f_cpu = 16000000L

; Build flags
build_flags = 
    -DF_CPU=16000000L
    -DCUSTOM_DEFINE

; Dependencies
lib_deps = 
    adafruit/Adafruit NeoPixel

; Extra scripts (post-build hooks)
extra_scripts = 
    scripts/post_build.py

; Custom options (use custom_ prefix to avoid warnings)
custom_my_option = value
```

### Accessing Custom Options in Scripts

```python
# In extra_scripts Python file
from SCons.Script import Import
Import("env")

# Read custom option with default
value = env.GetProjectOption("custom_my_option", default="default_value")
```

## Source File Selection

Control which source files are compiled using `build_src_filter`:

```ini
build_src_filter = 
    -<*>              ; Exclude all files by default
    +<main.cpp>       ; Include specific file
    ; +<other.cpp>    ; Comment out alternatives
```

## Troubleshooting

### Build Fails with Module Not Found
```bash
# PlatformIO not installed as Python module
python -m platformio run  # Won't work

# Use the bundled executable instead
~/.platformio/penv/bin/platformio run
```

### Permission Denied (Linux/macOS)
```bash
# Make PlatformIO executable
chmod +x ~/.platformio/penv/bin/platformio
```

### VSCode Terminal vs External Terminal
- VSCode's integrated terminal may have different PATH settings
- If `pio` works in VSCode but not external terminal, add to shell profile
- If `pio` works externally but not in VSCode, restart VSCode after PATH changes

### Clean Rebuild
```bash
# Force complete rebuild
pio run --target clean && pio run
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PLATFORMIO_HOME_DIR` | Override PlatformIO home (~/.platformio) |
| `PLATFORMIO_CORE_DIR` | Override core packages location |
| `PLATFORMIO_CACHE_DIR` | Override cache location |

## Integration Notes

- PlatformIO creates `.pio/` directory for build artifacts
- Add `.pio/` to `.gitignore`
- Configuration in `platformio.ini` is project-specific
- Libraries cached in `~/.platformio/lib/`
