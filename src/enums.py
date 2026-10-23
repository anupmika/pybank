"""
Enumerations for PyBank application.
Defines menu action choices.
"""

from enum import Enum


class BankAction(Enum):
    """Enumeration of available bank operations from the main menu."""
    OPEN_ACCOUNT = 1      # Register a new account
    DEPOSIT_MONEY = 2     # Deposit money into an account
    WITHDRAW_MONEY = 3    # Withdraw money from an account
    VIEW_BALANCE = 4      # View account balance
    VIEW_HISTORY = 5      # View transaction history
    CLOSE_ACCOUNT = 6     # Close/deactivate an account
    VIEW_ACCOUNT = 7      # View full account and user details
    CLOSE_APP = 8         # Exit the application
