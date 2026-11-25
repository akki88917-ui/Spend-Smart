from flask import Blueprint, render_template, session, request
from flask_login import login_required
from app.database.connection import get_db
from datetime import datetime
import calendar as _cal

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    uid = session.get('user_id')
    selected = request.args.get("month", datetime.now().strftime("%Y-%m"))

    with get_db() as conn:
        # 1. Fetch distinct months where user has transactions
        income_months = conn.execute(
            "SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM incomes WHERE user_id = %s", (uid,)
        ).fetchall()

        expense_months = conn.execute(
            "SELECT
