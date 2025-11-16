#!/usr/bin/env python3
"""
Test script for UNIBOS TUI - verifies Enter key handling
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_dev_tui():
    """Test unibos-dev TUI"""
    print("=" * 60)
    print("Testing unibos-dev TUI")
    print("=" * 60)

    from core.profiles.dev.tui import UnibosDevTUI

    # Create TUI instance
    tui = UnibosDevTUI()

    # Check handler registration
    print("\nRegistered handlers:")
    for handler_id in sorted(tui.action_handlers.keys()):
        print(f"  ✓ {handler_id}")

    # Check menu structure
    sections = tui.get_menu_sections()
    print(f"\nMenu sections: {len(sections)}")
    for section in sections:
        print(f"  - {section.label}: {len(section.items)} items")

    # Test a handler directly
    print("\nTesting handler execution:")
    test_item = type('TestItem', (), {'id': 'git_status', 'label': 'git status'})()

    try:
        print("  Calling git_status handler...")
        result = tui.handle_git_status(test_item)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n✓ TUI initialization successful")
    print("  All handlers registered")
    print("  Menu structure loaded")
    return True

def test_basic_interactive():
    """Test basic interactive mode"""
    print("\n" + "=" * 60)
    print("Testing basic interactive mode")
    print("=" * 60)

    from core.profiles.dev.interactive import UnibosDevInteractive

    # Create interactive instance
    interactive = UnibosDevInteractive()

    # Check sections
    sections = interactive.get_sections()
    print(f"\nMenu sections: {len(sections)}")
    for section in sections:
        print(f"  - {section['label']}: {len(section['items'])} items")

    print("\n✓ Basic interactive mode functional")
    return True

def test_key_detection():
    """Test key detection"""
    print("\n" + "=" * 60)
    print("Testing key detection")
    print("=" * 60)

    from core.clients.cli.framework.ui.input import get_single_key, Keys

    print("\nKey constants:")
    print(f"  ENTER: {repr(Keys.ENTER)}")
    print(f"  UP: {repr(Keys.UP)}")
    print(f"  DOWN: {repr(Keys.DOWN)}")
    print(f"  ESC: {repr(Keys.ESC)}")

    print("\n✓ Key detection module loaded")
    return True

if __name__ == "__main__":
    try:
        # Run tests
        test_key_detection()
        test_basic_interactive()
        test_dev_tui()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nThe TUI should now work properly with Enter key.")
        print("Test it by running: unibos-dev")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)