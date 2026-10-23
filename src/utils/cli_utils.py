from colorama import Fore, Style, init

# Initialize colorama (strip=False ensures it works nicely in Windows terminals)
init(autoreset=True)


def colored(text: str, color_name: str) -> str:
    """Returns a string wrapped in the specified ANSI color escape code."""
    # Convert input string (e.g., 'red', 'GREEN') to uppercase matching Colorama keys
    color_key = color_name.strip().upper()

    # Safely fetch the color from Fore, default to empty string if not found
    color_code = getattr(Fore, color_key, '')

    print(f"{color_code}{text}{Style.RESET_ALL}")
