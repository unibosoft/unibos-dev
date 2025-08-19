#!/usr/bin/env python3
"""Test arrow key detection"""

import sys
import termios
import tty

def get_key():
    """Get single key press"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        
        # Read first character
        key = sys.stdin.read(1)
        
        # Handle escape sequences (arrow keys, etc.)
        if key == '\x1b':
            # For escape sequences, we need to read the full sequence
            try:
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    second = sys.stdin.read(1)
                    if second == '[':
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            third = sys.stdin.read(1)
                            return f'\x1b[{third}'
            except:
                pass
            # If we can't read a complete sequence, just return ESC
            return '\x1b'
        
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

print("Press arrow keys to test (q to quit):")
print("===============================")

while True:
    key = get_key()
    
    # Display the key
    if key == '\x1b[A':
        print("UP ARROW detected")
    elif key == '\x1b[B':
        print("DOWN ARROW detected")
    elif key == '\x1b[C':
        print("RIGHT ARROW detected")
    elif key == '\x1b[D':
        print("LEFT ARROW detected")
    elif key == 'q':
        print("Quitting...")
        break
    else:
        print(f"Key pressed: {repr(key)}")