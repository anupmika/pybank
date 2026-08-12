from enum import Enum

class BankAction(Enum):
    OPEN_ACCOUNT = 1
    DEPOSIT_MONEY = 2
    WITHDRAW_MONEY = 3
    VIEW_BALANCE = 4
    VIEW_HISTORY = 5
    CLOSE_ACCOUNT = 6
    VIEW_ACCOUNT = 7
    CLOSE_APP = 8
