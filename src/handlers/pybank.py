import sqlite3
from datetime import datetime
from pydantic import ValidationError
from src.validators.models import User, Account, TransactionRecord
from src.sqlite_db import SqliteDB


class PyBank:
    def __init__(self):
        db = SqliteDB()
        self.connect = db.db_connect()
        self.cursor = self.connect.cursor()

    def register_account(self):
        cursor = self.cursor
        raw_aadhar_num: str = input("Enter 12-digit Aadhar Number (no dashes): ")
        raw_name = input("Enter Full Name: ")
        raw_email = input("Enter Email (Optional, press Enter to skip): ") or None
        raw_phone = input("Enter Phone Number: ")
        raw_age = input("Enter Age: ")
        raw_father = input("Enter Father's Name: ")
        raw_address = input("Enter Address (Optional, press Enter to skip): ") or None
        raw_city = input("Enter City: ")
        raw_initial_bal = input("Enter Initial Balance: ")

        user_input = {
            "aadhar_num": raw_aadhar_num,
            "name": raw_name,
            "email": raw_email,
            "phone": raw_phone,
            "age": raw_age,
            "fatherName": raw_father,
            "address": raw_address,
            "city": raw_city,
            "initialBal": raw_initial_bal,
        }

        try:
            validated_user = User(**user_input)
            user_dict = validated_user.model_dump()

            user_query = """
            INSERT INTO users (aadhar_num, name, email, phone, age, father_name, address, city, initial_balance, created_at)
            VALUES (:aadhar_num, :name, :email, :phone, :age, :father_name, :address, :city, :initial_balance, :created_at)
            """
            cursor.execute(user_query, user_dict)
            new_user_id = cursor.lastrowid

            generated_account_num = 500000 + new_user_id

            account_input = {
                "accountNum": generated_account_num,
                "userId": new_user_id,
                "balance": validated_user.initial_balance,
                "currency": "INR",
            }
            validated_account = Account(**account_input)
            account_dict = validated_account.model_dump()

            account_query = """
            INSERT INTO accounts (account_num, user_id, account_type, balance, currency, is_active, created_at)
            VALUES (:account_num, :user_id, :account_type, :balance, :currency, :is_active, :created_at)
            """
            cursor.execute(account_query, account_dict)

            self.connect.commit()

            print(
                f"\n==============================================\n"
                f"🎉 REGISTRATION SUCCESSFUL!\n"
                f"Dear {validated_user.name}, your account is active.\n"
                f"Your system assigned Account Number is: {validated_account.account_num}\n"
                f"Opening Balance: {validated_account.balance} {validated_account.currency}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print("\n❌ Registration Failed! Correct these issues:")
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                print(f" - {field}: {error['msg']}")
            self.connect.rollback()

        except sqlite3.IntegrityError:
            print(
                "\n❌ Database Error: This CNIC profile already exists in our system!"
            )
            self.connect.rollback()

    def view_balance(self):
        cursor = self.cursor

        try:
            target_acc = input("Enter your Account Number: ")

            query = """
            SELECT account_num, user_id, account_type, balance, currency, is_active, created_at
            FROM accounts
            WHERE account_num = ?
            """
            cursor.execute(query, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: Account number not found in our records.")
                return

            account_data = {
                "account_num": row[0],
                "user_id": row[1],
                "account_type": row[2],
                "balance": row[3],
                "currency": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6],
            }

            account = Account.model_validate(account_data)

            print(
                f"\n==============================================\n"
                f"📊 ACCOUNT SUMMARY\n"
                f"Account Number : {account.account_num}\n"
                f"Account Type   : {account.account_type.capitalize()}\n"
                f"Current Balance: {account.balance:,.2f} {account.currency}\n"
                f"Status         : {'🟢 Active' if account.is_active else '🔴 Inactive'}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print(f"❌ Corrupted Database Data detected: {e.errors()}")
        except Exception as err:
            print(f"❌ An error occurred: {err}")

    def view_data(self):

        cursor = self.cursor

        try:
            target_acc = input("Enter Account Number to view full profile: ")

            query = """
            SELECT
                u.aadhar_num, u.name, u.email, u.phone, u.age, u.father_name, u.address, u.city, u.initial_balance, u.created_at,
                a.account_num, a.user_id, a.account_type, a.balance, a.currency, a.is_active, a.created_at
            FROM accounts a
            INNER JOIN users u ON a.user_id = u.id
            WHERE a.account_num = ?
            """
            cursor.execute(query, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: No registered profile found for this Account Number.")
                return

            user_data = {
                "aadhar_num": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "age": row[4],
                "father_name": row[5],
                "address": row[6],
                "city": row[7],
                "initial_balance": row[8],
                "created_at": row[9],
            }

            account_data = {
                "account_num": row[10],
                "user_id": row[11],
                "account_type": row[12],
                "balance": row[13],
                "currency": row[14],
                "is_active": bool(row[15]),
                "created_at": row[16],
            }

            user = User.model_validate(user_data)
            account = Account.model_validate(account_data)

            if not account.is_active:
                print("❌ Error: Account is closed/inactive. Details not available.")
                return

            print(
                f"\n==============================================\n"
                f"👤 CUSTOMER PROFILE & ACCOUNT DETAILS\n"
                f"==============================================\n"
                f" CUSTOMER DETAILS:\n"
                f"  • Name        : {user.name}\n"
                f"  • Father Name : {user.father_name}\n"
                f"  • AAdhar Number : {user.aadhar_num}\n"
                f"  • Age / City  : {user.age} yrs / {user.city}\n"
                f"  • Phone / Email: {user.phone} / {user.email or 'N/A'}\n"
                f"  • Address     : {user.address or 'N/A'}\n\n"
                f" 🏦 ACCOUNT METRICS:\n"
                f"  • Account No. : {account.account_num}\n"
                f"  • Type        : {account.account_type.capitalize()}\n"
                f"  • Currency    : {account.currency}\n"
                f"  • Net Balance : {account.balance:,.2f} {account.currency}\n"
                f"  • Account Status: {'🟢 Active' if account.is_active else '🔴 Inactive'}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print(
                f"❌ Structural Validation Error: System record is corrupted. {e.errors()}"
            )
        except Exception as err:
            print(f"❌ Failed to fetch complete record data: {err}")

    def withdraw_money(self):

        cursor = self.cursor

        try:
            target_acc = input("Enter Account Number: ")
            withdraw_amount_str = input("Enter Amount to Withdraw: ")

            try:
                amount_to_sub = float(withdraw_amount_str)
                if amount_to_sub <= 0:
                    print("❌ Error: Withdraw amount must be greater than zero.")
                    return
            except ValueError:
                print(
                    "❌ Error: Invalid amount entered. Please type a valid numeric number."
                )
                return

            query_select = """
                SELECT account_num, user_id, account_type, balance, currency, is_active, created_at
                FROM accounts
                WHERE account_num = ?
                """
            cursor.execute(query_select, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: Account number not found.")
                return

            account_data = {
                "account_num": row[0],
                "user_id": row[1],
                "account_type": row[2],
                "balance": row[3] - amount_to_sub,  # Calculate new tentative balance
                "currency": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6],
            }

            account = Account.model_validate(account_data)

            if not account.is_active:
                print(
                    "❌ Transaction Denied: Cannot withdraw into an inactive account."
                )
                return

            query_update = "UPDATE accounts SET balance = ? WHERE account_num = ?"
            cursor.execute(query_update, (account.balance, account.account_num))

            transaction_query = """
                INSERT INTO transactions (account_num, transaction_type, amount, balance_after, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """
            cursor.execute(transaction_query, (
                account.account_num,
                'withdraw',
                amount_to_sub,
                account.balance,
                datetime.now().isoformat()
            ))
            self.connect.commit()

            print(
                f"\n==============================================\n"
                f"💰 WITHDRAW TRANSACTION SUCCESSFUL\n"
                f"Account Number : {account.account_num}\n"
                f"Withdraw : -{amount_to_sub:,.2f} {account.currency}\n"
                f"Updated Balance: {account.balance:,.2f} {account.currency}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print(
                f"❌ Transaction Blocked: Balance constraint validation failed. {e.errors()}"
            )
            self.connect.rollback()
        except Exception as err:
            print(f"❌ System error during withdraw execution: {err}")
            self.connect.rollback()

    def deposit_money(self):

        cursor = self.cursor

        try:
            target_acc = input("Enter Account Number: ")
            deposit_amount_str = input("Enter Amount to Deposit: ")

            try:
                amount_to_add = float(deposit_amount_str)
                if amount_to_add <= 0:
                    print("❌ Error: Deposit amount must be greater than zero.")
                    return
            except ValueError:
                print(
                    "❌ Error: Invalid amount entered. Please type a valid numeric number."
                )
                return

            query_select = """
                SELECT account_num, user_id, account_type, balance, currency, is_active, created_at
                FROM accounts
                WHERE account_num = ?
                """
            cursor.execute(query_select, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: Account number not found.")
                return

            account_data = {
                "account_num": row[0],
                "user_id": row[1],
                "account_type": row[2],
                "balance": row[3] + amount_to_add,
                "currency": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6],
            }

            account = Account.model_validate(account_data)

            if not account.is_active:
                print("❌ Transaction Denied: Cannot deposit into an inactive account.")
                return

            query_update = "UPDATE accounts SET balance = ? WHERE account_num = ?"
            cursor.execute(query_update, (account.balance, account.account_num))

            transaction_query = """
                INSERT INTO transactions (account_num, transaction_type, amount, balance_after, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """
            cursor.execute(transaction_query, (
                account.account_num,
                'deposit',
                amount_to_add,
                account.balance,
                datetime.now().isoformat()
            ))
            self.connect.commit()

            print(
                f"\n==============================================\n"
                f"💰 DEPOSIT TRANSACTION SUCCESSFUL\n"
                f"Account Number : {account.account_num}\n"
                f"Deposited      : +{amount_to_add:,.2f} {account.currency}\n"
                f"Updated Balance: {account.balance:,.2f} {account.currency}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print(
                f"❌ Transaction Blocked: Balance constraint validation failed. {e.errors()}"
            )
            self.connect.rollback()
        except Exception as err:
            print(f"❌ System error during deposit execution: {err}")
            self.connect.rollback()

    def view_history(self):
        cursor = self.cursor

        try:
            target_acc = input("Enter Account Number: ")

            query_select = """
                SELECT account_num, user_id, account_type, balance, currency, is_active, created_at
                FROM accounts
                WHERE account_num = ?
                """
            cursor.execute(query_select, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: Account number not found.")
                return

            account_data = {
                "account_num": row[0],
                "user_id": row[1],
                "account_type": row[2],
                "balance": row[3],
                "currency": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6],
            }

            account = Account.model_validate(account_data)

            if not account.is_active:
                print("❌ Error: Account is closed/inactive. History not available.")
                return

            history_query = """
                SELECT transaction_type, amount, balance_after, timestamp
                FROM transactions
                WHERE account_num = ?
                ORDER BY timestamp DESC
                """
            cursor.execute(history_query, (target_acc,))
            transactions = cursor.fetchall()

            if not transactions:
                print("\n📭 No transactions found for this account.")
                return

            print(
                f"\n==============================================\n"
                f"📜 TRANSACTION HISTORY\n"
                f"Account Number : {target_acc}\n"
                f"=============================================="
            )
            print(f"{'#':<4} {'Type':<10} {'Amount':>12} {'Balance After':>14} {'Timestamp':<22}")
            print("-" * 66)

            for idx, txn in enumerate(transactions, start=1):
                txn_type, amount, balance_after, timestamp = txn
                sign = '+' if txn_type == 'deposit' else '-'
                print(f"{idx:<4} {txn_type.capitalize():<10} {sign}{amount:>11,.2f} {balance_after:>14,.2f} {timestamp:<22}")

            print("=" * 66)

        except ValidationError as e:
            print(
                f"❌ Structural Validation Error: System record is corrupted. {e.errors()}"
            )
        except Exception as err:
            print(f"❌ Failed to fetch transaction history: {err}")


    def close_account(self):
        cursor = self.cursor

        try:
            target_acc = input("Enter Account Number to Close: ")

            query_select = """
                SELECT account_num, user_id, account_type, balance, currency, is_active, created_at
                FROM accounts
                WHERE account_num = ?
                """
            cursor.execute(query_select, (target_acc,))
            row = cursor.fetchone()

            if row is None:
                print("❌ Error: Account number not found.")
                return

            account_data = {
                "account_num": row[0],
                "user_id": row[1],
                "account_type": row[2],
                "balance": row[3],
                "currency": row[4],
                "is_active": bool(row[5]),
                "created_at": row[6],
            }

            account = Account.model_validate(account_data)

            if not account.is_active:
                print(
                    "❌ Account is already closed/inactive."
                )
                return

            query_update = "UPDATE accounts SET is_active = 0 WHERE account_num = ?"
            cursor.execute(query_update, (account.account_num,))
            self.connect.commit()

            print(
                f"\n==============================================\n"
                f"🔒 ACCOUNT CLOSED SUCCESSFULLY\n"
                f"Account Number : {account.account_num}\n"
                f"Final Balance  : {account.balance:,.2f} {account.currency}\n"
                f"=============================================="
            )

        except ValidationError as e:
            print(
                f"❌ Structural Validation Error: System record is corrupted. {e.errors()}"
            )
            self.connect.rollback()
        except Exception as err:
            print(f"❌ Failed to close account: {err}")
            self.connect.rollback()