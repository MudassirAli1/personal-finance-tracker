from rich.console import Console
from datetime import datetime

# Transaction categories
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

console = Console()

def load_all_transactions():
    """Loads all transactions from the transactions file."""
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 5:
                    try:
                        timestamp, trans_type, category, description, amount_paisa_str = parts
                        transactions.append({
                            "timestamp": float(timestamp),
                            "type": trans_type,
                            "category": category,
                            "description": description,
                            "amount_paisa": int(amount_paisa_str)
                        })
                    except ValueError as e:
                        console.print(f"[red]Skipping malformed transaction line: {line.strip()} - {e}[/red]")
                else:
                    console.print(f"[red]Skipping malformed transaction line (incorrect number of parts): {line.strip()}[/red]")
    except FileNotFoundError:
        # This is not an error, it just means no transactions have been recorded yet.
        pass
    except Exception as e:
        console.print(f"[red]Error loading transactions: {e}[/red]")
    return transactions

def load_budgets():
    """
    Loads budgets from budgets.txt for the current month.
    Returns a dictionary: {category: amount_paisa}
    """
    budgets = {}
    current_month_year = datetime.now().strftime("%Y-%m")
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    month_year, category, amount_paisa = parts
                    if month_year == current_month_year:
                        budgets[category] = int(amount_paisa)
        return budgets
    except FileNotFoundError:
        return {}
    except Exception as e:
        console.print(f"Error loading budgets: {e}")
        return {}
