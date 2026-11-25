from flask import Flask, render_template, session, redirect, url_for
from flask_login import LoginManager
from .config import Config
from .database.connection import close_db, ensure_schema

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # User loader for Flask-Login
    from app.database.connection import get_db
    @login_manager.user_loader
    def load_user(user_id):
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
            return user # Assuming your User object handles this

    # --- Static Files Optimization (Render) ---
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/')

    # --- Jinja Filters ---
    @app.template_filter('format_date')
    def format_date_filter(value):
        if not value: return ""
        if hasattr(value, 'strftime'): return value.strftime('%Y-%m-%d')
        return str(value).split(' ')[0]

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.analytics import analytics_bp
    from .routes.transactions import transactions_bp
    from .routes.budgets import budgets_bp
    from .routes.export import export_bp
    from .routes.goals import goals_bp
    from .routes.home import home_bp
    from .routes.account import account_bp
    from .routes.recurring import recurring_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(recurring_bp)

    ensure_schema(app)

    @app.route("/")
    def landing():
        if "user_id" in session:
            return redirect(url_for("home.index"))
        return render_template("landing.html")

    app.teardown_appcontext(close_db)
    return app
