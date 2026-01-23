import csv
import json
from datetime import datetime
from rich.console import Console

from database.utils import load_all_transactions, load_budgets, TRANSACTIONS_FILE, BUDGETS_FILE

console = Console()

def export_transactions_csv(file_path, transactions):
    """Exports a list of transactions to a CSV file."""
    try:
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['timestamp', 'type', 'category', 'description', 'amount_paisa'])
            # Write transaction data
            for t in transactions:
                writer.writerow([
                    t['timestamp'],
                    t['type'],
                    t['category'],
                    t['description'],
                    t['amount_paisa']
                ])
        console.print(f"[green]Successfully exported transactions to {file_path}[/green]")
    except IOError as e:
        console.print(f"[red]Error exporting to CSV: {e}[/red]")

def export_transactions_json(file_path, transactions):
    """Exports a list of transactions to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(transactions, f, indent=4)
        console.print(f"[green]Successfully exported transactions to {file_path}[/green]")
    except IOError as e:
        console.print(f"[red]Error exporting to JSON: {e}[/red]")

def import_transactions_csv(file_path):
    """Imports transactions from a CSV file, skipping duplicates."""
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            transactions_to_add = list(reader)
        
        return _add_imported_transactions(transactions_to_add)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        return 0, 0
    except Exception as e:
        console.print(f"[red]Error importing from CSV: {e}[/red]")
        return 0, 0

def import_transactions_json(file_path):
    """Imports transactions from a JSON file, skipping duplicates."""
    try:
        with open(file_path, 'r') as f:
            transactions_to_add = json.load(f)

        return _add_imported_transactions(transactions_to_add)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        return 0, 0
    except json.JSONDecodeError:
        console.print(f"[red]Invalid JSON format in {file_path}[/red]")
        return 0, 0
    except Exception as e:
        console.print(f"[red]Error importing from JSON: {e}[/red]")
        return 0, 0

def _add_imported_transactions(new_transactions):
    """
    Adds new transactions to the database, checking for duplicates.
    A duplicate is defined as a transaction with the same timestamp and amount.
    """
    existing_transactions = load_all_transactions()
    existing_signatures = {
        (str(t['timestamp']), str(t['amount_paisa'])) for t in existing_transactions
    }

    imported_count = 0
    skipped_count = 0

    with open(TRANSACTIONS_FILE, "a") as f:
        for t in new_transactions:
            try:
                # Ensure values are in the correct format
                timestamp = float(t['timestamp'])
                amount_paisa = int(t['amount_paisa'])
                
                # Create a signature to check for duplicates
                signature = (str(timestamp), str(amount_paisa))
                
                if signature not in existing_signatures:
                    f.write(
                        f"{timestamp},{t['type']},{t['category']},{t['description']},{amount_paisa}\n"
                    )
                    existing_signatures.add(signature)
                    imported_count += 1
                else:
                    skipped_count += 1
            except (KeyError, ValueError) as e:
                console.print(f"[yellow]Skipping malformed record: {t} - {e}[/yellow]")
                skipped_count += 1

    return imported_count, skipped_count

def create_backup():
    """Creates a full backup of transactions and budgets."""
    transactions = load_all_transactions()
    budgets = load_budgets()

    backup_data = {
        "transactions": transactions,
        "budgets": budgets
    }

    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_path = f"finance_tracker_backup_{timestamp}.json"

    try:
        with open(file_path, 'w') as f:
            json.dump(backup_data, f, indent=4)
        console.print(f"[green]Successfully created backup at {file_path}[/green]")
    except IOError as e:
        console.print(f"[red]Error creating backup: {e}[/red]")

def restore_from_backup(file_path):
    """Restores transactions and budgets from a backup file, overwriting existing data."""
    try:
        with open(file_path, 'r') as f:
            backup_data = json.load(f)

        # Restore transactions
        with open(TRANSACTIONS_FILE, 'w') as f:
            for t in backup_data.get("transactions", []):
                 f.write(
                    f"{t['timestamp']},{t['type']},{t['category']},{t['description']},{t['amount_paisa']}\n"
                )

        # Restore budgets
        with open(BUDGETS_FILE, 'w') as f:
            current_month_year = datetime.now().strftime("%Y-%m")
            for category, amount in backup_data.get("budgets", {}).items():
                f.write(f"{current_month_year},{category},{amount}\n")

        console.print(f"[green]Successfully restored data from {file_path}[/green]")

    except FileNotFoundError:
        console.print(f"[red]Backup file not found: {file_path}[/red]")
    except (json.JSONDecodeError, KeyError) as e:
        console.print(f"[red]Invalid backup file format: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during restore: {e}[/red]")
