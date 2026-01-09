import questionary
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta

# Initialize Rich Console
console = Console()

# Transaction categories
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

TRANSACTIONS_FILE = "database/transactions.txt"

def add_expense():
    """Adds a new expense transaction."""
    amount_str = questionary.text("Enter the expense amount:").ask()
    try:
        # Store amount in cents
        amount = int(float(amount_str) * 100)
        if amount <= 0:
            console.print("[red]Amount must be a positive number.[/red]")
            return
    except (ValueError, TypeError):
        console.print("[red]Invalid amount. Please enter a number.[/red]")
        return

    category = questionary.select(
        "Select an expense category:",
        choices=EXPENSE_CATEGORIES
    ).ask()

    description = questionary.text("Enter a description for the expense:").ask()

    date_str = questionary.text(
        "Enter the date (YYYY-MM-DD), or leave empty for today:"
    ).ask()

    if not date_str:
        # Use current timestamp if date not provided
        timestamp = datetime.now().timestamp()
    else:
        try:
            # Validate and convert custom date to timestamp
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = date_obj.timestamp()
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
            return

    # Save the transaction
    with open("database/transactions.txt", "a") as f:
        f.write(f"{timestamp},expense,{category},{description},{amount}\n")

    console.print("[green]Expense added successfully![/green]")

def add_income():
    """Adds a new income transaction."""
    amount_str = questionary.text("Enter the income amount:").ask()
    try:
        # Store amount in cents
        amount = int(float(amount_str) * 100)
        if amount <= 0:
            console.print("[red]Amount must be a positive number.[/red]")
            return
    except (ValueError, TypeError):
        console.print("[red]Invalid amount. Please enter a number.[/red]")
        return

    category = questionary.select(
        "Select an income category:",
        choices=INCOME_CATEGORIES
    ).ask()

    description = questionary.text("Enter a description for the income:").ask()

    date_str = questionary.text(
        "Enter the date (YYYY-MM-DD), or leave empty for today:"
    ).ask()

    if not date_str:
        timestamp = datetime.now().timestamp()
    else:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = date_obj.timestamp()
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")
            return

    with open("database/transactions.txt", "a") as f:
        f.write(f"{timestamp},income,{category},{description},{amount}\n")

    console.print("[green]Income added successfully![/green]")

def _load_all_transactions():
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
        console.print("[yellow]No transactions recorded yet.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error loading transactions: {e}[/red]")
    return transactions

def list_transactions():
    """Lists all transactions, with optional filters."""
    console.print(Text("\n--- Your Transactions ---", style="bold blue"))

    transactions = _load_all_transactions()
    if not transactions:
        return

    # Sort by date, newest first
    transactions.sort(key=lambda x: x['timestamp'], reverse=True)

    filter_choice = questionary.select(
        "Filter transactions:",
        choices=[
            "All",
            "Last 7 Days",
            "Only Expenses",
            "Only Income"
        ]
    ).ask()

    filtered_transactions = []
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    for t in transactions:
        include = False
        transaction_date_obj = datetime.fromtimestamp(t['timestamp'])

        if filter_choice == "All":
            include = True
        elif filter_choice == "Last 7 Days":
            if transaction_date_obj >= seven_days_ago:
                include = True
        elif filter_choice == "Only Expenses":
            if t['type'].lower() == "expense":
                include = True
        elif filter_choice == "Only Income":
            if t['type'].lower() == "income":
                include = True
        
        if include:
            filtered_transactions.append(t)

    if not filtered_transactions:
        console.print("[yellow]No transactions found matching your filter criteria.[/yellow]")
        return

    table = Table(title="Transaction History")
    table.add_column("Date", style="cyan", justify="left")
    table.add_column("Type", justify="left")
    table.add_column("Category", style="magenta", justify="left")
    table.add_column("Description", style="white", justify="left")
    table.add_column("Amount (Rs)", justify="right")

    for t in filtered_transactions:
        amount_display = f"{t['amount_paisa'] / 100:.2f}"
        style = "green" if t['type'].lower() == "income" else "red"
        
        table.add_row(
            datetime.fromtimestamp(t['timestamp']).strftime("%Y-%m-%d"),
            Text(t['type'].capitalize(), style=style),
            t['category'],
            t['description'],
            Text(amount_display, style=style)
        )
    
    console.print(table)

def view_balance():
    """
    Displays the total income, total expenses, and current balance for the current month.
    """
    console.print(Text("\n--- Current Month's Balance ---", style="bold green"))

    transactions = _load_all_transactions()
    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    current_month_year = datetime.now().strftime("%Y-%m")
    
    total_income_paisa = 0
    total_expense_paisa = 0

    for t in transactions:
        transaction_date_obj = datetime.fromtimestamp(t['timestamp'])
        if transaction_date_obj.strftime("%Y-%m") == current_month_year:
            if t['type'].lower() == "income":
                total_income_paisa += t['amount_paisa']
            elif t['type'].lower() == "expense":
                total_expense_paisa += t['amount_paisa']
    
    current_balance_paisa = total_income_paisa - total_expense_paisa

    console.print(f"Total Income: [green]{total_income_paisa / 100:.2f} Rs[/green]")
    console.print(f"Total Expenses: [red]{total_expense_paisa / 100:.2f} Rs[/red]")
    
    balance_style = "green" if current_balance_paisa >= 0 else "red"
    console.print(f"Current Balance: [{balance_style}]{current_balance_paisa / 100:.2f} Rs[/{balance_style}]")

