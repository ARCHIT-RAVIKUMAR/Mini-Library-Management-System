"""Mini Library Management System (standard library only).

Usage:
    python library.py          -> interactive menu
    python library.py --demo   -> scripted demo that also writes borrowing_records.txt
"""
import sys
from datetime import date, timedelta

LOAN_DAYS = 14                      # how long a book may be kept
SAMPLE_FILE = "sample_books.txt"
RECORDS_FILE = "borrowing_records.txt"

# ---------- Step 1: data structures ----------
# books: list of dicts. borrow_log: list of dicts (one per loan, open or closed).
books = []
borrow_log = []


# ---------- Step 2: core functions ----------
def add_book(title, author):
    """Add a book and return it. Rejects blank fields and exact duplicates."""
    title, author = title.strip(), author.strip()
    if not title or not author:
        print("  ! Title and author are required.")
        return None
    for b in books:
        if b["title"].lower() == title.lower() and b["author"].lower() == author.lower():
            print(f"  ! '{title}' by {author} is already in the library (ID {b['id']}).")
            return None
    book = {"id": len(books) + 1, "title": title, "author": author,
            "available": True, "borrower": None, "due_date": None}
    books.append(book)
    return book


def load_sample_books(path=SAMPLE_FILE):
    """Load 'title | author' lines from a text file."""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "|" in line:
                    title, author = line.split("|", 1)
                    add_book(title, author)
    except FileNotFoundError:
        print(f"  ! Sample file '{path}' not found; starting with an empty library.")


def find_book_by_id(book_id):
    for b in books:
        if b["id"] == book_id:
            return b
    return None


def search_books(query):
    """Case-insensitive search on title or author."""
    q = query.strip().lower()
    return [b for b in books if q in b["title"].lower() or q in b["author"].lower()]


# ---------- Step 3: unavailable & overdue handling ----------
def borrow_book(book_id, borrower, borrow_date=None):
    """Lend a book. Returns True on success; prints a clear reason on failure."""
    borrow_date = borrow_date or date.today()
    book = find_book_by_id(book_id)
    if book is None:
        print(f"  ! No book with ID {book_id}.")
        return False
    if not borrower.strip():
        print("  ! Borrower name is required.")
        return False
    if not book["available"]:
        print(f"  ! '{book['title']}' is already checked out by {book['borrower']} "
              f"(due {book['due_date']}).")
        return False
    book["available"] = False
    book["borrower"] = borrower.strip()
    book["due_date"] = borrow_date + timedelta(days=LOAN_DAYS)
    borrow_log.append({"book_id": book["id"], "title": book["title"],
                       "borrower": book["borrower"], "borrow_date": borrow_date,
                       "due_date": book["due_date"], "return_date": None})
    print(f"  + {book['borrower']} borrowed '{book['title']}'. Due {book['due_date']}.")
    return True


def return_book(book_id, return_date=None):
    """Return a book; reports if it was late."""
    return_date = return_date or date.today()
    book = find_book_by_id(book_id)
    if book is None:
        print(f"  ! No book with ID {book_id}.")
        return False
    if book["available"]:
        print(f"  ! '{book['title']}' is not checked out, nothing to return.")
        return False
    for rec in borrow_log:
        if rec["book_id"] == book_id and rec["return_date"] is None:
            rec["return_date"] = return_date
    days_late = (return_date - book["due_date"]).days
    msg = f"  + '{book['title']}' returned by {book['borrower']}."
    if days_late > 0:
        msg += f" LATE by {days_late} day(s)."
    print(msg)
    book["available"], book["borrower"], book["due_date"] = True, None, None
    return True


def get_overdue_books(today=None):
    """Books currently out whose due date has passed."""
    today = today or date.today()
    return [b for b in books if not b["available"] and b["due_date"] < today]


def print_overdue(today=None):
    today = today or date.today()
    overdue = get_overdue_books(today)
    if not overdue:
        print("  No overdue books.")
        return
    for b in overdue:
        print(f"  ! OVERDUE: '{b['title']}' - {b['borrower']}, due {b['due_date']} "
              f"({(today - b['due_date']).days} days late)")


