#!/usr/bin/env python3
"""Test navigation key detection"""

import os
import sys

# Set debug mode
os.environ['UNIBOS_DEBUG'] = 'true'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import get_single_key

print("Navigation Test - Press arrow keys, 'q' to quit")
print("Debug log will be written to /tmp/unibos_key_debug.log")

# Clear debug log
with open('/tmp/unibos_key_debug.log', 'w') as f:
    f.write("=== Navigation Test Started ===\n")

while True:
    print("\nWaiting for key...")
    key = get_single_key(timeout=0.1)
    
    if key:
        print(f"Got key: {repr(key)}")
        
        if key == '\x1b[A':
            print("UP ARROW detected!")
        elif key == '\x1b[B':
            print("DOWN ARROW detected!")
        elif key == '\x1b[C':
            print("RIGHT ARROW detected!")
        elif key == '\x1b[D':
            print("LEFT ARROW detected!")
        elif key.lower() == 'q':
            print("Quitting...")
            break
        else:
            print(f"Other key: {repr(key)}")

print("\nTest complete. Check /tmp/unibos_key_debug.log for details.")