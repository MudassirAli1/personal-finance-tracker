import questionary
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
from database.utils import load_all_transactions, EXPENSE_CATEGORIES, INCOME_CATEGORIES

console = Console()

def spending_analysis():
    """
    Analyzes and displays spending patterns for the current month.
    """
    console.print(Text("\n--- Spending Analysis ---", style="bold blue"))

    transactions = load_all_transactions()
    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    current_month_year = datetime.now().strftime("%Y-%m")
    
    current_month_expenses = [
        t for t in transactions 
        if t['type'].lower() == 'expense' and 
           datetime.fromtimestamp(t['timestamp']).strftime('%Y-%m') == current_month_year
    ]

    if not current_month_expenses:
        console.print("[yellow]No expenses recorded for the current month.[/yellow]")
        return

    # Calculate spending breakdown by category
    spending_by_category = {cat: 0 for cat in EXPENSE_CATEGORIES}
    total_expense = 0
    for expense in current_month_expenses:
        category = expense['category']
        amount = expense['amount_paisa']
        if category in spending_by_category:
            spending_by_category[category] += amount
        total_expense += amount

    # Display spending breakdown in a table
    table = Table(title=f"Spending Breakdown for {datetime.now().strftime('%B %Y')}")
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Amount (Rs)", style="red", justify="right")
    table.add_column("Percentage", style="magenta", justify="right")

    for category, amount in spending_by_category.items():
        if amount > 0:
            percentage = (amount / total_expense) * 100 if total_expense > 0 else 0
            table.add_row(category, f"{amount / 100:.2f}", f"{percentage:.2f}%")
    
    console.print(table)

    # Top 3 spending categories
    sorted_spending = sorted(spending_by_category.items(), key=lambda item: item[1], reverse=True)
    console.print(Text("\n--- Top 3 Spending Categories ---", style="bold blue"))
    for i in range(min(3, len(sorted_spending))):
        category, amount = sorted_spending[i]
        if amount > 0:
            console.print(f"{i+1}. {category}: [red]{amount / 100:.2f} Rs[/red]")

    # Average daily expense
    days_in_month = (datetime.now().day)
    average_daily_expense = (total_expense / days_in_month) / 100 if days_in_month > 0 else 0
    console.print(Text("\n--- Burn Rate ---", style="bold blue"))
    console.print(f"Average Daily Expense: [red]{average_daily_expense:.2f} Rs[/red]")
    
    # ASCII Pie Chart
    console.print(Text("\n--- Spending Distribution ---", style="bold blue"))
    pie_chart_data = {cat: amount for cat, amount in spending_by_category.items() if amount > 0}
    total_for_pie = sum(pie_chart_data.values())
    
    for category, amount in pie_chart_data.items():
        percentage = (amount / total_for_pie) * 100
        bar_length = int(percentage / 2) # Scale to a 50-char width
        bar = "█" * bar_length
        console.print(f"{category:<15} {bar} {percentage:.1f}%")

def income_analysis():
    """
    Analyzes and displays income patterns for the current month.
    """
    console.print(Text("\n--- Income Analysis ---", style="bold green"))

    transactions = load_all_transactions()
    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    current_month_year = datetime.now().strftime("%Y-%m")
    
    current_month_income = [
        t for t in transactions 
        if t['type'].lower() == 'income' and 
           datetime.fromtimestamp(t['timestamp']).strftime('%Y-%m') == current_month_year
    ]

    if not current_month_income:
        console.print("[yellow]No income recorded for the current month.[/yellow]")
        return

    # Calculate income breakdown by source
    income_by_source = {cat: 0 for cat in INCOME_CATEGORIES}
    total_income = 0
    for income in current_month_income:
        category = income['category']
        amount = income['amount_paisa']
        if category in income_by_source:
            income_by_source[category] += amount
        total_income += amount

    # Display income breakdown in a table
    table = Table(title=f"Income Breakdown for {datetime.now().strftime('%B %Y')}")
    table.add_column("Source", style="cyan", justify="left")
    table.add_column("Amount (Rs)", style="green", justify="right")
    table.add_column("Percentage", style="magenta", justify="right")

    for source, amount in income_by_source.items():
        if amount > 0:
            percentage = (amount / total_income) * 100 if total_income > 0 else 0
            table.add_row(source, f"{amount / 100:.2f}", f"{percentage:.2f}%")
    
    console.print(table)

    # Total income
    console.print(Text("\n--- Total Income ---", style="bold green"))
    console.print(f"Total Income this month: [green]{total_income / 100:.2f} Rs[/green]")

def savings_analysis():
    """
    Analyzes and displays savings for the current month.
    """
    console.print(Text("\n--- Savings Analysis ---", style="bold yellow"))

    transactions = load_all_transactions()
    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    current_month_year = datetime.now().strftime("%Y-%m")
    
    total_income = 0
    total_expense = 0

    for t in transactions:
        if datetime.fromtimestamp(t['timestamp']).strftime('%Y-%m') == current_month_year:
            if t['type'].lower() == 'income':
                total_income += t['amount_paisa']
            elif t['type'].lower() == 'expense':
                total_expense += t['amount_paisa']

    monthly_savings = total_income - total_expense
    savings_rate = (monthly_savings / total_income) * 100 if total_income > 0 else 0

    savings_style = "green" if monthly_savings >= 0 else "red"

    console.print(f"Total Income: [green]{total_income / 100:.2f} Rs[/green]")
    console.print(f"Total Expenses: [red]{total_expense / 100:.2f} Rs[/red]")
    console.print(f"Monthly Savings: [{savings_style}]{monthly_savings / 100:.2f} Rs[/{savings_style}]")
    console.print(f"Savings Rate: [{savings_style}]{savings_rate:.2f}%[/{savings_style}]")

if __name__ == '__main__':
    spending_analysis()
    income_analysis()
    savings_analysis()
