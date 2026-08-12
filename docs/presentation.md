# PyBank — Presentation

> A terminal-based banking system built with clean architecture, Pydantic validation, and SQLite persistence.

---

## Slide 1: Introduction

- **PyBank** is a CLI banking application that demonstrates clean separation of concerns in a compact Python codebase.
- It models classic banking primitives: **register → deposit/withdraw → report**.
- Uses **Pydantic v2** for validation, **SQLite** for persistence, and **Mermaid** for architecture documentation.

```mermaid
graph LR
    A[PyBank] --> B[CLI Layer]
    A --> C[Handler Layer]
    A --> D[Validation Layer]
    A --> E[Persistence Layer]
    style A fill:#6a9fb4,color:#fff
    style B fill:#c792ea,color:#fff
    style C fill:#d29922,color:#000
    style D fill:#8fbf7b,color:#000
    style E fill:#ddd,color:#000
```

---

## Slide 2: System Overview

- Single-process terminal application
- Numbered text menu mapped to `BankAction` enum
- Singleton-wrapped SQLite connection
- WAL journaling enabled for concurrency

```mermaid
mindmap
  root((PyBank))
    CLI
      app.py
      const.py
      enums.py
    Handler
      pybank.py
    Validation
      Pydantic Models
    Persistence
      sqlite_db.py
      Singleton Pattern
```

---

## Slide 3: Layered Architecture

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

---

## Slide 4: Design Patterns

### 1. Singleton — `SqliteDB`

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

### 2. Command / Dispatch — `BankAction` enum

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

---

## Slide 5: Data Models

```mermaid
classDiagram
    class User {
        +int aadhar_num
        +str name
        +EmailStr? email
        +str phone
        +int age
        +str father_name
        +str? address
        +str city
        +float initial_balance
        +datetime created_at
    }
    class Account {
        +int account_num
        +int user_id
        +str account_type
        +float balance
        +str currency
        +bool is_active
        +datetime created_at
    }
    class TransactionRecord {
        +int id
        +int account_num
        +str transaction_type
        +float amount
        +datetime timestamp
    }
    User "1" <-- "1" Account : user_id
    Account "1" --o "*" TransactionRecord : account_num
```

---

## Slide 6: Database Schema

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

## Slide 7: Request Flow — Registration

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

---

## Slide 8: Request Flow — Deposit / Withdraw

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

## Slide 9: Error Handling Strategy

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

---

## Slide 10: Key Takeaways

- **Clean Architecture**: Four layers with strict dependency rules
- **Validation at the Boundary**: Pydantic guards all database writes
- **Shared Connection**: Singleton pattern prevents file lock contention
- **Atomic Transactions**: Every mutating operation commits or rolls back
- **Extensible**: Command dispatch via enum makes adding new operations trivial
