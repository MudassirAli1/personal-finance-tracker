import questionary
from rich.console import Console
from datetime import datetime

from database.utils import load_all_transactions
from .data_management import (
    export_transactions_csv,
    export_transactions_json,
    import_transactions_csv,
    import_transactions_json,
    create_backup,
    restore_from_backup
)

console = Console()

def show_data_management_menu():
    """Displays the data management menu and handles user choices."""
    while True:
        choice = questionary.select(
            "Data Management Menu:",
            choices=[
                "Export Transactions",
                "Import Transactions",
                "Create Full Backup",
                "Restore from Backup",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Export Transactions":
            handle_export()
        elif choice == "Import Transactions":
            handle_import()
        elif choice == "Create Full Backup":
            create_backup()
        elif choice == "Restore from Backup":
            handle_restore()
        elif choice == "Back to Main Menu":
            break
        else:
            console.print("[red]Invalid choice.[/red]")
        
        console.print("\n")

def handle_export():
    """Handles the logic for exporting transactions."""
    export_format = questionary.select(
        "Select export format:",
        choices=["CSV", "JSON"]
    ).ask()

    export_range = questionary.select(
        "Select data range to export:",
        choices=["All Time", "Current Month", "Specific Year"]
    ).ask()

    transactions = load_all_transactions()
    transactions_to_export = []

    if export_range == "All Time":
        transactions_to_export = transactions
    elif export_range == "Current Month":
        current_month_year = datetime.now().strftime("%Y-%m")
        transactions_to_export = [
            t for t in transactions 
            if datetime.fromtimestamp(t['timestamp']).strftime("%Y-%m") == current_month_year
        ]
    elif export_range == "Specific Year":
        year = questionary.text("Enter the year (YYYY):").ask()
        try:
            int(year) # Validate
            transactions_to_export = [
                t for t in transactions
                if datetime.fromtimestamp(t['timestamp']).strftime("%Y") == year
            ]
        except (ValueError, TypeError):
            console.print("[red]Invalid year format.[/red]")
            return

    if not transactions_to_export:
        console.print("[yellow]No transactions found for the selected range.[/yellow]")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_path = f"transactions_export_{timestamp}"

    if export_format == "CSV":
        file_path += ".csv"
        export_transactions_csv(file_path, transactions_to_export)
    elif export_format == "JSON":
        file_path += ".json"
        export_transactions_json(file_path, transactions_to_export)

def handle_import():
    """Handles the logic for importing transactions."""
    import_format = questionary.select(
        "Select import format:",
        choices=["CSV", "JSON"]
    ).ask()

    file_path = questionary.text("Enter the full path to the import file:").ask()
    if not file_path:
        console.print("[red]File path cannot be empty.[/red]")
        return

    imported_count = 0
    skipped_count = 0

    if import_format == "CSV":
        imported_count, skipped_count = import_transactions_csv(file_path)
    elif import_format == "JSON":
        imported_count, skipped_count = import_transactions_json(file_path)
        
    console.print(f"\nImport Summary:")
    console.print(f"  • [green]Successfully imported: {imported_count} transactions[/green]")
    console.print(f"  • [yellow]Skipped (duplicates or malformed): {skipped_count} transactions[/yellow]")

def handle_restore():
    """Handles the logic for restoring from a backup."""
    file_path = questionary.text("Enter the full path to the backup file:").ask()
    if not file_path:
        console.print("[red]File path cannot be empty.[/red]")
        return
        
    if questionary.confirm(
        "WARNING: This will overwrite all existing data. Are you sure you want to continue?",
        default=False
    ).ask():
        restore_from_backup(file_path)
    else:
        console.print("[yellow]Restore operation cancelled.[/yellow]")
