# sql_library_backend
This is a relational database-driven terminal application built using Python 3.12 and SQLite. It moves beyond temporary file storage by utilizing structured SQL tables to manage a library's core logistics—tracking physical book inventory, member profiles, and live borrowing histories in real-time.

## Features
* **Relational Database Integrity:** Enforces database-level `FOREIGN KEY` constraints across tables to prevent orphaned transaction logs.
* **Dynamic Inventory Guard:** Checks real-time copy availability before checking out books, handling atomic decrement/increment updates during loans and returns.
* **Persistent Local Storage:** Uses an embedded SQLite footprint, storing system states inside a reusable `library.db` file.
* **Interactive Shell Interface:** Equipped with a loop-driven Command Line Interface (CLI) bundled with defensive error handling for non-numeric or out-of-bounds user entries.

---

## Database Schema

The relational schema coordinates data transformations across three core tables:

| Books Table (Primary) | Transactions Table (Junction) | Members Table (Primary) |
| :--- | :--- | :--- |
| `book_id` **(PK)** | `transaction_id` **(PK)** | `member_id` **(PK)** |
| `title` | `book_id` **(FK ➔ Books)** | `name` |
| `author` | `member_id` **(FK ➔ Members)** | `join_date` |
| `total_copies` | `borrow_date` | |
| `available_copies` | `return_date` | |

* **PK** = Primary Key | **FK** = Foreign Key
1. **`Books`**: Manages the unique catalog items, total library acquisitions, and real-time floating inventory shelves (`available_copies`).
2. **`Members`**: Maintains registered library cardholder data.
3. **`Transactions`**: Maps actions between `Books` and `Members`, archiving historical date stamps for active borrow statuses and closing updates.
