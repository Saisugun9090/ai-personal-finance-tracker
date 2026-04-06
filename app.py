import os
from typing import List

from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from finance_ai import analyze_budget, format_expenses_for_display, parse_uploaded_csv

load_dotenv()

st.set_page_config(page_title="AI Personal Finance Tracker", layout="wide")

API_KEY = os.getenv("GOOGLE_API_KEY")

EXAMPLE_CSV = "Amount,Category,Description,Date\n72.45,Groceries,Weekly market,2026-03-01\n18.60,Transportation,Uber ride,2026-03-02\n34.00,Entertainment,Movie night,2026-03-05\n128.35,Utilities,Electric bill,2026-03-07\n61.20,Dining,Dinner out,2026-03-09"


def get_currency_label(currency: str) -> str:
    """Returns currency symbol based on selected currency"""
    currency_symbols = {
        "USD": "$",
        "GBP": "£",
        "EUR": "€",
        "INR": "₹",
        "CAD": "C$",
        "AUD": "A$",
        "JPY": "¥",
        "CHF": "CHF",
        "CNY": "¥",
        "SGD": "S$",
        "HKD": "HK$",
        "KRW": "₩",
        "BRL": "R$",
        "MXN": "Mex$",
        "ZAR": "R",
        "TRY": "₺",
        "RUB": "₽",
        "SEK": "kr",
        "NOK": "kr",
        "DKK": "kr",
        "PLN": "zł",
        "CZK": "Kč",
        "HUF": "Ft",
        "ILS": "₪",
        "THB": "฿",
        "MYR": "RM",
        "PHP": "₱",
        "IDR": "Rp",
        "VND": "₫",
        "EGP": "£",
        "SAR": "﷼",
        "AED": "د.إ",
        "Other": "$"
    }
    return currency_symbols.get(currency, "$")


def get_currency_options() -> list:
    """Returns list of available currencies for selection"""
    return [
        "USD", "GBP", "EUR", "INR", "CAD", "AUD", "JPY", "CHF", "CNY", "SGD",
        "HKD", "KRW", "BRL", "MXN", "ZAR", "TRY", "RUB", "SEK", "NOK", "DKK",
        "PLN", "CZK", "HUF", "ILS", "THB", "MYR", "PHP", "IDR", "VND", "EGP",
        "SAR", "AED", "Other"
    ]


def load_expense_rows() -> List[dict]:
    if "expenses" not in st.session_state:
        st.session_state.expenses = []
    return st.session_state.expenses


def collect_income() -> dict:
    st.subheader("Step 1: Your Monthly Income")
    with st.form("income_form"):
        primary_income = st.number_input("Primary Monthly Income (after tax)", min_value=0.0, format="%.2f", value=0.0)
        additional_income = st.number_input("Additional Income (freelance, side hustle, etc.)", min_value=0.0, format="%.2f", value=0.0)
        selected_currency = st.selectbox(
            "Preferred Currency",
            get_currency_options(),
            index=0  # Default to USD
        )
        total_income = primary_income + additional_income
        submitted = st.form_submit_button("Next: Essential Expenses")
        if submitted:
            return {
                "primary": primary_income,
                "additional": additional_income,
                "total": total_income,
                "currency": selected_currency,
            }
    return {}


def collect_essential_expenses() -> dict:
    st.subheader("Step 2: Essential Monthly Expenses")
    with st.form("essential_form"):
        rent = st.number_input("Rent/Housing", min_value=0.0, format="%.2f", value=0.0)
        emi = st.number_input("EMI/Loan Payments", min_value=0.0, format="%.2f", value=0.0)
        groceries = st.number_input("Groceries", min_value=0.0, format="%.2f", value=0.0)
        utilities = st.number_input("Utilities (Electricity, Water, Gas)", min_value=0.0, format="%.2f", value=0.0)
        insurance = st.number_input("Insurance (Health, Car, etc.)", min_value=0.0, format="%.2f", value=0.0)
        transport = st.number_input("Transportation (Fuel, Public Transport)", min_value=0.0, format="%.2f", value=0.0)
        submitted = st.form_submit_button("Next: Non-Essential Expenses")
        if submitted:
            total_essential = rent + emi + groceries + utilities + insurance + transport
            return {
                "rent": rent, "emi": emi, "groceries": groceries,
                "utilities": utilities, "insurance": insurance, "transport": transport,
                "total": total_essential
            }
    return {}


