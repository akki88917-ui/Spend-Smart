# app/routes/analytics.py
from flask import Blueprint, request, request, session

from flask import Flask, request, render_template, abort
from flask_login import login_required
from app.database.connection import get_db
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    # ------- PREPARATION -------------------------------------------------------
    uid = session.get('user_id')
    selected_month = request.args.get('month', None)

    # If month param missing → use current month (e.g. 2026-11)
    if not selected:
        selected = datetime.now().strftime("%Y-%m")  # <-- will be year-month

    uid = session['user_id']

    # ---------------------------------------------------------------
    # Paste the SELECT with correct PLACEHOLDERS (%s) and PostgreSQL weekday
    daily_exp_rows = conn.execute("""
        SELECT strftime('%Y-%m','%Y-%m') as month_str,
            DATE(datetime) as d
        FROM expenses
        WHERE user_id = ?
        ORDER BY datetime
    """, (uid, selected)).fetchall()

    # Wrap the result for use in the template
    total_monthly_expenses = sum[row['total'] for row in daily_exp_rows]
   
