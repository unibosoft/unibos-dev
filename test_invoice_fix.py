#!/usr/bin/env python3
"""Test script for invoice processor fix"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from invoice_processor_cli import InvoiceProcessorCLI

# Create instance
cli = InvoiceProcessorCLI()

# Test render in terminal
print("\n" + "="*60)
print("Testing Invoice Processor CLI Render")
print("="*60 + "\n")

# Clear screen
sys.stdout.write("\033[2J\033[H")

# Run in content area mode (simulating the UNIBOS integration)
cli.run_in_content_area(31, 3, 88, 40)

print("\nTest completed!")