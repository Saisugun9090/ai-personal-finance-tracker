import os
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


def parse_uploaded_csv(uploaded_file) -> List[Dict[str, object]]:
    import pandas as pd
    from datetime import datetime

    df = pd.read_csv(uploaded_file)
    if "Amount" not in df.columns:
        raise ValueError("CSV must include at least an Amount column.")

    expenses = []
    for _, row in df.iterrows():
        date = str(row.get("Date", datetime.now().date().isoformat()))
        category = str(row.get("Category", "")).strip() or "Other"
        description = str(row.get("Description", "")).strip() or "Expense"
        amount = float(row["Amount"])
        expenses.append(
            {
                "Date": date,
                "Category": category,
                "Description": description,
                "Amount": amount,
            }
        )
    return expenses


def format_expenses_for_display(expenses: List[Dict[str, object]]):
    import pandas as pd

    df = pd.DataFrame(expenses)
    if "Amount" in df.columns:
        df["Amount"] = df["Amount"].astype(float).map("${:,.2f}".format)
    return df


def _build_prompt(expenses: List[Dict[str, object]], user_goal: str) -> str:
    lines = [
        "You are a helpful personal finance coach.",
        "Review the user's expenses and give them a short budget summary, spending categories, savings ideas, and an action plan.",
        f"Goal: {user_goal}",
        "Expenses:",
    ]
    for item in expenses:
        lines.append(
            f"{item['Date']} | {item['Category']} | {item['Description']} | ${item['Amount']:.2f}"
        )
    lines.append(
        "\nPlease return:\n1. A quick spending overview\n2. The three most important recommendations\n3. One budgeting action to take this week\n4. A friendly tone"
    )
    return "\n".join(lines)


def _get_gemini_response(prompt: str) -> Optional[str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or genai is None:
        return None

    try:
        genai.configure(api_key=api_key)
        model_name = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-1.0-pro")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Log the error but don't crash - fallback to local analysis
        print(f"Gemini API error: {e}")
        return None


def _local_budget_analysis(expenses: List[Dict[str, object]], user_goal: str) -> str:
    total = sum(item["Amount"] for item in expenses)
    category_totals = {}
    for item in expenses:
        category_totals[item["Category"]] = category_totals.get(item["Category"], 0.0) + item["Amount"]

    sorted_categories = sorted(category_totals.items(), key=lambda pair: pair[1], reverse=True)
    top_categories = sorted_categories[:3]
    high_spend = [name for name, amt in top_categories if amt / total > 0.2]

    lines = [
        "### Local finance summary",
        f"Total spend: ${total:,.2f}",
        f"Analyzed {len(expenses)} expense rows.",
        "\n**Top categories:**",
    ]
    for name, amt in top_categories:
        lines.append(f"- {name}: ${amt:,.2f} ({amt / total:.0%})")

    lines.append("\n**Recommendations:**")
    if high_spend:
        lines.append(
            f"- Your biggest spend categories are {', '.join(high_spend)}. Try setting a weekly limit for these categories."
        )
    else:
        lines.append("- Your spending looks fairly balanced. Track variable expenses like dining and entertainment closely.")

    lines.append(f"- Goal focus: {user_goal}")
    lines.append("- Create a simple weekly budget: set one saving target, reduce one non-essential purchase, and review your next pay period.")
    return "\n".join(lines)


def analyze_budget(expenses: List[Dict[str, object]], user_goal: str) -> str:
    if not expenses:
        # For investment or general advice without expenses
        prompt = f"You are a helpful personal finance coach. {user_goal} Provide specific, actionable advice."
        gemini_answer = _get_gemini_response(prompt)
        if gemini_answer:
            return gemini_answer
        return "Please provide more details for personalized advice."
    
    prompt = _build_prompt(expenses, user_goal)
    gemini_answer = _get_gemini_response(prompt)
    if gemini_answer:
        return gemini_answer
    return _local_budget_analysis(expenses, user_goal)
