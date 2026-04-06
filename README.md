# AI Personal Finance Advisor

A comprehensive Streamlit app that helps you track expenses, visualize spending patterns, analyze budgets, and get personalized investment recommendations using Google Gemini AI or a local fallback.

## What this project does

- Interactive questionnaire to collect income and expense data
- **Currency selection** for global financial guidance
- Visualize spending with detailed bar charts showing all expense categories
- Analyze budget vs. expenses automatically
- Provide **simple, proven investment allocation strategy**:
  - **50% - Safe Deposits**: Bank FDs, savings accounts, government bonds
  - **20% - Mutual Funds/ETFs**: Diversified equity funds for growth
  - **20% - Gold**: Gold ETFs, bonds, or bullion for inflation protection
  - **10% - Stocks**: Direct equity investments for higher returns
- AI-powered personalized recommendations based on your surplus
- Guide users through financial planning with actionable advice

## Why this is a great project for your GitHub

- User-friendly interface with no data preparation needed
- Proven investment allocation model (modern portfolio theory)
- Complete financial advisory workflow from data collection to strategy
- Combines data visualization, AI analysis, and interactive UX
- Practical application helping global users manage personal finances
- Simple, clear recommendations that are easy to understand and implement
- Great portfolio fit for fintech, data science, and AI applications

## Setup

1. Create a new Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate       # Windows PowerShell
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. (Optional) Add your Google Gemini key.

   Option A: set the environment variable directly in PowerShell:

   ```powershell
   $env:GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
   ```

   Option B: create a `.env` file in the project root with:

   ```text
   GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
   ```

   To get a valid Gemini API key:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key (it should start with "AIza...")

   The app loads `.env` automatically and `.env` is already ignored by `.gitignore`.

4. Run the app.

```bash
streamlit run app.py
```

## Usage

1. **Select your currency** (for global financial guidance)
2. **Answer step-by-step questions** about your monthly income and expenses
3. **View detailed expense visualizations** with category breakdowns
4. **Get automatic budget analysis** and spending insights
5. **If you have surplus funds**, see the recommended allocation:
   - 50% to safe deposits (banks, bonds, guaranteed returns)
   - 20% to mutual funds/ETFs (diversified growth)
   - 20% to gold (inflation hedge)
   - 10% to individual stocks (high growth potential)
6. **Receive personalized AI recommendations** based on your surplus amount

## Key Features

- **Simple Allocation**: Easy-to-understand 50-20-20-10 strategy
- **Flexible by Amount**: Scales perfectly to any surplus amount
- **Risk-Balanced**: Mix of safety (50%), growth (30%), and protection (20%)
- **Global Friendly**: Works with multiple currencies for international users
- **AI-Powered**: Get personalized advice from Google Gemini AI

## File overview

- `app.py` — Streamlit user interface
- `finance_ai.py` — Gemini wrapper and local analysis engine
- `requirements.txt` — Python dependencies
- `.gitignore` — Common ignored files

## Notes

- The app is intentionally small and portable for GitHub showcase.
- Without a Gemini API key, the app still generates smart offline suggestions.
- With a key, it connects to Google Gemini to produce richer finance feedback.
