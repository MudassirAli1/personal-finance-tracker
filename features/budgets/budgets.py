import questionary
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import ProgressBar
from database.utils import (
    load_all_transactions,
    load_budgets,
    EXPENSE_CATEGORIES,
    BUDGETS_FILE
)

# Initialize Rich console
console = Console()

def _get_current_month_expenses():
    """
    Reads transactions for the current month and aggregates expenses by category.
    Returns a dictionary: {category: spent_amount_paisa}
    """
    expenses = {cat: 0 for cat in EXPENSE_CATEGORIES}
    current_month_year = datetime.now().strftime("%Y-%m")
    
    all_transactions = load_all_transactions()

    for t in all_transactions:
        transaction_date = datetime.fromtimestamp(t['timestamp'])
        if transaction_date.strftime("%Y-%m") == current_month_year and t['type'].lower() == "expense":
            if t['category'] in expenses:
                expenses[t['category']] += t['amount_paisa']
    return expenses


def set_budget():
    """
    Allows the user to set a monthly budget for a specific category.
    """
    console.print(Text("\n--- Set Monthly Budget ---", style="bold green"))

    category = questionary.select(
        "Select a category for the budget:",
        choices=EXPENSE_CATEGORIES
    ).ask()

    if not category:
        console.print(Text("Budget setting cancelled.", style="red"))
        return

    while True:
        amount_str = questionary.text(f"Enter budget amount for {category} (e.g., 50.00):").ask()
        if not amount_str:
            console.print(Text("Budget setting cancelled.", style="red"))
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                console.print(Text("Amount must be a positive number.", style="red"))
                continue
            # Store as paisa/cents to avoid floating-point errors
            amount_paisa = int(amount * 100)
            break
        except ValueError:
            console.print(Text("Invalid amount. Please enter a number.", style="red"))

    current_month = datetime.now().strftime("%Y-%m") # YYYY-MM format

    # Save to budgets.txt
    try:
        # Check if budget for this category and month already exists to update it
        existing_budgets = []
        updated = False
        try:
            with open(BUDGETS_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        m_y, cat, _ = parts
                        if m_y == current_month and cat == category:
                            existing_budgets.append(f"{current_month},{category},{amount_paisa}\n")
                            updated = True
                        else:
                            existing_budgets.append(line)
                    else:
                        existing_budgets.append(line) # Keep malformed lines
        except FileNotFoundError:
            pass # File will be created

        with open(BUDGETS_FILE, "w") as f:
            if updated:
                f.writelines(existing_budgets)
            else:
                f.writelines(existing_budgets) # Write existing lines back
                f.write(f"{current_month},{category},{amount_paisa}\n") # Add new budget

        console.print(Text(f"Budget of Rs {amount:.2f} set for {category} for {current_month}.", style="green"))
    except IOError as e:
        console.print(Text(f"Error saving budget: {e}", style="red"))


def view_budgets():
    """
    Displays current month's budgets and spending against them.
    """
    console.print(Text("\n--- Monthly Budget Overview ---", style="bold blue"))

    current_month_budgets = load_budgets()
    current_month_expenses = _get_current_month_expenses()
    current_month_year = datetime.now().strftime("%B %Y")

    table = Table(title=f"Budget vs. Spending ({current_month_year})")
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Budget (Rs)", style="magenta", justify="right")
    table.add_column("Spent (Rs)", style="red", justify="right")
    table.add_column("Remaining (Rs)", style="green", justify="right")
    table.add_column("Utilization (%)", justify="center")
    table.add_column("Status", justify="center")

    total_budget_paisa = 0
    total_spent_paisa = 0
    over_budget_categories = []

    for category in EXPENSE_CATEGORIES:
        budget_paisa = current_month_budgets.get(category, 0)
        spent_paisa = current_month_expenses.get(category, 0)

        remaining_paisa = budget_paisa - spent_paisa
        
        utilization_percentage = 0
        if budget_paisa > 0:
            utilization_percentage = (spent_paisa / budget_paisa) * 100

        status_text = ""
        status_style = ""
        
        if utilization_percentage < 70:
            status_style = "green"
            status_text = "🟢 OK"
        elif 70 <= utilization_percentage <= 100:
            status_style = "yellow"
            status_text = "🟡 Warning"
        else:
            status_style = "red"
            status_text = "🔴 Over"
            if budget_paisa > 0: # Only count as over budget if there was a budget set
                over_budget_categories.append(category)

        total_budget_paisa += budget_paisa
        total_spent_paisa += spent_paisa

        # Progress bar for utilization (using Rich's capabilities if possible, or simple text representation)
        # For a simple text representation:
        progress_bar_length = 10
        filled_blocks = int((utilization_percentage / 100) * progress_bar_length)
        empty_blocks = progress_bar_length - filled_blocks
        progress_bar = f"[{'█' * filled_blocks}{'░' * empty_blocks}]"

        table.add_row(
            category,
            f"{budget_paisa / 100:.2f}",
            f"{spent_paisa / 100:.2f}",
            f"{remaining_paisa / 100:.2f}",
            f"{progress_bar} {utilization_percentage:.1f}%",
            Text(status_text, style=status_style)
        )
    
    console.print(table)

    # Overall Summary
    overall_remaining_paisa = total_budget_paisa - total_spent_paisa
    overall_utilization_percentage = 0
    if total_budget_paisa > 0:
        overall_utilization_percentage = (total_spent_paisa / total_budget_paisa) * 100

    overall_status_style = "green"
    if overall_utilization_percentage >= 70 and overall_utilization_percentage <= 100:
        overall_status_style = "yellow"
    elif overall_utilization_percentage > 100:
        overall_status_style = "red"

    console.print(Text("\n--- Overall Monthly Summary ---", style="bold blue"))
    console.print(f"Total Budget: [magenta]{total_budget_paisa / 100:.2f}[/magenta] Rs")
    console.print(f"Total Spent: [red]{total_spent_paisa / 100:.2f}[/red] Rs")
    console.print(f"Total Remaining: [{overall_status_style}]{overall_remaining_paisa / 100:.2f}[/{overall_status_style}] Rs")
    console.print(f"Overall Utilization: [{overall_status_style}]{overall_utilization_percentage:.1f}%[/{overall_status_style}]")

    if over_budget_categories:
        console.print(Text("\n⚠️ Categories Over Budget:", style="bold yellow"))
        for cat in over_budget_categories:
            console.print(f"- [red]{cat}[/red]")
        console.print(Text("Consider adjusting your spending in these areas.", style="yellow"))

    if total_budget_paisa == 0:
        console.print(Text("\nNo budgets set for the current month. Use 'Set Budget' to get started!", style="italic yellow"))


if __name__ == '__main__':
    # Test cases (uncomment to run for testing)
    # set_budget()
    view_budgets()