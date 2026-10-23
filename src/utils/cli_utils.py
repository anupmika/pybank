"""
CLI utility functions for terminal output formatting.
"""

from colorama import Fore, Style, init

# Initialize colorama (strip=False ensures it works nicely in Windows terminals)
init(autoreset=True)


def colored(text: str, color_name: str) -> str:
    """
    Print text in the specified color and return the colored string.
    
    Args:
        text: The text to be colored.
        color_name: Color name (e.g., 'red', 'green', 'yellow', 'blue').
                    Case-insensitive, falls back to no color if invalid.
        
    Returns:
        The text wrapped in ANSI color escape codes.
    """
    # Convert input string (e.g., 'red', 'GREEN') to uppercase matching Colorama keys
    color_key = color_name.strip().upper()

    # Safely fetch the color from Fore, default to empty string if not found
    color_code = getattr(Fore, color_key, '')

    print(f"{color_code}{text}{Style.RESET_ALL}")
    return f"{color_code}{text}{Style.RESET_ALL}"

