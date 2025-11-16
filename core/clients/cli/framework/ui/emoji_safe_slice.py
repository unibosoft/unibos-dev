"""
Emoji-safe string slicing utilities.

This module provides functions for safely slicing strings containing emojis
and other multi-width Unicode characters, ensuring proper visual width.
"""

import unicodedata
import re
from typing import Tuple


def get_display_width(text: str) -> int:
    """
    Calculate the display width of a string, accounting for emojis and wide characters.

    Args:
        text: The string to measure

    Returns:
        The display width in terminal columns
    """
    width = 0
    i = 0
    while i < len(text):
        char = text[i]

        # Check for ANSI escape sequences
        if char == '\033':
            # Find the end of the escape sequence
            j = i + 1
            while j < len(text) and text[j] != 'm':
                j += 1
            i = j + 1
            continue

        # Check for emoji variation selector (U+FE0F)
        if i + 1 < len(text) and text[i + 1] == '\uFE0F':
            width += 2  # Emoji with variation selector is wide
            i += 2
            continue

        # Check for other combining characters
        if unicodedata.combining(char):
            i += 1
            continue

        # Check for wide characters (CJK, emojis, etc.)
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        # Check if it's an emoji
        elif ord(char) >= 0x1F300:  # Common emoji range
            width += 2
        else:
            width += 1

        i += 1

    return width


def emoji_safe_slice(text: str, max_width: int) -> str:
    """
    Slice a string to a maximum display width, accounting for emojis.

    This function ensures that emojis and other wide characters are not
    split in the middle, and that the resulting string fits within the
    specified display width.

    Args:
        text: The string to slice
        max_width: The maximum display width in terminal columns

    Returns:
        The sliced string that fits within max_width
    """
    if not text:
        return text

    width = 0
    i = 0
    result = []

    while i < len(text) and width < max_width:
        char = text[i]

        # Check for ANSI escape sequences
        if char == '\033':
            # Find the end of the escape sequence and include it all
            j = i + 1
            while j < len(text) and text[j] != 'm':
                j += 1
            result.append(text[i:j+1])
            i = j + 1
            continue

        # V527: Handle emoji sequences (emoji + variation selector U+FE0F)
        # This ensures emoji+selector are treated as a single 2-width unit
        if i + 1 < len(text) and ord(text[i + 1]) == 0xFE0F:
            # This is an emoji with variation selector
            char_width = 2
            if width + char_width <= max_width:
                result.append(text[i:i+2])  # Include BOTH characters as ONE unit
                width += char_width
            i += 2  # Skip both the emoji AND the variation selector
            continue  # Process next character

        # Check for other combining characters
        if unicodedata.combining(char):
            result.append(char)
            i += 1
            continue

        # Calculate character width
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            char_width = 2
        elif ord(char) >= 0x1F300:  # Common emoji range
            char_width = 2
        else:
            char_width = 1

        # Add character if it fits
        if width + char_width <= max_width:
            result.append(char)
            width += char_width
        else:
            break

        i += 1

    return ''.join(result)
