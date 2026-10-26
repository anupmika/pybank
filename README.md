# 💰 PyBank

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://anupmika-pybank.streamlit.app/)
[![Python](https://img.shields.io/badge/python-3.12+-blue?logo=python)](https://www.python.org/)
[![codecov](https://codecov.io/github/anupmika/pybank/graph/badge.svg?token=976A6T3HSC)](https://codecov.io/github/anupmika/pybank)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

> 🏦 **A modern dual-interface Python banking system** showcasing clean architecture, OOP, Pydantic v2 validation, SQLite persistence, secure PIN authentication, and seamless CLI + Web experiences.

PyBank lets you register customers, open secured bank accounts, perform deposits, withdrawals, transfers, close accounts, and view detailed transaction histories with passbook-style statements. Built for learning and demonstration of production-grade patterns in Python.

> **Status:** 🚀 Early-stage educational project. Explore the [Architecture Guide](docs/architecture.md) and [User Guide](docs/user-guide.md) for deeper insights.

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Project Structure](#️-project-structure)
- [🚀 Getting Started](#-getting-started)
- [💻 Usage](#-usage)
- [🗄️ Data Model](#️-data-model)
- [📚 Documentation](#-documentation)
- [🛠️ Development](#️-development)
- [📜 License](#-license)

## ✨ Features

- 🖥️ **Dual Interface** – Intuitive terminal CLI (`main.py`) and feature-rich Streamlit web UI (`streamlit_app.py`)
- 👤 **Smart Account Registration** – Captures Aadhaar, personal details, and sets up secure PIN protection
- 🔐 **Secure Authentication** – 4-digit PINs hashed with **PBKDF2-HMAC-SHA256** using unique salts
- 💵 **Deposits & Withdrawals** – Real-time balance updates with PIN verification and validation
- 💸 **Fund Transfers** – Secure transfers between accounts with atomic transactions and rollback on errors
- 🔒 **Account Management** – Close/deactivate accounts with PIN verification
- 📊 **Balance & Profile Views** – Quick balance checks and comprehensive customer/account profiles
- 📜 **Transaction History** – Passbook-style statement with running balances and timestamps
- ✅ **Robust Validation** – Pydantic v2 validates all inputs at the trust boundary
- 🗃️ **Reliable Persistence** – SQLite with WAL journaling, schema auto-creation, and migrations
- 🏛️ **Clean Design** – Singleton connection manager, enum-based routing, and layered architecture
- 🔄 **Transactional Integrity** – Commits on success, automatic rollback on errors

## 🏗️ Project Structure

```text
pybank/
├── main.py              # 🚪 CLI application entry point
├── streamlit_app.py     # 🌐 Streamlit web UI
├── pyproject.toml       # 📦 Project metadata & dependencies (uv)
├── justfile             # ⚡ Task recipes
├── README.md            # 📖 Project documentation
├── LICENSE              # ⚖️ Apache-2.0 License
├── db/                  # 💾 SQLite database (auto-created)
├── docs/                # 📚 Documentation
│   ├── architecture.md
│   ├── components.md
│   ├── presentation.md
│   └── user-guide.md
├── src/
│   ├── app.py           # 🔄 CLI loop & BankAction router
│   ├── const.py         # 📋 DB config & menu constants
│   ├── enums.py         # 🔢 BankAction enumeration
│   ├── sqlite_db.py     # 🗄️ Singleton SQLite connection + schema
│   ├── validators/
│   │   └── models.py    # 🛡️ Pydantic models
│   ├── handlers/
│   │   └── pybank.py    # 💼 Core banking operations
│   ├── helpers/
│   │   ├── design.py    # 🧬 SingletonMeta
│   │   └── security.py  # 🔐 PIN hashing
│   └── utils/
│       └── cli_utils.py # 🎨 Colored output
└── tests/               # 🧪 Test suite
```

## 🚀 Getting Started

### Prerequisites

- 🐍 [Python](https://www.python.org/) 3.12+
- ⚡ [uv](https://docs.astral.sh/uv/) (recommended)

### Installation

```bash
git clone https://github.com/anupmika/pybank.git
cd pybank
uv sync --no-cache
```

## 💻 Usage

### CLI Interface

```bash
python main.py
# or
uv run main.py
# or
just run
```

### Web Interface

```bash
streamlit run streamlit_app.py
# or
uv run streamlit run streamlit_app.py
# or
just dev-ui
```

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

See [User Guide](docs/user-guide.md) for detailed walkthroughs.

## 🗄️ Data Model

### `users`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| id | INTEGER | PK (autoincrement) | Primary key |
| aadhar_num | TEXT | UNIQUE NOT NULL | 12-digit Aadhaar |
| name | TEXT | NOT NULL | Full name |
| email | TEXT | NULL | Optional |
| phone | TEXT | NOT NULL | Phone number |
| age | INTEGER | NOT NULL | Age |
| father_name | TEXT | NOT NULL | Father's name |
| address | TEXT | NULL | Optional |
| city | TEXT | NOT NULL | City |
| initial_balance | REAL | NOT NULL | Initial deposit |
| created_at | TEXT | NOT NULL (ISO) | Created timestamp |

### `accounts`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| account_num | INTEGER | UNIQUE NOT NULL | 500000 + user_id |
| user_id | INTEGER | FK -> users(id) NOT NULL | User reference |
| account_type | TEXT | DEFAULT 'savings' | Account type |
| balance | REAL | DEFAULT 0 | Current balance |
| currency | TEXT | DEFAULT 'INR' | Currency |
| is_active | INTEGER | DEFAULT 1 | 1 active, 0 inactive |
| created_at | TEXT | NOT NULL (ISO) | Created timestamp |
| pin_hash | TEXT | NULL | PBKDF2-HMAC-SHA256 hash |

### `transactions`

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| id | INTEGER | PK (autoincrement) | Primary key |
| account_num | INTEGER | FK -> accounts(account_num) | Account reference |
| transaction_type | TEXT | NOT NULL | deposit/withdraw/transfer_in/transfer_out |
| amount | REAL | NOT NULL | Amount |
| balance_after | REAL | NOT NULL | Balance after tx |
| timestamp | TEXT | NOT NULL (ISO) | Timestamp |

## 📚 Documentation

| Document | Description |
| --- | --- |
| [Architecture Guide](docs/architecture.md) | Design patterns, layers, and flows |
| [Component Reference](docs/components.md) | Module/class/function details |
| [User Guide](docs/user-guide.md) | Step-by-step usage for CLI and web |
| [Presentation](docs/presentation.md) | Project presentation and diagrams |

## 🛠️ Development

```bash
just test      # Run tests
just coverage  # Run with coverage
just sync      # Install deps
just run       # CLI app
just dev-ui    # Streamlit app
just clean     # Clean artifacts
```

## 📜 License

Licensed under the [Apache License 2.0](LICENSE). Made with ❤️ and Python 💰
