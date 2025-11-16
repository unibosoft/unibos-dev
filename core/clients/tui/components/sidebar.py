"""
UNIBOS TUI Sidebar Component
V527-style sidebar - proven, stable implementation
Rewritten from v527 sidebar_fix.py (2025-11-02)
"""

import sys
from typing import List, Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor
from core.clients.cli.framework.ui.emoji_safe_slice import emoji_safe_slice


class Sidebar:
    """Sidebar component for TUI - V527 Implementation"""

    def __init__(self, config):
        """Initialize sidebar with config"""
        self.config = config
        # V527 spec: sidebar width is exactly 25 characters (fixed)
        self.width = 25

        # Cache for fast updates (v527 anti-flicker)
        self.last_selected_index = -1
        self.last_section = -1
        self.last_y_position = -1  # Track last selected Y position

    def draw(self, sections: List, current_section: int, selected_index: int,
             in_submenu: bool = False):
        """
        Draw multi-section sidebar using V527 PROVEN logic

        V527 SPEC:
        - Clear entire sidebar area first
        - Draw each section with simple text formatting
        - Section format: " {icon} {title}"
        - Item format: " {name}" (name already includes emoji from data)
        - Width: EXACTLY 25 characters with ljust(25)
        - Background: ALWAYS BG_DARK on EVERY line
        - Spacing: 2 empty lines between sections

        Args:
            sections: List of MenuSection objects
            current_section: Currently active section index
            selected_index: Selected item within current section
            in_submenu: Whether in submenu (dims all sidebar items)
        """
        cols, lines = get_terminal_size()

        # V527 CRITICAL: Check if sidebar should be dimmed
        is_dimmed = in_submenu
        text_color = Colors.DIM if is_dimmed else Colors.WHITE
        title_color = Colors.DIM if is_dimmed else Colors.CYAN

        # V527 STEP 1: Clear entire sidebar area first (lines 2 to lines-1)
        # BUGFIX: Use range(2, lines) to extend to line lines-1 (footer is at line 'lines')
        for y in range(2, lines):
            sys.stdout.write(f"\033[{y};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
        sys.stdout.flush()

        # V527 STEP 2: Draw sections
        y_pos = 3  # Start at line 3 (after header at line 1)

        for section_idx, section in enumerate(sections):
            # BUGFIX: Stop at line 'lines' (footer position), not 'lines - 1'
            if y_pos >= lines:
                break

            # Draw section title (NO icon/emoji for section headers)
            title = section.label
            if self.config.lowercase_ui:
                title = title.lower()

            # V527: Use emoji_safe_slice for section title (max 22 chars)
            safe_title = emoji_safe_slice(title, 22)

            # Draw section header - two-step for consistent background
            # Step 1: Clear with background
            sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
            # Step 2: Draw text at column 2
            sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{Colors.BOLD}{title_color} {safe_title}{Colors.RESET}")
            y_pos += 1

            # Skip 1 line after section header (v527 has items start at +2 from section)
            y_pos += 1

            # Draw section items
            is_current_section = (section_idx == current_section)

            for item_idx, item in enumerate(section.items):
                # BUGFIX: Stop at line 'lines' (footer position), not 'lines - 1'
                if y_pos >= lines:
                    break

                # V527 CRITICAL: Clear line FIRST with BG_DARK
                sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
                sys.stdout.flush()

                # Get item text with icon
                # v527: Use double space for emojis with variation selector (FE0F)
                if hasattr(item, 'icon') and item.icon:
                    if '\uFE0F' in item.icon:
                        name = f"{item.icon}  {item.label}"  # 2 spaces for variation selector emojis
                    else:
                        name = f"{item.icon} {item.label}"   # 1 space for regular emojis
                else:
                    name = item.label

                # Apply lowercase if needed (keep emoji, lowercase text only)
                if self.config.lowercase_ui:
                    parts = name.split(' ', 1)
                    if len(parts) == 2 and hasattr(item, 'icon') and item.icon:
                        name = f"{parts[0]} {parts[1].lower()}"
                    else:
                        name = name.lower()

                # V527 EXACT: Use emoji_safe_slice with max 22 chars
                safe_name = emoji_safe_slice(name, 22)

                # Determine if this item is selected
                is_selected = (is_current_section and item_idx == selected_index and not is_dimmed)

                if is_selected:
                    # V527: Selected item - two-step drawing
                    # Step 1: Fill background
                    sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * self.width}{Colors.RESET}")
                    sys.stdout.flush()
                    # Step 2: Draw text at column 2
                    sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
                    sys.stdout.flush()
                else:
                    # V527: Normal item - two-step drawing
                    fg = text_color
                    if not item.enabled:
                        fg = Colors.DIM
                    # Step 1: Already cleared above
                    # Step 2: Draw text at column 2
                    sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{fg} {safe_name}{Colors.RESET}")
                    sys.stdout.flush()

                y_pos += 1

            # V527: Add 2 empty lines between sections with BG_DARK
            for _ in range(2):
                # BUGFIX: Stop at line 'lines' (footer position)
                if y_pos < lines:
                    sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
                    y_pos += 1
            sys.stdout.flush()

        # V527: Fill remaining sidebar space with BG_DARK
        # BUGFIX: Fill to line 'lines - 1' (footer is at line 'lines')
        while y_pos < lines:
            sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
            y_pos += 1
        sys.stdout.flush()

        # V527: Draw vertical separator
        # BUGFIX: Use range(2, lines) to draw separator to line 'lines - 1'
        for y in range(2, lines):
            sys.stdout.write(f"\033[{y};{self.width + 1}H{Colors.DIM}│{Colors.RESET}")
        sys.stdout.flush()

        # V527: Force final flush to ensure everything is rendered
        sys.stdout.flush()

    def update_selection_fast(self, sections: List, current_section: int,
                             selected_index: int, in_submenu: bool = False):
        """
        V527 FAST UPDATE: Only redraws changed lines to prevent flicker

        This is the v527 anti-flicker technique:
        1. Only update the previous selection line
        2. Only update the current selection line
        3. Use single buffer flush
        4. No full sidebar redraw

        Args:
            sections: List of MenuSection objects
            current_section: Currently active section index
            selected_index: Selected item within current section
            in_submenu: Whether in submenu (dims all sidebar items)
        """
        # V527: If section changed, do full redraw
        if current_section != self.last_section:
            self.draw(sections, current_section, selected_index, in_submenu)
            self.last_section = current_section
            self.last_selected_index = selected_index
            return

        # V527: Only redraw if selection changed within same section
        if selected_index == self.last_selected_index:
            return

        cols, lines = get_terminal_size()

        # V527: Get colors
        is_dimmed = in_submenu
        text_color = Colors.DIM if is_dimmed else Colors.WHITE

        # Calculate Y positions for items
        curr_y = self._calculate_item_y_position(sections, current_section, selected_index)
        prev_y = self._calculate_item_y_position(sections, current_section, self.last_selected_index)

        if curr_y == -1 or prev_y == -1:
            # Fallback to full redraw if calculation fails
            self.draw(sections, current_section, selected_index, in_submenu)
            self.last_selected_index = selected_index
            return

        section = sections[current_section]

        # V527: Redraw previous selection (clear highlight)
        if 0 <= self.last_selected_index < len(section.items):
            prev_item = section.items[self.last_selected_index]

            # Clear line with BG_DARK
            sys.stdout.write(f"\033[{prev_y};1H{Colors.BG_DARK}{' ' * self.width}{Colors.RESET}")
            sys.stdout.flush()

            # Get item text with icon
            if hasattr(prev_item, 'icon') and prev_item.icon:
                name = f"{prev_item.icon} {prev_item.label}"
            else:
                name = prev_item.label

            # Apply lowercase if needed (keep emoji, lowercase text only)
            if self.config.lowercase_ui:
                parts = name.split(' ', 1)
                if len(parts) == 2 and hasattr(prev_item, 'icon') and prev_item.icon:
                    name = f"{parts[0]} {parts[1].lower()}"
                else:
                    name = name.lower()

            # V527 EXACT: Use emoji_safe_slice with max 22 chars
            safe_name = emoji_safe_slice(name, 22)

            fg = text_color if prev_item.enabled else Colors.DIM
            # Step 1: Already cleared above
            # Step 2: Draw text at column 2
            sys.stdout.write(f"\033[{prev_y};2H{Colors.BG_DARK}{fg} {safe_name}{Colors.RESET}")
            sys.stdout.flush()

        # V527: Draw new selection (with highlight)
        if 0 <= selected_index < len(section.items) and not is_dimmed:
            curr_item = section.items[selected_index]

            # Get item text with icon
            if hasattr(curr_item, 'icon') and curr_item.icon:
                name = f"{curr_item.icon} {curr_item.label}"
            else:
                name = curr_item.label

            # Apply lowercase if needed (keep emoji, lowercase text only)
            if self.config.lowercase_ui:
                parts = name.split(' ', 1)
                if len(parts) == 2 and hasattr(curr_item, 'icon') and curr_item.icon:
                    name = f"{parts[0]} {parts[1].lower()}"
                else:
                    name = name.lower()

            # V527 EXACT: Use emoji_safe_slice with max 22 chars
            safe_name = emoji_safe_slice(name, 22)

            # V527: Selected item - two-step drawing
            # Step 1: Fill background
            sys.stdout.write(f"\033[{curr_y};1H{Colors.BG_ORANGE}{' ' * self.width}{Colors.RESET}")
            sys.stdout.flush()
            # Step 2: Draw text at column 2
            sys.stdout.write(f"\033[{curr_y};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
            sys.stdout.flush()

        # V527: Final flush for all updates (anti-flicker)
        sys.stdout.flush()

        # Update tracking
        self.last_selected_index = selected_index

    def _calculate_item_y_position(self, sections: List, section_idx: int, item_idx: int) -> int:
        """
        Calculate Y position for a specific item (V527 logic)

        V527 layout:
        - Line 3: Section 0 title
        - Line 4: (blank)
        - Line 5+: Section 0 items
        - +2 blank lines
        - Next section...

        Args:
            sections: List of MenuSection objects
            section_idx: Section index
            item_idx: Item index within section

        Returns:
            Y position or -1 if invalid
        """
        if section_idx < 0 or section_idx >= len(sections):
            return -1
        if item_idx < 0:
            return -1

        y = 3  # Start at line 3 (first section title)

        for i, section in enumerate(sections):
            if i == section_idx:
                # Found our section
                # Title at y, blank at y+1, items start at y+2
                if item_idx >= len(section.items):
                    return -1
                return y + 2 + item_idx

            # Skip past this section
            y += 1  # Section title
            y += 1  # Blank line
            y += len(section.items)  # All items
            y += 2  # Section spacing (2 blank lines)

        return -1

    def draw_separator(self):
        """
        Draw vertical separator line between sidebar and content (v527 spec)

        V527 SPEC:
        - Character: │ (Unicode Box Drawing Light Vertical, U+2502)
        - Position: Column 26 (sidebar_width + 1)
        - Color: Dim gray
        - Height: From line 2 to terminal height - 1
        """
        cols, lines = get_terminal_size()
        separator_col = self.width + 1  # Column 26

        # BUGFIX: Use range(2, lines) to draw separator to line 'lines - 1' (footer is at line 'lines')
        for y in range(2, lines):  # Start from line 2, end at line lines-1 (footer at lines)
            move_cursor(separator_col, y)
            sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")

        sys.stdout.flush()
