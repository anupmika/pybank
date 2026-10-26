# User Guide

This guide walks through every PyBank operation for both CLI and Streamlit interfaces.

## Table of Contents

- [Main Menu (CLI)](#main-menu-cli)
- [1. Open Account](#1-open-account)
- [2. Deposit Money](#2-deposit-money)
- [3. Withdraw Money](#3-withdraw-money)
- [4. View Balance](#4-view-balance)
- [5. View History](#5-view-history)
- [6. Close Account](#6-close-account)
- [7. View Account](#7-view-account)
- [8. Transfer Money](#8-transfer-money)
- [9. Close App](#9-close-app)
- [Streamlit Web UI](#streamlit-web-ui)
- [Tips & Troubleshooting](#tips--troubleshooting)

## Main Menu (CLI)

```text
----------------------
|       PyBank       |
----------------------
| 1 |  Open Account  |
----------------------
| 2 | Deposite Money |
----------------------
| 3 | Withdraw Money |
----------------------
| 4 |  View Balance  |
----------------------
| 5 |  View History  |
----------------------
| 6 | Close  Account |
----------------------
| 7 | View   Account |
----------------------
| 8 | Transfer Money |
----------------------
| 9 |   Close  App   |
----------------------
```

## 1. Open Account

Register a new customer and create an account with PIN protection.

**Inputs:**

- Aadhar Number (12 digits, no dashes)
- Full Name
- Email (optional)
- Phone Number
- Age
- Father's Name
- Address (optional)
- City
- Initial Balance
- 4-digit PIN and confirmation

**Validation:** Pydantic enforces formats; PIN must be exactly 4 digits and match.

**Result:** Displays account number (`500000 + user_id`), opening balance, and success message.

## 2. Deposit Money

Add funds to an account.

**Steps:**

1. Enter Account Number
2. Enter amount to deposit (must be > 0)
3. Balance updates and transaction recorded

**Notes:** Deposits don't require PIN verification in the current implementation; transactions are logged.

## 3. Withdraw Money

Withdraw funds with PIN protection.

**Steps:**

1. Enter Account Number
2. Enter 4-digit PIN (up to 3 attempts)
3. Enter amount to withdraw (> 0)
4. Sufficient balance required; account must be active
5. Balance updated, transaction recorded

## 4. View Balance

Check current balance securely.

**Steps:**

1. Enter Account Number
2. Enter PIN (up to 3 attempts)
3. View account summary with status

## 5. View History

View passbook-style transaction history.

**Steps:**

1. Enter Account Number
2. Enter PIN (up to 3 attempts)
3. See all transactions with type, amount, balance after, and timestamp in chronological order

## 6. Close Account

Deactivate an account (soft close).

**Steps:**

1. Enter Account Number
2. Enter PIN (up to 3 attempts)
3. Account marked inactive; further transactions may be restricted

## 7. View Account

View full customer profile and account details.

**Steps:**

1. Enter Account Number
2. Enter PIN (up to 3 attempts)
3. Displays personal details, account metrics, and status

## 8. Transfer Money

Transfer funds between two accounts securely.

**Steps:**

1. Enter Source Account Number
2. Enter Source Account PIN (up to 3 attempts)
3. Enter Destination Account Number (must be different)
4. Enter amount to transfer (> 0)
5. Both accounts must exist and be active; sufficient balance required
6. Funds debited from source, credited to destination; both `transfer_out` and `transfer_in` transactions recorded atomically

**Notes:** Transfer is atomic (committed on success, rolled back on error).

## 9. Close App

Exit the CLI application.

## Streamlit Web UI

Launch with `streamlit run streamlit_app.py`. Sidebar menu includes:

- Home
- Open Account
- Deposit Money
- Withdraw Money
- View Balance
- View Transaction History
- View Account Details
- Transfer Money
- Close Account

All operations mirror CLI functionality with form-based inputs and interactive feedback.

## Tips & Troubleshooting

- **Database location:** `db/pybank.db` (auto-created)
- **PIN security:** Never share your 4-digit PIN. 3 failed attempts block access.
- **Account number:** Remember `500000 + your user ID`
- **Validation errors:** Fix inputs as indicated by Pydantic messages
- **Duplicates:** Aadhaar must be unique per registration
- **Inactive accounts:** Closed accounts cannot perform transactions
