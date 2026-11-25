from flask import Blueprint, redirect, url_for

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def index():
    return redirect(url_for('home.index'))