def collect_non_essential_expenses() -> dict:
    st.subheader("Step 3: Non-Essential Monthly Expenses")
    with st.form("non_essential_form"):
        entertainment = st.number_input("Entertainment (Movies, Games, Hobbies)", min_value=0.0, format="%.2f", value=0.0)
        dining = st.number_input("Dining Out", min_value=0.0, format="%.2f", value=0.0)
        shopping = st.number_input("Shopping (Clothes, Gadgets, etc.)", min_value=0.0, format="%.2f", value=0.0)
        miscellaneous = st.number_input("Miscellaneous (Other expenses)", min_value=0.0, format="%.2f", value=0.0)
        submitted = st.form_submit_button("Analyze My Finances")
        if submitted:
            total_non_essential = entertainment + dining + shopping + miscellaneous
            return {
                "entertainment": entertainment, "dining": dining, "shopping": shopping,
                "miscellaneous": miscellaneous, "total": total_non_essential
            }
    return {}


def get_budget_info() -> dict:
    st.subheader("Enter Your Budget Information")
    with st.form("budget_form"):
        income = st.number_input("Monthly Income (after tax)", min_value=0.0, format="%.2f", value=0.0)
        budget_type = st.selectbox("Budget Type", ["Monthly", "Yearly"])
        essential_expenses = st.number_input("Essential Expenses (Rent, EMI, Groceries, Utilities, Insurance)", min_value=0.0, format="%.2f", value=0.0)
        discretionary_budget = st.number_input("Discretionary Budget (Dining, Entertainment, Shopping)", min_value=0.0, format="%.2f", value=0.0)
        savings_goal = st.number_input("Monthly Savings Goal", min_value=0.0, format="%.2f", value=0.0)
        submitted = st.form_submit_button("Analyze Budget")
        if submitted:
            return {
                "income": income,
                "budget_type": budget_type,
                "essential_expenses": essential_expenses,
                "discretionary_budget": discretionary_budget,
                "savings_goal": savings_goal
            }
    return {}


def show_expense_visualizations(expenses: List[dict]) -> None:
    import pandas as pd
    df = pd.DataFrame(expenses)
    df['Amount'] = df['Amount'].astype(float)
    
    # Category totals
    category_totals = df.groupby('Category')['Amount'].sum().reset_index()
    st.subheader("Expense Breakdown by Category")
    st.bar_chart(category_totals.set_index('Category'))
    
    # Monthly totals (assuming Date is in YYYY-MM-DD)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_totals = df.groupby('Month')['Amount'].sum().reset_index()
    monthly_totals['Month'] = monthly_totals['Month'].astype(str)
    st.subheader("Monthly Spending Trend")
    st.line_chart(monthly_totals.set_index('Month'))
    
    # Top expenses
    top_expenses = df.nlargest(10, 'Amount')[['Date', 'Category', 'Description', 'Amount']]
    st.subheader("Top 10 Expenses")
    st.dataframe(top_expenses, use_container_width=True)


def show_sidebar() -> None:
    st.sidebar.header("AI Personal Finance Advisor")
    st.sidebar.write(
        "Answer questions about your income and expenses for personalized financial insights."
    )
    st.sidebar.markdown("**No CSV required** - Just answer the questions step by step.")
    st.sidebar.markdown("**Local fallback**: If `GOOGLE_API_KEY` is not set, the app will still run with a smart offline analyzer.")
    if API_KEY:
        st.sidebar.success("Gemini API key detected")
    else:
        st.sidebar.warning("No Gemini API key found. Using offline insights.")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### How it works")
    st.sidebar.write(
        "1. Enter your monthly income\n"
        "2. List essential expenses\n"
        "3. Add non-essential spending\n"
        "4. Get analysis and advice"
    )


