#!/usr/bin/env python3
"""
Test script for invoice processor CLI fixes
"""

import sys
import os

# Add the src directory to the path
sys.path.append('/Users/berkhatirli/Desktop/unibos/src')

from invoice_processor_cli import InvoiceProcessorCLI

def test_cli():
    """Test the invoice processor CLI"""
    # Clear screen
    sys.stdout.write("\033[2J\033[H")
    
    print("Testing Invoice Processor CLI")
    print("=" * 50)
    
    # Create CLI instance
    cli = InvoiceProcessorCLI()
    
    print("✓ CLI instance created")
    print(f"✓ Processor available: {cli.processor_available}")
    print(f"✓ Selected option initialized: {cli.selected_option}")
    print(f"✓ Total options: {cli.total_options}")
    
    print("\nTest completed. Starting CLI in content area...")
    print("Use arrow keys to navigate, Enter to select, 'q' to quit")
    print("Press any key to start...")
    
    # Wait for keypress
    cli.get_key()
    
    # Start the CLI in content area mode
    try:
        cli.run_in_content_area()
    except KeyboardInterrupt:
        print("\nCLI interrupted by user")
    except Exception as e:
        print(f"\nError running CLI: {e}")
    
    # Clear screen on exit
    sys.stdout.write("\033[2J\033[H")
    print("CLI test completed")

if __name__ == "__main__":
    test_cli()