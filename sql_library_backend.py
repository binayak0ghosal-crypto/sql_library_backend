import sqlite3
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def setup_database():
    """Connects to SQLite, enables foreign keys, and creates tables."""
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Enforce foreign key constraints in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create Books Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
    ''')

    # Create Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    ''')

    # Create Transactions Table (with Foreign Keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            borrow_date DATE NOT NULL,
            return_date DATE,
            FOREIGN KEY (book_id) REFERENCES Books(book_id),
            FOREIGN KEY (member_id) REFERENCES Members(member_id)
        )
    ''')
    
    conn.commit()
    return conn

# ==========================================
# 2. CORE FUNCTIONS
# ==========================================
def add_dummy_data(conn):
    """Populates the database with some initial data for testing."""
    cursor = conn.cursor()
    
    # Check if data already exists to avoid duplicates on multiple runs
    cursor.execute("SELECT COUNT(*) FROM Books")
    if cursor.fetchone()[0] == 0:
        # Insert Books
        cursor.execute("INSERT INTO Books (title, author, total_copies, available_copies) VALUES ('1984', 'George Orwell', 3, 3)")
        cursor.execute("INSERT INTO Books (title, author, total_copies, available_copies) VALUES ('Dune', 'Frank Herbert', 2, 2)")
        
        # Insert Members
        cursor.execute("INSERT INTO Members (name, join_date) VALUES ('Alice Smith', '2023-01-15')")
        cursor.execute("INSERT INTO Members (name, join_date) VALUES ('Bob Jones', '2023-06-22')")
        
        conn.commit()
        print("Dummy data added successfully.\n")

def view_available_books(conn):
    """Fetches and prints all books currently available."""
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, author, available_copies FROM Books WHERE available_copies > 0")
    books = cursor.fetchall()
    
    print("\n--- Available Books ---")
    for book in books:
        print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]} | Available: {book[3]}")
    print("-" * 23 + "\n")

def borrow_book(conn, member_id, book_id):
    """Handles the logic of a user checking out a book."""
    cursor = conn.cursor()
    
    # Check if the book is actually available
    cursor.execute("SELECT available_copies, title FROM Books WHERE book_id = ?", (book_id,))
    result = cursor.fetchone()
    
    if not result:
        print("Error: Book does not exist.")
        return
        
    available_copies, title = result
    
    if available_copies <= 0:
        print(f"Sorry, '{title}' is currently out of stock.\n")
        return
        
    # Proceed with transaction: Decrease available copies
    cursor.execute('UPDATE Books SET available_copies = available_copies - 1 WHERE book_id = ?', (book_id,))
    
    # Log the transaction
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO Transactions (book_id, member_id, borrow_date) VALUES (?, ?, ?)', (book_id, member_id, today))
    
    conn.commit()
    print(f"Success! Member ID {member_id} borrowed '{title}'.\n")

def return_book(conn, transaction_id):
    """Handles a book return."""
    cursor = conn.cursor()
    
    # Get the book_id from the transaction
    cursor.execute("SELECT book_id, return_date FROM Transactions WHERE transaction_id = ?", (transaction_id,))
    result = cursor.fetchone()
    
    if not result:
        print("Error: Transaction not found.")
        return
        
    book_id, return_date = result
    
    if return_date is not None:
        print("Error: This book has already been returned.\n")
        return
        
    # Update transaction with return date
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('UPDATE Transactions SET return_date = ? WHERE transaction_id = ?', (today, transaction_id))
    
    # Increase available copies
    cursor.execute('UPDATE Books SET available_copies = available_copies + 1 WHERE book_id = ?', (book_id,))
    
    conn.commit()
    print(f"Success! Transaction {transaction_id} closed. Book returned.\n")

# ==========================================
# 3. INTERACTIVE MENU EXECUTION
# ==========================================
if __name__ == "__main__":
    # Initialize DB and data
    db_connection = setup_database()
    add_dummy_data(db_connection)
    
    while True:
        print("=== LIBRARY MANAGEMENT MENU ===")
        print("1. View Available Books")
        print("2. Borrow a Book")
        print("3. Return a Book")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            view_available_books(db_connection)
            
        elif choice == '2':
            try:
                mem_id = int(input("Enter Member ID (Try 1 or 2): "))
                bk_id = int(input("Enter Book ID (Try 1 or 2): "))
                borrow_book(db_connection, mem_id, bk_id)
            except ValueError:
                print("Please enter valid numeric IDs.\n")
                
        elif choice == '3':
            try:
                tx_id = int(input("Enter Transaction ID to return (e.g., 1): "))
                return_book(db_connection, tx_id)
            except ValueError:
                print("Please enter a valid numeric Transaction ID.\n")
                
        elif choice == '4':
            print("Exiting system. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please choose between 1 and 4.\n")
            
    db_connection.close()