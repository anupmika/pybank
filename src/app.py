from src.handlers.pybank import PyBank
from src.enums import BankAction
from src.const import BANK_MENU
from src.const import DB_PATH
from src.utils.cli_utils import colored


def bank():
    while True:
        print(BANK_MENU)

        try:
            user_choice = BankAction(int(input("\nPlease Enter Choice: ")))
        except ValueError:
            colored("Invalid Choice!!!", "red")
            continue

        obj = PyBank()

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
                print("Exiting!!!")
                return
