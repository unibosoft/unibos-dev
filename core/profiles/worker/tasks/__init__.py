"""
UNIBOS Worker Tasks
Task modules for background processing
"""

# Import task modules for autodiscovery
from . import core

# Optional task modules (import if available)
try:
    from . import ocr
except ImportError:
    pass

try:
    from . import media
except ImportError:
    pass
