#!/usr/bin/env python3
"""
Debug script to test Enter key handling in TUI
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Enable debug mode
os.environ['UNIBOS_DEBUG'] = 'true'

# Create debug log file
debug_file = '/tmp/unibos_tui_debug.log'

def log_debug(msg):
    """Log debug message"""
    with open(debug_file, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        f.flush()

# Clear previous debug log
with open(debug_file, 'w') as f:
    f.write("=== TUI Debug Log ===\n")

log_debug("Starting TUI debug session")

# Import after setting debug mode
from core.clients.cli.framework.ui.input import get_single_key, Keys

print("TUI Enter Key Debug Test")
print("=" * 50)
print()
print("Press keys to test detection:")
print("- Press ENTER to test Enter key")
print("- Press arrows to test arrow keys")
print("- Press 'q' to quit")
print()
print(f"Debug log: {debug_file}")
print()

# Test key detection
while True:
    key = get_single_key(timeout=0.1)

    if key:
        log_debug(f"Key detected: {repr(key)}")

        # Display key info
        if key == Keys.ENTER or key == '\r':
            print(f"✓ ENTER key detected! (raw: {repr(key)})")
            log_debug("Enter key confirmed!")
        elif key == Keys.UP:
            print(f"↑ UP arrow (raw: {repr(key)})")
        elif key == Keys.DOWN:
            print(f"↓ DOWN arrow (raw: {repr(key)})")
        elif key == Keys.LEFT:
            print(f"← LEFT arrow (raw: {repr(key)})")
        elif key == Keys.RIGHT:
            print(f"→ RIGHT arrow (raw: {repr(key)})")
        elif key == Keys.ESC or key == '\x1b':
            print(f"ESC key (raw: {repr(key)})")
        elif key == 'q':
            print("Quitting...")
            break
        else:
            print(f"Other key: {repr(key)}")

print()
print(f"Check debug log: {debug_file}")