def main() -> None:
    st.title("AI Personal Finance Advisor")
    st.write(
        "Answer a few questions about your income and expenses, and get personalized financial insights and advice."
    )

    show_sidebar()

    # Initialize session state
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "income" not in st.session_state:
        st.session_state.income = {}
    if "essential" not in st.session_state:
        st.session_state.essential = {}
    if "non_essential" not in st.session_state:
        st.session_state.non_essential = {}
    if "investment_country" not in st.session_state:
        st.session_state.investment_country = "Global"
    if "currency" not in st.session_state:
        st.session_state.currency = "USD"

    # Progress indicator
    progress = (st.session_state.step - 1) / 4
    st.progress(progress)
    st.write(f"Step {st.session_state.step} of 4")

    if st.session_state.step == 1:
        income_data = collect_income()
        if income_data:
            st.session_state.income = income_data
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        if st.button("← Back to Income"):
            st.session_state.step = 1
            st.rerun()
        essential_data = collect_essential_expenses()
        if essential_data:
            st.session_state.essential = essential_data
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        if st.button("← Back to Essentials"):
            st.session_state.step = 2
            st.rerun()
        non_essential_data = collect_non_essential_expenses()
        if non_essential_data:
            st.session_state.non_essential = non_essential_data
            st.session_state.step = 4
            st.rerun()

    elif st.session_state.step == 4:
        show_analysis_and_insights()

    # Reset button
    if st.button("Start Over"):
        st.session_state.step = 1
        st.session_state.income = {}
        st.session_state.essential = {}
        st.session_state.non_essential = {}
        st.session_state.investment_country = "Global"
        st.session_state.currency = "USD"
        st.rerun()


