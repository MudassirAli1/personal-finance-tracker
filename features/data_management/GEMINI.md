
# Day 6: Data Management & Portability

## Today's Goal
Enable users to export their financial data and import it, ensuring data portability and backup capabilities.

## Learning Focus
- Data serialization (CSV, JSON)
- File I/O operations
- Data validation and error handling during import
- User-friendly data export options

## Fintech Concepts
- **Data Portability**: The ability for users to move their data from one service to another.
- **Data Backup & Restore**: Creating a copy of data that can be used to restore the original in case of data loss.
- **Data Integrity**: Ensuring the accuracy and consistency of data.

## Features to Build

### 1. Export Transactions
- **Formats**: CSV and JSON.
- **Options**:
    - Export all time data.
    - Export data for the current month.
    - Export data for a specific year.
- **File Naming**: `transactions_export_YYYY-MM-DD.csv` or `.json`.
- **Content**: The exported file should contain all transaction details (timestamp, type, category, description, amount).

### 2. Import Transactions
- **Formats**: CSV and JSON.
- **Process**:
    1. Ask the user for the file path.
    2. Validate the file format and structure.
    3. Read the data and parse transactions.
    4. **Avoid Duplicates**: Check if a transaction with the same timestamp and amount already exists before importing.
    5. Provide a summary of the import (e.g., "Successfully imported 50 transactions, skipped 5 duplicates.").
- **Error Handling**: Gracefully handle malformed files or rows.

### 3. Backup & Restore
- **Backup**:
    - Create a single backup file (e.g., `finance_tracker_backup_YYYY-MM-DD.json`).
    - This file should contain both transactions and budgets.
- **Restore**:
    - Ask the user for the backup file path.
    - **Warning**: Clearly state that restoring will overwrite existing data.
    - Wipe current `transactions.txt` and `budgets.txt`.
    - Restore transactions and budgets from the backup file.

## Success Criteria

✅ Can export all transactions to CSV.
✅ Can export monthly transactions to JSON.
✅ Can import transactions from a CSV file.
✅ Can import transactions from a JSON file, skipping duplicates.
✅ Can create a full backup of all data (transactions and budgets).
✅ Can restore data from a backup file, overwriting existing data.
✅ Handles file errors and invalid data gracefully.
