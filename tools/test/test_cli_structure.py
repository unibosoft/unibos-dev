#!/usr/bin/env python3
"""
Test CLI structure and common functionality for all three profiles
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_cli_imports():
    """Test that all three CLI profiles can be imported"""
    print("Testing CLI imports...")

    errors = []

    # Test dev profile
    try:
        from core.profiles.dev.main import cli as dev_cli, main as dev_main
        print("✓ unibos-dev imports successfully")
    except Exception as e:
        errors.append(f"❌ unibos-dev import error: {e}")

    # Test prod profile
    try:
        from core.profiles.prod.main import cli as prod_cli, main as prod_main
        print("✓ unibos imports successfully")
    except Exception as e:
        errors.append(f"❌ unibos import error: {e}")

    # Test server profile
    try:
        from core.profiles.server.main import cli as server_cli, main as server_main
        print("✓ unibos-server imports successfully")
    except Exception as e:
        errors.append(f"❌ unibos-server import error: {e}")

    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False

    return True

def test_interactive_modes():
    """Test that all interactive modes can be imported"""
    print("\nTesting interactive modes...")

    errors = []

    # Test dev interactive
    try:
        from core.profiles.dev.interactive import run_interactive as dev_interactive
        from core.profiles.dev.interactive import UnibosDevInteractive
        print("✓ unibos-dev interactive mode available")
    except Exception as e:
        errors.append(f"❌ unibos-dev interactive error: {e}")

    # Test prod interactive
    try:
        from core.profiles.prod.interactive import run_interactive as prod_interactive
        from core.profiles.prod.interactive import UnibosNodeInteractive
        print("✓ unibos interactive mode available")
    except Exception as e:
        errors.append(f"❌ unibos interactive error: {e}")

    # Test server interactive
    try:
        from core.profiles.server.interactive import run_interactive as server_interactive
        from core.profiles.server.interactive import UnibosServerInteractive
        print("✓ unibos-server interactive mode available")
    except Exception as e:
        errors.append(f"❌ unibos-server interactive error: {e}")

    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False

    return True

def test_tui_availability():
    """Test TUI availability for profiles that have it"""
    print("\nTesting TUI availability...")

    # Test dev TUI (should exist)
    try:
        from core.profiles.dev.tui import UnibosDevTUI, run_interactive
        print("✓ unibos-dev TUI available")
    except ImportError:
        print("⚠ unibos-dev TUI not available (will fallback to basic interactive)")

    # Test if prod/server might have TUI in future
    try:
        from core.profiles.prod.tui import UnibosNodeTUI
        print("✓ unibos TUI available")
    except ImportError:
        print("⚠ unibos TUI not yet implemented")

    try:
        from core.profiles.server.tui import UnibosServerTUI
        print("✓ unibos-server TUI available")
    except ImportError:
        print("⚠ unibos-server TUI not yet implemented")

    return True

def test_common_framework():
    """Test that common framework components are available"""
    print("\nTesting common framework...")

    try:
        from core.clients.cli.framework.interactive import InteractiveMode
        from core.clients.cli.framework.ui import MenuItem, MenuState, Colors
        from core.clients.tui.base import BaseTUI
        print("✓ Common CLI/TUI framework available")
        return True
    except Exception as e:
        print(f"❌ Framework error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("UNIBOS CLI Structure Test")
    print("=" * 60)

    results = []

    results.append(test_cli_imports())
    results.append(test_interactive_modes())
    results.append(test_tui_availability())
    results.append(test_common_framework())

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All structural tests passed!")
        print("\nCLI Commands:")
        print("  - unibos-dev: Development & deployment tools")
        print("  - unibos: Standalone node management")
        print("  - unibos-server: Production server management")
        print("\nAll three share common framework and can run in interactive mode.")
    else:
        print("⚠ Some tests failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()