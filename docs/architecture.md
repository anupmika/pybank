# Architecture Guide

PyBank is a small but well-layered terminal banking application. This document
explains how the system is organized, the design patterns it uses, and how data
and control flow between the layers.

---

## Table of Contents

| Section |
| --- |
| [System Overview](#system-overview) |
| [Layered Architecture](#layered-architecture) |
| [Design Patterns](#design-patterns) |
| [Request Flow (Sequence)](#request-flow-sequence) |
| [Database Schema](#database-schema) |
| [Error Handling Strategy](#error-handling-strategy) |

---

## System Overview

PyBank runs as a single-process CLI application. The user interacts through a
numbered text menu; each selection is mapped to a `BankAction` enum value and
dispatched to the corresponding method on the `PyBank` handler. All persistence
is handled by a Singleton-wrapped SQLite connection.

### Goals

- Demonstrate clean separation of concerns in a compact codebase.
- Show how Pydantic validation guards the database trust boundary.
- Model the classic banking primitives: **register → deposit/withdraw → report**.

---

## Layered Architecture

The codebase is split into four logical layers. Each layer depends only on the
layers below it (dependency rule flows downward).

```mermaid
flowchart TD
    CLI["CLI Layer<br/>app.py, const.py, enums.py"]
    Handler["Handler Layer<br/>handlers/pybank.py"]
    Validation["Validation Layer<br/>validators/models.py"]
    Persistence["Persistence Layer<br/>sqlite_db.py, helpers/design.py"]
    External["External<br/>SQLite on disk"]

    CLI -->|dispatches BankAction| Handler
    Handler -->|validates data| Validation
    Handler -->|commits/queries| Persistence
    Persistence -->|connection| External

    classDef cli fill:#6a9fb4,color:#fff
    classDef handler fill:#c792ea,color:#fff
    classDef validation fill:#d29922,color:#000
    classDef persistence fill:#8fbf7b,color:#000
    classDef external fill:#ddd,color:#000

    class CLI cli
    class Handler handler
    class Validation validation
    class Persistence persistence
    class External external
```

### Layer Descriptions

| Layer | Files | Responsibility |
| --- | --- | --- |
| **CLI** | `app.py`, `const.py`, `enums.py` | Renders the menu, reads the user's choice, and routes to the handler. No business logic. |
| **Handler** | `handlers/pybank.py` | The `PyBank` class orchestrates the banking operations: input collection, validation, SQL execution, and user-facing output. |
| **Validation** | `validators/models.py` | Pydantic models (`User`, `Account`, `TransactionRecord`) that enforce schema rules and field aliases. |
| **Persistence** | `sqlite_db.py`, `helpers/design.py` | Singleton-gated SQLite connection factory plus one-time schema creation. |

---

## Design Patterns

### 1. Singleton — `SqliteDB`

A single database connection (with WAL journaling) is shared across the entire
application lifetime. This avoids file-level lock contention and guarantees the
schema is created exactly once.

```mermaid
classDiagram
    class SingletonMeta {
        -_instances: dict
        +__call__() object
    }
    class SqliteDB {
        -_conn?
        +db_connect()~conn~
    }
    SingletonMeta <|-- SqliteDB : metaclass
```

**Implementation**: `src/helpers/design.py` defines the `SingletonMeta`
metaclass, and `src/sqlite_db.py` applies it to `SqliteDB`.

### 2. Command / Dispatch — `BankAction` enum

The CLI loop maps the user's integer choice to a `BankAction` enum member, then
uses a `match` statement to invoke the corresponding handler. This is a
lightweight variant of the Command pattern — each case is an implicit command.

```mermaid
stateDiagram-v2
    [*] --> ShowMenu
    ShowMenu --> ParseChoice: read int
    ParseChoice --> Dispatch: BankAction match
    Dispatch --> OpenAccount: 1
    Dispatch --> Deposit: 2
    Dispatch --> Withdraw: 3
    Dispatch --> ViewBalance: 4
    Dispatch --> ViewHistory: 5
    Dispatch --> CloseAccount: 6
    Dispatch --> ViewAccount: 7
    Dispatch --> Exit: 8
    OpenAccount --> ShowMenu
    Deposit --> ShowMenu
    Withdraw --> ShowMenu
    ViewBalance --> ShowMenu
    ViewHistory --> ShowMenu
    CloseAccount --> ShowMenu
    ViewAccount --> ShowMenu
    Exit --> [*]
```

### 3. Data Transfer Object — Pydantic Models

`User`, `Account`, and `TransactionRecord` are validated DTOs. They decouple the
raw user input (which uses camelCase aliases like `fatherName`, `accountNum`)
from the snake_case database columns. Pydantic also provides `model_dump()` for
parameterised SQL insertion.

---

## Request Flow (Sequence)

### Registration Sequence

The following diagram shows how a new customer account is created end-to-end.

```mermaid
sequenceDiagram
    participant User
    participant App as app.py (CLI)
    participant Bank as PyBank handler
    participant UserModel as User (Pydantic)
    participant AccModel as Account (Pydantic)
    participant DB as SqliteDB

    User->>App: choose 1 (Open Account)
    App->>Bank: register_account()
    Bank->>User: prompt for aadhar, name, ...
    User->>Bank: submit raw input
    Bank->>UserModel: User(**input)
    alt validation success
        User->>AccModel: Account(accountNum = 500000 + id)
        Bank->>DB: connect()
        DB->>DB: INSERT INTO users
        DB->>DB: INSERT INTO accounts
        DB-->>Bank: lastrowid
        Bank->>User: print success banner
    else ValidationError
        User->>Bank: print field errors
        Bank->>DB: rollback()
    end
```

### Transaction Sequence (Deposit / Withdraw)

```mermaid
flowchart TD
    A[User selects Deposit/Withdraw] --> B[Read account number + amount]
    B --> C[SELECT row BY account_num]
    C --> D{Row found?}
    D -- No --> Z[Print 'account not found']
    D -- Yes --> E[Parse amount to float]
    E --> F{Amount valid?}
    F -- No --> Z2[Print 'invalid amount']
    F -- Yes --> G[Account.model_validate]
    G --> H{Is active?}
    H -- No --> Z3[Print 'inactive account']
    H -- Yes --> I[Compute new balance]
    I --> J[UPDATE accounts SET balance]
    J --> K[commit]
    K --> L[Print transaction summary]
    K -->|exception| RB[rollback]
```

---

## Database Schema

The full schema is created in `SqliteDB.db_connect()` via
`conn.executescript(...)`. There are currently two tables plus an implicit
`id` primary key on `users`.

```mermaid
erDiagram
    USERS {
        integer id PK "autoincrement"
        text aadhar_num "UNIQUE NOT NULL"
        text name "NOT NULL"
        text email "nullable"
        text phone "NOT NULL"
        integer age "NOT NULL"
        text father_name "NOT NULL"
        text address "nullable"
        text city "NOT NULL"
        real initial_balance "NOT NULL"
        text created_at "NOT NULL"
    }
    ACCOUNTS {
        integer account_num "UNIQUE NOT NULL"
        integer user_id FK "NOT NULL"
        text account_type "default savings"
        real balance "default 0"
        text currency "default INR"
        integer is_active "default 1"
        text created_at "NOT NULL"
    }
    USERS ||--o{ ACCOUNTS : "user_id"
```

---

## Error Handling Strategy

PyBank applies errors at three layers:

```mermaid
flowchart LR
    Input[Raw CLI input] --> Val{Pydantic<br/>ValidationError}
    Val -- caught --> Msg1[Print field-level<br/>error list]
    Val -- success --> DB{sqlite3.<br/>IntegrityError}
    DB -- caught --> Msg2[Print integrity error<br/>+ rollback]
    DB -- success --> Msg3[Print success banner]
    DB -- other --> Msg4[Print generic<br/>error + rollback]

    classDef node fill:#f0f0f0,stroke:#333
    class Input,Val,DB,Msg1,Msg2,Msg3,Msg4 node
```

| Exception type | Where | Behaviour |
| --- | --- | --- |
| `ValueError` | `app.py` menu parse | Reprints the menu; user re-enters. |
| `pydantic.ValidationError` | handler methods | Lists every invalid field; rolls back the DB transaction. |
| `sqlite3.IntegrityError` | `register_account` | Reports the duplicate Aadhaar; rollback. |
| generic `Exception` | all I/O methods | Prints the error and rolls back if a transaction is open. |
