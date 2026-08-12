from src.enums import BankAction
from src.const import BANK_MENU
from src.utils.cli_utils import colored


def bank():
    print(BANK_MENU)

    try:
        user_choice = BankAction(int(input("Please Enter Choice: ")))
    except ValueError:
        colored("Invalid Choice!!!", "red")
        return

    match user_choice:
        case BankAction.OPEN_ACCOUNT:
            print("Open Account!")
        case BankAction.CLOSE_APP:
            print("Exiting app...")
        case _:
            print("Feature not implemented yet.")
