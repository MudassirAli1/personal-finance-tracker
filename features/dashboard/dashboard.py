import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.utils import load_all_transactions, load_budgets

def run():
    st.set_page_config(layout="wide", page_title="Financial Dashboard")

    st.title("Personal Finance Dashboard")

    # Load data
    transactions = load_all_transactions()
    budgets = load_budgets()

    if not transactions:
        st.warning("No transactions found. Add some transactions in the CLI to see the dashboard.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df['amount'] = df['amount_paisa'] / 100

    # Filter for current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    df_current_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]

    # --- Balance Section ---
    total_income = df_current_month[df_current_month['type'] == 'income']['amount'].sum()
    total_expenses = df_current_month[df_current_month['type'] == 'expense']['amount'].sum()
    balance = total_income - total_expenses

    st.markdown("### Current Month's Financial Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{total_income:,.2f}", delta_color="normal")
    col2.metric("Total Expenses", f"₹{total_expenses:,.2f}", delta_color="inverse")
    col3.metric("Current Balance", f"₹{balance:,.2f}")

    st.markdown("---")

    # --- Budget Status Section ---
    st.markdown("### Budget Status")

    if not budgets:
        st.info("No budgets set for the current month.")
    else:
        # Calculate spent amount for each category
        spent_by_category = df_current_month[df_current_month['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()

        budget_data = []
        for category, budget_paisa in budgets.items():
            budget_amount = budget_paisa / 100
            spent_amount = spent_by_category.get(category, 0)
            remaining = budget_amount - spent_amount
            utilization = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
            budget_data.append({
                "Category": category,
                "Budget": budget_amount,
                "Spent": spent_amount,
                "Remaining": remaining,
                "Utilization": utilization
            })
        
        if budget_data:
            budget_df = pd.DataFrame(budget_data)
            
            for index, row in budget_df.iterrows():
                st.markdown(f"**{row['Category']}**")
                st.markdown(f"₹{row['Spent']:,.2f} / ₹{row['Budget']:,.2f}")
                
                progress_color = 'green'
                if row['Utilization'] >= 100:
                    progress_color = 'red'
                elif row['Utilization'] >= 70:
                    progress_color = 'orange'
                
                st.progress(int(row['Utilization']))
        else:
            st.info("No budget data to display.")


    st.markdown("---")

    # --- Recent Transactions Table ---
    st.markdown("### Recent Transactions")
    df_recent = df.sort_values(by='date', ascending=False).head(10)
    
    # Format for display
    df_recent_display = df_recent[['date', 'type', 'category', 'description', 'amount']].copy()
    df_recent_display['date'] = df_recent_display['date'].dt.strftime('%Y-%m-%d')
    df_recent_display['amount'] = df_recent_display.apply(lambda row: f"₹{row['amount']:,.2f}", axis=1)
    
    st.dataframe(df_recent_display.style.apply(
        lambda row: ['color: green' if row.type == 'income' else 'color: red' for v in row], axis=1
    ), use_container_width=True)

if __name__ == "__main__":
    run()
