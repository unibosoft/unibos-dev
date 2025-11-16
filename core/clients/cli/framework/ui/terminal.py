"""
UNIBOS CLI Terminal Utilities
Cross-platform terminal manipulation functions

Extracted from v527 main.py
Reference: docs/development/cli_v527_reference.md
"""

import os
import sys
import platform
import unicodedata
from typing import Tuple, List


def clear_screen():
    """Clear the terminal screen with enhanced clearing"""
    # Use ANSI escape sequences for more thorough clearing
    sys.stdout.write('\033[2J')  # Clear entire screen
    sys.stdout.write('\033[H')   # Move cursor to top-left
    sys.stdout.write('\033[3J')  # Clear scrollback buffer (supported terminals)
    sys.stdout.flush()

    # Also use OS-specific clear command as fallback
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    sys.stdout.flush()  # Ensure screen is fully cleared before continuing


def get_terminal_size() -> Tuple[int, int]:
    """
    Get terminal dimensions

    Returns:
        Tuple of (columns, lines)
    """
    try:
        import shutil
        columns, lines = shutil.get_terminal_size((80, 24))
        return columns, lines
    except Exception:
        return 80, 24


def move_cursor(x: int, y: int):
    """
    Move cursor to position (1-indexed)

    Args:
        x: Column position (1-indexed)
        y: Row position (1-indexed)
    """
    print(f"\033[{y};{x}H", end='', flush=True)


def hide_cursor():
    """Hide the terminal cursor"""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    """Show the terminal cursor"""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def flush_input_buffer(times: int = 3):
    """
    Flush input buffer multiple times to prevent escape sequence leak

    This prevents arrow key escape sequences (ESC[A, ESC[B) from leaking
    into the footer or other UI components during rapid navigation.

    V527 Solution: Triple buffer flush with delays between each flush.

    Args:
        times: Number of flush iterations (default: 3)

    Example:
        After handling UP/DOWN arrow keys:
        >>> flush_input_buffer(times=2)
    """
    try:
        import sys
        import time

        # Only flush on Unix-like systems (macOS, Linux)
        if platform.system() != 'Windows':
            import termios
            for _ in range(times):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                time.sleep(0.01)  # 10ms delay between flushes
    except Exception:
        # Silently fail on platforms without termios
        pass


def get_spinner_frame(index: int) -> str:
    """
    Get a spinner animation frame

    Args:
        index: Frame index

    Returns:
        Unicode spinner character
    """
    spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    return spinners[index % len(spinners)]


def wrap_text(text: str, width: int) -> List[str]:
    """
    Wrap text to fit within specified width

    Args:
        text: Text to wrap
        width: Maximum line width

    Returns:
        List of wrapped lines
    """
    if not text:
        return []

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) <= width:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def print_centered(text: str, y: int = None):
    """
    Print text centered on the screen

    Args:
        text: Text to print
        y: Optional Y position
    """
    cols, _ = get_terminal_size()

    # Strip ANSI codes for length calculation
    from .colors import Colors
    clean_text = Colors.strip(text)
    text_width = len(clean_text)

    x = max(1, (cols - text_width) // 2)

    if y is not None:
        move_cursor(x, y)

    print(text, flush=True)


def get_visual_width(text: str) -> int:
    """
    Calculate the visual display width of text in a terminal.

    This accounts for:
    - Wide characters (emoji, CJK) that occupy 2 columns
    - Zero-width characters (variation selectors, combining marks)
    - Regular ASCII characters that occupy 1 column

    Args:
        text: Text to measure

    Returns:
        Visual width in terminal columns

    Example:
        >>> get_visual_width("hello")
        5
        >>> get_visual_width("🍽️")  # Emoji with variation selector
        2
        >>> get_visual_width(" 🛡️ guard")
        9  # 1 (space) + 2 (emoji) + 0 (variation) + 1 (space) + 5 (guard)
    """
    width = 0
    for char in text:
        # Variation selector (U+FE0F) and other combining marks have no width
        if unicodedata.combining(char) or char == '\uFE0F':
            continue

        # Check if character is wide (emoji, CJK, etc.)
        ea_width = unicodedata.east_asian_width(char)
        if ea_width in ('F', 'W'):  # Full-width or Wide
            width += 2
        else:
            width += 1

    return width


def pad_to_visual_width(text: str, target_width: int, fillchar: str = ' ') -> str:
    """
    Pad text to a specific visual width (not character count).

    This is a replacement for str.ljust() that accounts for emoji
    and wide characters displaying as 2 columns in terminals.

    Args:
        text: Text to pad
        target_width: Desired visual width in terminal columns
        fillchar: Character to use for padding (default: space)

    Returns:
        Padded text with exact visual width

    Example:
        >>> pad_to_visual_width("hello", 10)
        'hello     '  # 5 chars + 5 spaces = 10 visual columns
        >>> pad_to_visual_width(" 🛡️ guard", 25)
        ' 🛡️ guard                '  # emoji is 2 visual columns
    """
    current_width = get_visual_width(text)

    if current_width >= target_width:
        # Already at or exceeds target, return as-is
        return text

    # Calculate how many padding characters needed
    padding_needed = target_width - current_width

    return text + (fillchar * padding_needed)