def library_summary():
    total = len(books)
    out = sum(1 for b in books if not b["available"])
    return {"total": total, "borrowed": out, "available": total - out,
            "overdue": len(get_overdue_books())}


def print_summary():
    s = library_summary()
    print(f"  Total books: {s['total']} | Available: {s['available']} | "
          f"Borrowed: {s['borrowed']} | Overdue: {s['overdue']}")


def print_books(items):
    if not items:
        print("  No books found.")
    for b in items:
        status = "Available" if b["available"] else f"Out: {b['borrower']} (due {b['due_date']})"
        print(f"  [{b['id']}] {b['title']} by {b['author']} - {status}")


# ---------- Step 4: persistence ----------
def save_records(path=RECORDS_FILE):
    """Write the full lending log plus a summary to a text file."""
    s = library_summary()
    with open(path, "w", encoding="utf-8") as f:
        f.write("LIBRARY BORROWING RECORDS\n")
        f.write(f"Generated: {date.today()}\n")
        f.write(f"Loan period: {LOAN_DAYS} days\n")
        f.write("=" * 60 + "\n")
        for r in borrow_log:
            if r["return_date"]:
                status = "RETURNED " + str(r["return_date"])
                if r["return_date"] > r["due_date"]:
                    status += " (LATE)"
            elif r["due_date"] < date.today():
                status = "OVERDUE"
            else:
                status = "ON LOAN"
            f.write(f"{r['title']} | {r['borrower']} | borrowed {r['borrow_date']} | "
                    f"due {r['due_date']} | {status}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total: {s['total']}  Available: {s['available']}  "
                f"Borrowed: {s['borrowed']}  Overdue: {s['overdue']}\n")
    print(f"  Records saved to {path}")


# ---------- Interface ----------
def read_id(prompt):
    raw = input(prompt).strip()
    if raw.isdigit():
        return int(raw)
    print("  ! Please enter a numeric book ID.")
    return None


def menu():
    options = """
1) List books      2) Search        3) Add book
4) Borrow          5) Return        6) Overdue
7) Summary         8) Save & quit"""
    while True:
        print(options)
        choice = input("Choose: ").strip()
        if choice == "1":
            print_books(books)
        elif choice == "2":
            print_books(search_books(input("Search term: ")))
        elif choice == "3":
            b = add_book(input("Title: "), input("Author: "))
            if b:
                print(f"  + Added with ID {b['id']}.")
        elif choice == "4":
            bid = read_id("Book ID: ")
            if bid is not None:
                borrow_book(bid, input("Borrower name: "))
        elif choice == "5":
            bid = read_id("Book ID: ")
            if bid is not None:
                return_book(bid)
        elif choice == "6":
            print_overdue()
        elif choice == "7":
            print_summary()
        elif choice == "8":
            save_records()
            break
        else:
            print("  ! Invalid choice.")


def demo():
    """Scripted run using back-dated loans so overdue logic is visible."""
    today = date.today()
    print("== Search 'orwell' ==")
    print_books(search_books("orwell"))
    print("\n== Borrowing ==")
    borrow_book(1, "Asha", today - timedelta(days=20))     # overdue
    borrow_book(2, "Ravi", today - timedelta(days=3))
    borrow_book(4, "Meena", today - timedelta(days=30))    # overdue, returned late
    borrow_book(7, "Karan", today - timedelta(days=1))
    print("\n== Edge cases ==")
    borrow_book(2, "Divya")        # already out
    borrow_book(99, "Divya")       # bad ID
    return_book(3)                 # not checked out
    add_book("Dune", "Frank Herbert")  # duplicate
    print("\n== Returning ==")
    return_book(4)
    print("\n== Overdue ==")
    print_overdue()
    print("\n== Summary ==")
    print_summary()
    save_records()


if __name__ == "__main__":
    load_sample_books()
    if "--demo" in sys.argv:
        demo()
    else:
        print("Welcome to the Mini Library System")
        menu()
