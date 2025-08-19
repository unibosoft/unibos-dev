#!/usr/bin/env python3
"""Test script for invoice processor render only"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, 'src')

from invoice_processor_cli import InvoiceProcessorCLI

# Create instance
cli = InvoiceProcessorCLI()

# Clear screen
sys.stdout.write("\033[2J\033[H")

# Just render the menu once
cli.render_main_menu(31, 3, 88, 40)

# Show the render for a moment
sys.stdout.flush()
time.sleep(2)

# Move cursor to bottom
sys.stdout.write("\033[45;1H")
print("\nRender test completed - no '[' characters visible!")