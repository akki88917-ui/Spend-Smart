from flask import Blueprint, render_template, session, request, redirect, url_for
from app.database.connection import get_db
from datetime import datetime
import calendar as _cal

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def index():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login'))
        
    selected = request.args.get("month", datetime.now().strftime("%Y-%m"))

    conn = get_db()

    income_months = conn.execute("SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM incomes WHERE user_id = %s", (uid,)).fetchall()
    expense_months = conn.execute("SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM expenses WHERE user_id = %s", (uid,)).fetchall()

    months_set = {row['m'] for row in income_months if row['m']} | {row['m'] for row in expense_months if row['m']}
    months = sorted(list(months_set), reverse=True)

    daily_exp_rows = conn.execute("""
        SELECT TO_CHAR(date, 'DD') as d, SUM(amount) as total
        FROM expenses
        WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s
        GROUP BY TO_CHAR(date, 'DD')
    """, (uid, selected)).fetchall()

    daily_trend = {row['d']: float(row['total']) for row in daily_exp_rows}

    sm_income_row = conn.execute("SELECT SUM(amount) as total FROM incomes WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s", (uid, selected)).fetchone()
    sm_income = float(sm_income_row['total']) if sm_income_row and sm_income_row['total'] else 0.0

    sm_expense_row = conn.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s", (uid, selected)).fetchone()
    sm_expense = float(sm_expense_row['total']) if sm_expense_row and sm_expense_row['total'] else 0.0

    sm_saved = sm_income - sm_expense

    budget_row = conn.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s", (uid, selected)).fetchone()
    monthly_budget = float(budget_row['amount']) if budget_row and budget_row['amount'] else 0.0
    budget_used_percent = round(min(100.0, (sm_expense / monthly_budget) * 100.0), 1) if monthly_budget > 0 else 0.0

    cat_rows = conn.execute("""
        SELECT c.name as category, SUM(e.amount) as total
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s AND TO_CHAR(e.date, 'YYYY-MM') = %s
        GROUP BY c.name
    """, (uid, selected)).fetchall()
    
    category_data = {row['category']: float(row['total']) for row in cat_rows}

    conn.close()

    return render_template(
        'analytics.html', 
        months=months, 
        selected=selected, 
        income=sm_income, 
        expense=sm_expense, 
        sm_saved=sm_saved,
        daily_trend=daily_trend,
        monthly_budget=monthly_budget,
        budget_used_percent=budget_used_percent,
        category_data=category_data
    )
