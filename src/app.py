"""
Main application module for PyBank CLI.
Handles the main menu loop and user input routing to PyBank operations.
"""

from src.const import BANK_MENU
from src.enums import BankAction
from src.handlers.pybank import PyBank
from src.utils.cli_utils import colored


def bank():
    """
    Run the main PyBank CLI application loop.

    Displays the bank menu, accepts user input, and routes requests
    to the appropriate PyBank methods. Continues until the user
    chooses to exit the application.
    """
    while True:
        # Display the main menu
        print(BANK_MENU)

        try:
            # Get and validate user choice
            user_choice = BankAction(int(input('\nPlease Enter Choice: ')))
        except ValueError:
            colored('Invalid Choice!!!', 'red')
            continue

        # Create PyBank instance for this operation
        obj = PyBank()
        try:
            # Route to appropriate handler based on user choice
            match user_choice:
                case BankAction.OPEN_ACCOUNT:
                    obj.register_account()
                case BankAction.DEPOSIT_MONEY:
                    obj.deposit_money()
                case BankAction.WITHDRAW_MONEY:
                    obj.withdraw_money()
                case BankAction.VIEW_BALANCE:
                    obj.view_balance()
                case BankAction.VIEW_HISTORY:
                    obj.view_history()
                case BankAction.CLOSE_ACCOUNT:
                    obj.close_account()
                case BankAction.VIEW_ACCOUNT:
                    obj.view_data()
                case BankAction.CLOSE_APP:
                    print('Exiting!!!')
                    return
        finally:
            obj.connect.close()