def show_analysis_and_insights() -> None:
    st.header("📊 Your Financial Analysis")
    
    income = st.session_state.income
    essential = st.session_state.essential
    non_essential = st.session_state.non_essential
    selected_currency = st.session_state.get('currency', 'USD')
    currency_symbol = get_currency_label(selected_currency)
    
    total_income = income.get('total', 0)
    total_essential = essential.get('total', 0)
    total_non_essential = non_essential.get('total', 0)
    total_expenses = total_essential + total_non_essential
    surplus = total_income - total_expenses
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Monthly Income ({selected_currency})", total_income)
    with col2:
        st.metric(f"Essential Expenses ({selected_currency})", total_essential)
    with col3:
        st.metric(f"Non-Essential Expenses ({selected_currency})", total_non_essential)
    with col4:
        st.metric(f"Surplus/Deficit ({selected_currency})", surplus, delta=surplus)

    # Expense breakdown bar chart - detailed
    st.subheader("💰 Detailed Expense Breakdown")
    
    # Create detailed breakdowns first
    essential_breakdown = {k: v for k, v in essential.items() if k != 'total' and v > 0}
    non_essential_breakdown = {k: v for k, v in non_essential.items() if k != 'total' and v > 0}
    
    # Combine all expenses
    all_expenses = {}
    all_expenses.update({f"Essential - {k.title()}": v for k, v in essential_breakdown.items()})
    all_expenses.update({f"Non-Essential - {k.title()}": v for k, v in non_essential_breakdown.items()})
    
    if all_expenses:
        st.bar_chart(all_expenses)
    else:
        st.info("No expenses entered yet.")
    
    st.markdown(f"### 🌍 Currency Selected: {selected_currency} ({currency_symbol})")
    
    # Detailed breakdown
    st.subheader("📋 Detailed Expenses")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Essential Expenses:**")
        for cat, amt in essential_breakdown.items():
            st.write(f"- {cat.title()}: ${amt:,.2f}")
    
    with col2:
        st.markdown("**Non-Essential Expenses:**")
        for cat, amt in non_essential_breakdown.items():
            st.write(f"- {cat.title()}: ${amt:,.2f}")
    
    # Budget analysis and recommendations
    st.markdown("---")
    if surplus < 0:
        st.error("🚨 You're spending more than you earn!")
        st.markdown("### 💡 Recommendations to Balance Your Budget")
        
        # Find highest expenses
        all_expenses = {**essential_breakdown, **non_essential_breakdown}
        highest_expense = max(all_expenses, key=all_expenses.get)
        highest_amount = all_expenses[highest_expense]
        
        st.markdown(f"**Your highest expense is {highest_expense.title()} at ${highest_amount:,.2f}**")
        st.markdown("Suggestions:")
        st.markdown("- Try reducing dining out and entertainment by 20-30%")
        st.markdown("- Look for cheaper alternatives for shopping")
        st.markdown("- Consider negotiating rent or finding a roommate")
        st.markdown("- Cut subscriptions you don't use regularly")
        
        # AI advice
        deficit = abs(surplus)
        ai_prompt = f"Monthly income: ${total_income}, expenses: ${total_expenses}, deficit: ${deficit}. Highest expense: {highest_expense} (${highest_amount}). Essential expenses: {', '.join([f'{k}:${v}' for k,v in essential_breakdown.items()])}. Non-essential: {', '.join([f'{k}:${v}' for k,v in non_essential_breakdown.items()])}. Give specific, actionable advice to reduce expenses and balance the budget. Suggest alternatives for high expenses."
        ai_advice = analyze_budget([], ai_prompt)
        st.markdown("### 🤖 AI Financial Advice")
        st.markdown(ai_advice)
        
    else:
        st.success("✅ Great! You're within budget.")
        st.markdown(f"### 💰 You have {currency_symbol}{surplus:,.2f} surplus each month")
        st.markdown(f"**Currency used for recommendations:** {selected_currency} ({currency_symbol})")
        
        # Investment recommendations
        st.markdown("### 📈 Recommended Investment Allocation")
        fd_amount = surplus * 0.5
        mf_amount = surplus * 0.2
        gold_amount = surplus * 0.2
        stocks_amount = surplus * 0.1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"🏦 Safe Deposits (50%) ({selected_currency})", fd_amount)
        with col2:
            st.metric(f"📊 Funds/ETFs (20%) ({selected_currency})", mf_amount)
        with col3:
            st.metric(f"🥇 Gold (20%) ({selected_currency})", gold_amount)
        with col4:
            st.metric(f"🏭 Stocks (10%) ({selected_currency})", stocks_amount)
        
        st.markdown("---")
        st.markdown("### 💡 Investment Allocation Strategy")
        st.markdown("""
        Based on your monthly surplus, here's the recommended allocation:
        
        - **🏦 50% - Safe Deposits (50% of surplus)**: Bank FDs, savings accounts, government bonds for guaranteed returns
        - **📊 20% - Mutual Funds/ETFs (20% of surplus)**: Diversified equity funds for long-term growth
        - **🥇 20% - Gold & Precious Metals (20% of surplus)**: Gold ETFs, bonds, or bullion as inflation hedge
        - **🏭 10% - Individual Stocks (10% of surplus)**: Direct equity investments for higher growth potential
        
        This balanced approach provides:
        ✓ Capital safety (50% in secure assets)
        ✓ Growth opportunity (30% in equities)
        ✓ Inflation protection (20% in gold)
        """)
        
        st.markdown("---")
        
        invest_prompt = f"""Monthly surplus: {currency_symbol}{surplus:,.2f} ({selected_currency}).
        
        Provide personalized investment strategy considering:
        - User's monthly surplus allocation: Safe Deposits 50%, Funds/ETFs 20%, Gold 20%, Stocks 10%
        - Risk assessment and diversification
        - Tax implications for different investment types
        - Current market conditions and outlook
        
        Give specific, actionable advice on how to implement this allocation strategy."""
        
        invest_advice = analyze_budget([], invest_prompt)
        st.markdown("### 🤖 AI Investment Recommendations")
        st.markdown(invest_advice)


if __name__ == "__main__":
    main()
