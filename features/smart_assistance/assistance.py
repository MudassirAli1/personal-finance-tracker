from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, date
from database.utils import load_all_transactions, load_budgets

console = Console()

def daily_financial_check():
    """
    Provides a smart analysis of today's finances, including spending,
    remaining budget, alerts, and a quick tip.
    """
    console.print(
        Panel(
            Text("📊 Daily Financial Check", justify="center", style="bold yellow"),
            border_style="yellow"
        )
    )

    # --- 1. Today's Spending ---
    transactions = load_all_transactions()
    today = date.today()
    
    todays_expenses_paisa = sum(
        t['amount_paisa']
        for t in transactions
        if t['type'] == 'expense' and datetime.fromtimestamp(t['timestamp']).date() == today
    )

    console.print(f"Today's Spending: [bold red]Rs {todays_expenses_paisa / 100:.2f}[/bold red]")

    # --- 2. Remaining Daily Budget ---
    budgets = load_budgets()
    total_monthly_budget_paisa = sum(budgets.values())
    
    if total_monthly_budget_paisa > 0:
        days_in_month = (date(today.year, today.month + 1, 1) - date(today.year, today.month, 1)).days if today.month < 12 else 31
        daily_budget_paisa = total_monthly_budget_paisa / days_in_month
        remaining_daily_budget_paisa = daily_budget_paisa - todays_expenses_paisa
        
        remaining_style = "green" if remaining_daily_budget_paisa >= 0 else "red"
        console.print(f"Daily Budget: [bold green]Rs {daily_budget_paisa / 100:.2f}[/bold green]")
        console.print(f"Remaining: [bold {remaining_style}]Rs {remaining_daily_budget_paisa / 100:.2f}[/bold {remaining_style}]")
    else:
        console.print("Daily Budget: [yellow]No budget set for this month.[/yellow]")

    # --- 3. Alerts ---
    console.print("\n[bold yellow]⚠️ Alerts:[/bold yellow]")
    
    # Budget Alerts
    if budgets:
        current_month_expenses = {cat: 0 for cat in budgets.keys()}
        current_month_str = today.strftime("%Y-%m")

        for t in transactions:
            if t['type'] == 'expense' and t['category'] in current_month_expenses:
                if datetime.fromtimestamp(t['timestamp']).strftime("%Y-%m") == current_month_str:
                    current_month_expenses[t['category']] += t['amount_paisa']

        alert_found = False
        for category, spent in current_month_expenses.items():
            budget_amount = budgets.get(category, 0)
            if budget_amount > 0:
                utilization = (spent / budget_amount) * 100
                if utilization > 80:
                    alert_found = True
                    console.print(f"  • [yellow]'{category}' category is at {utilization:.1f}% of its budget.[/yellow]")
        
        if not alert_found:
             console.print("  • [green]No budget alerts. Keep it up![/green]")

    else:
        console.print("  • [cyan]Set budgets to get spending alerts.[/cyan]")

    # --- 4. Quick Tip ---
    console.print("\n[bold cyan]💡 Quick Tip:[/bold cyan]")
    # Simple rule-based tips for now
    if todays_expenses_paisa == 0:
        console.print("  • [green]No spending today! A great day to save.[/green]")
    elif todays_expenses_paisa > (total_monthly_budget_paisa / 30 if total_monthly_budget_paisa > 0 else 500000): # 5000 INR
         console.print("  • [yellow]Spending is a bit high today. Review your purchases.[/yellow]")
    else:
        console.print("  • [green]You're on track with your spending. Well done![/green]")
