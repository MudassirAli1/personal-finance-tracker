import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from features.transactions.transactions import add_expense, add_income, list_transactions, view_balance
from features.budgets.budgets import set_budget, view_budgets
from features.analytics.analytics import show_analytics_menu
from features.smart_assistance.assistance import daily_financial_check
from features.data_management.cli import show_data_management_menu

console = Console()

def display_main_menu():
    """Displays the main menu of the Personal Finance Tracker."""
    console.print(
        Panel(
            Text("Personal Finance Tracker CLI", justify="center", style="bold blue"),
            subtitle=Text("Track your money with ease!", justify="center", style="italic green"),
            border_style="green"
        )
    )

def main():
    display_main_menu()

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "View Current Balance",
                "Set Budget",
                "View Budgets",
                "Financial Analytics",
                "Smart Financial Assistant",
                "Data Management",
                "Exit"
            ]
        ).ask()

        if choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "List Transactions":
            list_transactions()
        elif choice == "View Current Balance":
            view_balance()
        elif choice == "Set Budget":
            set_budget()
        elif choice == "View Budgets":
            view_budgets()
        elif choice == "Financial Analytics":
            show_analytics_menu()
        elif choice == "Smart Financial Assistant":
            daily_financial_check()
        elif choice == "Data Management":
            show_data_management_menu()
        elif choice == "Exit":
            console.print(Text("Thank you for using the Personal Finance Tracker. Goodbye!", style="bold blue"))
            break
        else:
            console.print(Text("Invalid choice, please try again.", style="red"))
        
        console.print("\n") # Add a newline for better readability between actions


if __name__ == "__main__":
    main()