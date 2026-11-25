from flask import Blueprint, render_template, session, request
from flask_login import login_required
from app.database.connection import get_db
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
# @login_required
def index():
    uid = session.get('user_id')
    selected = request.args.get("month", datetime.now().strftime("%Y-%m"))

    with get_db() as conn:
        income_months = conn.execute(
            "SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM incomes WHERE user_id = %s", (uid,)
        ).fetchall()
        expense_months = conn.execute(
            "SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM expenses WHERE user_id = %s", (uid,)
        ).fetchall()

        months_set = {row['m'] for row in income_months if row['m']} | {row['m'] for row in expense_months if row['m']}
        months = sorted(list(months_set), reverse=True)

        daily_exp_rows = conn.execute("""
            SELECT TO_CHAR(date, 'DD') as d, SUM(amount) as total
            FROM expenses
            WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s
            GROUP BY TO_CHAR(date, 'DD')
        """, (uid, selected)).fetchall()

        daily_trend = {row['d']: float(row['total']) for row in daily_exp_rows}

        total_income = conn.execute("SELECT SUM(amount) as total FROM incomes WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s", (uid, selected)).fetchone()
        income = float(total_income['total']) if total_income and total_income['total'] else 0.0

        total_expense = conn.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s AND TO_CHAR(date, 'YYYY-MM') = %s", (uid, selected)).fetchone()
        expense = float(total_expense['total']) if total_expense and total_expense['total'] else 0.0

        return render_template('analytics.html', months=months, selected=selected, income=income, expense=expense, daily_trend=daily_trend)
