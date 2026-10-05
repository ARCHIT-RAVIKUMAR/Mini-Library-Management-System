# Obstacle Log

| # | Obstacle | How I solved it |
|---|----------|-----------------|
| 1 | **Testing overdue logic**: a book borrowed today can't be overdue for 14 days. | Gave `borrow_book()` and `return_book()` optional date parameters (default: today), so the demo can back-date loans. |
| 2 | **Tracking history vs. current state**: storing only "who has it now" on each book loses past loans, which the records file needs. | Kept two structures: `books` (current status) and `borrow_log` (one entry per loan, with a `return_date` of `None` while open). |
| 3 | **Silent failures**: borrowing a checked-out book or using a bad ID could just return nothing. | Every function checks its conditions first and prints a specific reason (who has the book, when it's due), and returns True/False. |
| 4 | **Duplicate books and blank input** when adding. | `add_book()` compares title and author case-insensitively and rejects blanks. |
| 5 | **Crash on non-numeric IDs** in the menu (`int("abc")`). | Added `read_id()` that validates with `.isdigit()` before converting. |
| 6 | **Late return wording**: a returned book isn't "overdue" anymore but was still late. | Records file distinguishes `OVERDUE` (still out), `RETURNED` and `RETURNED (LATE)`. |

**Known limitation:** data lives in memory only. The records file is a log, not reloaded on startup (a good next step).
