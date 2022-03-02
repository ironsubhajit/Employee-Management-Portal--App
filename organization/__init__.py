from datetime import timedelta

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Database instance
db = SQLAlchemy()

# Database Migration
migrate = Migrate()

# User login manager instance
login_manager = LoginManager()

# bcrypt instance for password encrypting
bcrypt = Bcrypt()


def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object('config.DevConfig')
        app.permanent_session_lifetime = timedelta(seconds=app.config['SESSION_ALIVE_SECONDS'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from organization import (account, employee, main)

    # DataBase object instance
    from organization.models import (
        City, Employee,
        Roles, ContactAddress
    )

    db.init_app(app)

    migrate.init_app(app, db, render_as_batch=True)

    # password encryption
    bcrypt.init_app(app)

    # login manager configuration
    login_manager.init_app(app)

    # Blueprints
    app.register_blueprint(main.main_bp)
    app.register_blueprint(account.account_bp)
    app.register_blueprint(employee.employee_bp)

    app.add_url_rule('/', endpoint='home')

    # Login view route
    login_manager.login_view = "account.login_page"
    login_manager.login_message_category = "info"

    # Fresh Login routes
    login_manager.refresh_view = "account.login_page"
    with app.app_context():
        db.create_all()
        return app


# @app.shell_context_processor
# def make_shell_context():
#     return dict(
#         db=db,
#         City=City,
#         Employee=Employee,
#         Roles=Roles,
#         ContactAddress=ContactAddress
#     )
