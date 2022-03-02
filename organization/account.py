import base64
import logging
from datetime import timedelta

from flask import (
    render_template, redirect, session, url_for,
    flash, Blueprint, jsonify, request, make_response
)
from flask_login import (
    login_user, logout_user, current_user, login_required
)
from sqlalchemy.exc import IntegrityError, OperationalError

from . import db
from .forms import (
    RegisterEmployeeForm, LoginForm
)
from .models import (
    Employee, Roles
)

account_logger = logging.getLogger()

account_bp = Blueprint('account', __name__, url_prefix='/account')


def login_by_api(request_by_api):
    """This login function invoked whenever an api call is made"""
    json_value = {'message': 'Please Login!'}
    if current_user.is_authenticated:
        json_value['message'] = f"{current_user.username} is already logged in !"
        return jsonify(json_value)
    if request_by_api.method == 'POST':
        try:
            auth_details = request_by_api.headers.get('Authorization')
            if auth_details:
                api_key = auth_details.replace('Basic ', '', 1)
                request_username = ''
                request_password = ''
                try:
                    api_key = base64.b64decode(api_key)
                    request_username = str(str(api_key).split(":")[0]).lstrip("b'")
                    request_password = str(str(api_key).split(":")[1]).rstrip("'")
                except TypeError:
                    pass
                attempted_employee = Employee.query.filter_by(username=request_username).first()
                if not attempted_employee:
                    account_logger.warning(f"Employee not found >>>>>>>>> {attempted_employee}")
                if attempted_employee and attempted_employee.check_password(attempted_password=request_password):
                    if attempted_employee.is_active_employee():  # True if employee is active
                        login_user(attempted_employee)
                        account_logger.debug(f"Success! {attempted_employee.username} is now logged in.")
                        json_value['message'] = f"Success! {attempted_employee.username} is now logged in."
                        return jsonify(json_value)
                    else:  # else employee is inactive
                        account_logger.warning(
                            f"Warning! removed user - '{attempted_employee.username}' is trying to sign in !")
                        json_value['message'] = f"Warning! {attempted_employee.username} is no longer an employee !"
                        return jsonify(json_value)
                else:
                    account_logger.debug(f"Username or Password is not match! Please try Again")
                    json_value['message'] = "Username or Password is not match! Please try Again"
        except OperationalError:
            account_logger.debug(f"Invalid Username !")
            json_value['message'] = f"Invalid Username ! Try again"
            return jsonify(json_value)

    return jsonify(json_value)


@account_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash(f"{current_user.username} is already logged in !", category="warning")
        return redirect(url_for("home"))
    form = RegisterEmployeeForm()
    if form.validate_on_submit():
        try:
            employee_role = Roles.query.filter_by(role='employee').first().role_id
            if employee_role is None:
                account_logger.warning("Employee role is set to None !")
            employee_to_register = Employee(
                username=form.username.data,
                password=form.password1.data,
                role_id=employee_role,
            )

            db.session.add(employee_to_register)
            db.session.commit()
            account_logger.info("Employee added to database.")

            # After successful registration login that employee
            login_user(employee_to_register)

            account_logger.debug(f"{employee_to_register.username} is logged in.")

            flash(
                f"Employee Account Created Successfully! {employee_to_register.username} is now logged in",
                category="success"
            )

            return redirect(
                url_for(
                    "employee.update_profile",
                    e_id=current_user.get_id()
                )
            )
        except (IntegrityError, OperationalError) as e:
            db.session.rollback()
            account_logger.critical(f"{e} Error occurred!\n database transaction failed !")

    if form.errors != {}:
        account_logger.debug(f"Errors while registering employee !")
        for error_msg in form.errors.values():
            account_logger.debug(f"{error_msg[0]}")
            flash(f"{error_msg[0]}", category="danger")

    context = {
        'auth_form': form,
    }

    return render_template("account/register.html", context=context)


@account_bp.route("/login", methods=["GET", "POST"])
def login_page():
    try:
        if 'Mozilla' in request.headers['User-Agent']:   # true if request made by any browser
            if current_user.is_authenticated:
                flash(f"{current_user.username} is already logged in !", category="info")
                return redirect(url_for("home"))

            form = LoginForm()
            if form.validate_on_submit():
                try:
                    attempted_employee = Employee.query.filter_by(username=form.username.data).first()
                    if attempted_employee and attempted_employee.check_password(
                            attempted_password=form.password.data
                    ):
                        if attempted_employee.is_active_employee():  # True if employee is active
                            login_user(attempted_employee)
                            account_logger.debug(f"Success! {attempted_employee.username} is now logged in.")
                            flash(f"Success! {attempted_employee.username} is now logged in.", category="success")
                            return redirect(url_for("home"))
                        else:  # else employee is inactive
                            account_logger.warning(
                                f"Warning! removed user - '{attempted_employee.username}' is trying to sign in !")
                            flash(
                                f"Warning! {attempted_employee.username} is no longer an employee !",
                                category="danger"
                            )
                            return redirect(url_for("account.login_page"))
                    else:
                        account_logger.debug(f"Username or Password is not match! Please try Again")
                        flash("Username or Password is not match! Please try Again", category="danger")
                except OperationalError:
                    account_logger.debug(f"Invalid Username !")
                    flash(f"Invalid Username ! Try again", category="danger")
                    return redirect(url_for("account.login_page"))

            return render_template("account/login.html", form=form)
        else:   # true if request made by any api
            json_obj = login_by_api(request)
            return make_response(json_obj)
    except TypeError as err:
        return redirect(url_for("main.server_error_page"))


@account_bp.route("/logout")
@login_required
def logout_page():
    json_value = {'message': ''}
    employee = current_user.username
    logout_user()
    account_logger.debug(f"{employee}, has been logged out")
    json_value['message'] = f"{employee}, has been logged out"
    if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
        flash(f"{employee}, you have been logged out", category="info")
        return redirect(url_for("home"))
    else:
        return make_response(jsonify(json_value))



