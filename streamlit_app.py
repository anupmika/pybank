"""
PyBank - Streamlit Web UI
A web interface for the PyBank banking system, deployable on HuggingFace Spaces.
"""

import re
import sqlite3
from datetime import datetime

import streamlit as st
from pydantic import ValidationError

from src.helpers.security import hash_pin, verify_pin
from src.sqlite_db import SqliteDB
from src.validators.models import Account, User

# Initialize database
db = SqliteDB()
conn = db.db_connect()
cursor = conn.cursor()


def main():
    st.set_page_config(
        page_title="PyBank",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🏦 PyBank")
    st.markdown("*A simple banking system web interface*")

    # Sidebar menu
    menu = st.sidebar.selectbox(
        "Select Operation",
        [
            "Home",
            "Open Account",
            "Deposit Money",
            "Withdraw Money",
            "View Balance",
            "View Transaction History",
            "View Account Details",
            "Close Account",
        ],
    )

    if menu == "Home":
        show_home()
    elif menu == "Open Account":
        show_open_account()
    elif menu == "Deposit Money":
        show_deposit()
    elif menu == "Withdraw Money":
        show_withdraw()
    elif menu == "View Balance":
        show_balance()
    elif menu == "View Transaction History":
        show_history()
    elif menu == "View Account Details":
        show_account_details()
    elif menu == "Close Account":
        show_close_account()


def show_home():
    st.header("Welcome to PyBank")
    st.markdown("""
    PyBank is a simple banking system with the following features:

    - 📝 **Open Account** - Register a new customer account with PIN
    - 💰 **Deposit Money** - Add funds to an account
    - 💸 **Withdraw Money** - Withdraw funds with PIN verification
    - 💳 **View Balance** - Check account balance
    - 📜 **View Transaction History** - See all transactions
    - 👤 **View Account Details** - View full customer profile
    - 🔒 **Close Account** - Deactivate an account

    Use the sidebar to navigate through the operations.
    """)


def show_open_account():
    st.header("Open New Account")

    with st.form("open_account_form"):
        col1, col2 = st.columns(2)

        with col1:
            aadhar_num = st.text_input("Aadhar Number (12 digits)", max_chars=12)
            name = st.text_input("Full Name")
            email = st.text_input("Email (optional)")
            phone = st.text_input("Phone Number")
            age = st.number_input("Age", min_value=1, max_value=125, step=1)

        with col2:
            father_name = st.text_input("Father's Name")
            address = st.text_input("Address (optional)")
            city = st.text_input("City")
            initial_balance = st.number_input(
                "Initial Balance (INR)", min_value=0.0, step=100.0
            )
            pin = st.text_input("Set 4-digit PIN", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)

        submitted = st.form_submit_button("Open Account")

        if submitted:
            if not re.fullmatch(r"\d{4}", pin) or pin != confirm_pin:
                st.error("PIN must be exactly 4 digits and both entries must match.")
                return

            user_input = {
                "aadhar_num": aadhar_num,
                "name": name,
                "email": email if email else None,
                "phone": phone,
                "age": age,
                "fatherName": father_name,
                "address": address if address else None,
                "city": city,
                "initialBal": initial_balance,
            }

            try:
                validated_user = User(**user_input)
                user_dict = validated_user.model_dump()
                user_dict["created_at"] = user_dict["created_at"].isoformat()

                cursor.execute(
                    """
                    INSERT INTO users (aadhar_num, name, email, phone, age, father_name, address, city, initial_balance, created_at)
                    VALUES (:aadhar_num, :name, :email, :phone, :age, :father_name, :address, :city, :initial_balance, :created_at)
                    """,
                    user_dict,
                )
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
                account_dict["pin_hash"] = hash_pin(pin)
                account_dict["created_at"] = account_dict["created_at"].isoformat()

                cursor.execute(
                    """
                    INSERT INTO accounts (account_num, user_id, account_type, balance, currency, is_active, created_at, pin_hash)
                    VALUES (:account_num, :user_id, :account_type, :balance, :currency, :is_active, :created_at, :pin_hash)
                    """,
                    account_dict,
                )
                conn.commit()

                st.success(f"""
                **Registration Successful!**

                Dear {validated_user.name}, your account is active.
                Account Number: **{validated_account.account_num}**
                Opening Balance: **{validated_account.balance} {validated_account.currency}**
                """)
            except ValidationError as e:
                st.error("Registration Failed! Correct these issues:")
                for error in e.errors():
                    field = " -> ".join(str(loc) for loc in error["loc"])
                    st.write(f"- {field}: {error["msg"]}")
                conn.rollback()
            except sqlite3.IntegrityError:
                st.error(
                    "Database Error: This Aadhar profile already exists in our system!"
                )
                conn.rollback()


def verify_pin_for_account(account_num, pin):
    cursor.execute(
        "SELECT pin_hash FROM accounts WHERE account_num = ?", (account_num,)
    )
    row = cursor.fetchone()
    if row is None:
        return False, "Account number not found."
    if not row[0]:
        return False, "This account has no PIN."
    if verify_pin(pin, row[0]):
        return True, ""
    return False, "Wrong PIN."


def show_deposit():
    st.header("Deposit Money")

    with st.form("deposit_form"):
        account_num = st.text_input("Account Number")
        amount = st.number_input("Amount to Deposit (INR)", min_value=0.01, step=100.0)
        submitted = st.form_submit_button("Deposit")

        if submitted:
            try:
                # Fetch account
                cursor.execute(
                    "SELECT account_num, user_id, account_type, balance, currency, is_active, created_at FROM accounts WHERE account_num = ?",
                    (account_num,),
                )
                row = cursor.fetchone()
                if row is None:
                    st.error("Account number not found.")
                    return

                account_data = {
                    "account_num": row[0],
                    "user_id": row[1],
                    "account_type": row[2],
                    "balance": row[3] + amount,
                    "currency": row[4],
                    "is_active": bool(row[5]),
                    "created_at": row[6],
                }
                account = Account.model_validate(account_data)
                if not account.is_active:
                    st.error("Cannot deposit into an inactive account.")
                    return

                cursor.execute(
                    "UPDATE accounts SET balance = ? WHERE account_num = ?",
                    (account.balance, account.account_num),
                )
                cursor.execute(
                    "INSERT INTO transactions (account_num, transaction_type, amount, balance_after, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (
                        account.account_num,
                        "deposit",
                        amount,
                        account.balance,
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()

                st.success(f"""
                **Deposit Successful!**
                Account Number: {account.account_num}
                Deposited: +{amount:,.2f} {account.currency}
                Updated Balance: {account.balance:,.2f} {account.currency}
                """)
            except ValidationError as e:
                st.error(f"Transaction Blocked: {e.errors()}")
                conn.rollback()
            except Exception as err:
                st.error(f"Error: {err}")
                conn.rollback()


def show_withdraw():
    st.header("Withdraw Money")

    with st.form("withdraw_form"):
        account_num = st.text_input("Account Number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        amount = st.number_input("Amount to Withdraw (INR)", min_value=0.01, step=100.0)
        submitted = st.form_submit_button("Withdraw")

        if submitted:
            ok, msg = verify_pin_for_account(account_num, pin)
            if not ok:
                st.error(msg)
                return

            try:
                cursor.execute(
                    "SELECT account_num, user_id, account_type, balance, currency, is_active, created_at FROM accounts WHERE account_num = ?",
                    (account_num,),
                )
                row = cursor.fetchone()
                if row is None:
                    st.error("Account number not found.")
                    return

                account_data = {
                    "account_num": row[0],
                    "user_id": row[1],
                    "account_type": row[2],
                    "balance": row[3] - amount,
                    "currency": row[4],
                    "is_active": bool(row[5]),
                    "created_at": row[6],
                }
                account = Account.model_validate(account_data)
                if not account.is_active:
                    st.error("Cannot withdraw from an inactive account.")
                    return

                cursor.execute(
                    "UPDATE accounts SET balance = ? WHERE account_num = ?",
                    (account.balance, account.account_num),
                )
                cursor.execute(
                    "INSERT INTO transactions (account_num, transaction_type, amount, balance_after, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (
                        account.account_num,
                        "withdraw",
                        amount,
                        account.balance,
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()

                st.success(f"""
                **Withdraw Successful!**
                Account Number: {account.account_num}
                Withdrawn: -{amount:,.2f} {account.currency}
                Updated Balance: {account.balance:,.2f} {account.currency}
                """)
            except ValidationError as e:
                st.error(f"Transaction Blocked: {e.errors()}")
                conn.rollback()
            except Exception as err:
                st.error(f"Error: {err}")
                conn.rollback()


def show_balance():
    st.header("View Balance")

    with st.form("balance_form"):
        account_num = st.text_input("Account Number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("View Balance")

        if submitted:
            ok, msg = verify_pin_for_account(account_num, pin)
            if not ok:
                st.error(msg)
                return

            try:
                cursor.execute(
                    "SELECT account_num, user_id, account_type, balance, currency, is_active, created_at FROM accounts WHERE account_num = ?",
                    (account_num,),
                )
                row = cursor.fetchone()
                if row is None:
                    st.error("Account not found.")
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
                st.info(f"""
                **Account Summary**
                Account Number: {account.account_num}
                Account Type: {account.account_type.capitalize()}
                Current Balance: **{account.balance:,.2f} {account.currency}**
                Status: {"🟢 Active" if account.is_active else "🔴 Inactive"}
                """)
            except Exception as err:
                st.error(f"Error: {err}")


def show_history():
    st.header("Transaction History")

    with st.form("history_form"):
        account_num = st.text_input("Account Number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("View History")

        if submitted:
            ok, msg = verify_pin_for_account(account_num, pin)
            if not ok:
                st.error(msg)
                return

            cursor.execute(
                "SELECT transaction_type, amount, balance_after, timestamp FROM transactions WHERE account_num = ? ORDER BY timestamp DESC",
                (account_num,),
            )
            transactions = cursor.fetchall()
            if not transactions:
                st.info("No transactions found for this account.")
                return

            data = []
            for idx, txn in enumerate(transactions, start=1):
                txn_type, amount, balance_after, timestamp = txn
                data.append({
                    "#": idx,
                    "Type": txn_type.capitalize(),
                    "Amount": f"{'+' if txn_type == "deposit" else "-"}{amount:,.2f}",
                    "Balance After": f"{balance_after:,.2f}",
                    "Timestamp": timestamp,
                })
            st.table(data)


def show_account_details():
    st.header("View Account Details")

    with st.form("details_form"):
        account_num = st.text_input("Account Number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("View Details")

        if submitted:
            ok, msg = verify_pin_for_account(account_num, pin)
            if not ok:
                st.error(msg)
                return

            cursor.execute(
                """
                SELECT u.aadhar_num, u.name, u.email, u.phone, u.age, u.father_name, u.address, u.city,
                       a.account_num, a.user_id, a.account_type, a.balance, a.currency, a.is_active
                FROM accounts a INNER JOIN users u ON a.user_id = u.id WHERE a.account_num = ?
                """,
                (account_num,),
            )
            row = cursor.fetchone()
            if row is None:
                st.error("No profile found for this account.")
                return

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Customer Details")
                st.write(f"**Name:** {row[1]}")
                st.write(f"**Father's Name:** {row[5]}")
                st.write(f"**Aadhar Number:** {row[0]}")
                st.write(f"**Age:** {row[4]}")
                st.write(f"**City:** {row[7]}")
                st.write(f"**Phone:** {row[3]}")
                st.write(f"**Email:** {row[2] or "N/A"}")
                st.write(f"**Address:** {row[6] or "N/A"}")
            with col2:
                st.subheader("Account Details")
                st.write(f"**Account Number:** {row[8]}")
                st.write(
                    f"**Account Type:** {row[10].capitalize() if row[10] else "Savings"}"
                )
                st.write(f"**Currency:** {row[12]}")
                st.write(f"**Balance:** {row[11]:,.2f} {row[12]}")
                st.write(f"**Status:** {"🟢 Active" if row[13] else "🔴 Inactive"}")


def show_close_account():
    st.header("Close Account")

    with st.form("close_form"):
        account_num = st.text_input("Account Number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Close Account")

        if submitted:
            ok, msg = verify_pin_for_account(account_num, pin)
            if not ok:
                st.error(msg)
                return

            cursor.execute(
                "SELECT is_active, balance, currency FROM accounts WHERE account_num = ?",
                (account_num,),
            )
            row = cursor.fetchone()
            if row is None:
                st.error("Account not found.")
                return
            if not row[0]:
                st.error("Account is already closed.")
                return

            cursor.execute(
                "UPDATE accounts SET is_active = 0 WHERE account_num = ?",
                (account_num,),
            )
            conn.commit()
            st.success(
                f"Account {account_num} closed successfully. Final Balance: {row[1]:,.2f} {row[2]}"
            )


if __name__ == "__main__":
    main()
