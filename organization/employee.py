import logging

from flask import (
    render_template, redirect, request, url_for,
    flash, Blueprint, jsonify, make_response
)
from flask_login import (
    login_required, current_user, fresh_login_required
)
from sqlalchemy.exc import IntegrityError, OperationalError
from functools import wraps

from . import db
from .forms import (
    CityDetailForm, CityDetailForm,
    ContactAddressForm, SearchEmployeeForm, UpdateContactAddressForm
)
from .models import (
    City, ContactAddress, Employee, Roles
)


employee_logger = logging.getLogger()

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')


def superuser_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash("You don't have permission to view this page", "warning")
            return redirect(url_for("main.page_not_found"))

        return func(*args, **kwargs)

    return decorated_function


@employee_bp.route("/<int:e_id>/profile")
@login_required
def employee_profile(e_id):
    if int(e_id) != int(current_user.get_id()) and not current_user.is_admin():
        employee_logger.debug(f"current user is admin: {not current_user.is_admin()}")
        employee_logger.warning(f"Trying to access invalid url !")
        return redirect(url_for("main.page_not_found"))

    employee_auth = Employee.query.filter_by(e_id=e_id).first()
    employee_contact_details = ContactAddress.query.filter_by(e_id=e_id).first()
    return render_template(
        'employee/profile_page.html',
        employee_contact=employee_contact_details,
        employee_auth=employee_auth
    )


@employee_bp.route("/<int:e_id>/profile/update-details", methods=["GET", "POST"])
@login_required
def update_profile(e_id):
    if int(e_id) != int(current_user.get_id()) and (not current_user.is_admin()):
        employee_logger.warning(f"Trying to access invalid url !")
        return redirect(url_for("main.page_not_found"))

    _is_contact_present = ContactAddress.query.filter_by(e_id=e_id).first()
    if _is_contact_present:
        # old user details update form
        contact_address_form = UpdateContactAddressForm()
    else:
        # new user details update form
        contact_address_form = ContactAddressForm()

    city_form = CityDetailForm()
    employee_auth_details = Employee.query.filter_by(e_id=e_id).first()
    if contact_address_form.validate_on_submit() and city_form.validate_on_submit():
        if City.query.filter_by(pin_code=city_form.pin_code.data).first() is None:
            # if pincode no found in city table then entry new details
            employee_logger.warning(f"Pin code: {city_form.pin_code.data} is not present in City table !")
            update_city_and_pin = City(
                city_name=city_form.city_name.data,
                pin_code=city_form.pin_code.data
            )
            try:
                db.session.add(update_city_and_pin)
                db.session.commit()
                employee_logger.info(f"Pin code: {city_form.pin_code.data} is added to City Table !")
            except IntegrityError as err:
                db.session.rollback()
                employee_logger.critical(f"Unable to add City: {city_form.city_name.data} and Pin code: {city_form.pin_code.data} in City table!")
                employee_logger.critical(f"{err} Error occured!\n database transaction failed !")
                flash(f"Unable to add city: {city_form.city_name.data} and pin code: {city_form.pin_code.data} !", category="danger")
                return redirect(url_for('employee.update_profile', e_id=employee_auth_details.get_id()))
            employee_logger.info(f"City: {city_form.city_name.data} and Pin code: {city_form.pin_code.data} added to City table.")
        
        city_table_id = City.query.filter_by(pin_code=city_form.pin_code.data).first().cp_id

        details_to_update = ContactAddress.query.filter_by(e_id=e_id).first()
        if _is_contact_present:
            employee_logger.debug(f"Started to update @{employee_auth_details.username}'s contact_address table...")
            details_to_update.firstname = contact_address_form.firstname.data
            details_to_update.lastname = contact_address_form.lastname.data
            details_to_update.date_of_birth = contact_address_form.date_of_birth.data
            details_to_update.addressLine = contact_address_form.addressLine.data
            details_to_update.cp_id = city_table_id
        else:
            employee_logger.debug(f"Trying to insert {employee_auth_details.username}'s new details into contact_address table...")
            details_to_update = ContactAddress(
                firstname=contact_address_form.firstname.data,
                lastname=contact_address_form.lastname.data,
                email=contact_address_form.email.data,
                phone_number=contact_address_form.phone_number.data,
                date_of_birth=contact_address_form.date_of_birth.data,
                addressLine=contact_address_form.addressLine.data,
                cp_id=city_table_id,
                e_id=e_id,
            )

        try:
            db.session.add(details_to_update)
            db.session.commit()
            employee_logger.info(f"{employee_auth_details.username}'s contact details has been updated.")
            flash(f"{employee_auth_details.username}'s Profile Details Updated Successfully!", category="success")
            return redirect(url_for("employee.employee_profile", e_id=e_id))
        except IntegrityError as err:
            db.session.rollback()
            employee_logger.critical(f"Unable to update {employee_auth_details.username}'s contact_address details !")
            
            # delete recent added city details
            current_added_city_detail = City.query.filter_by(cp_id=city_table_id).first()
            db.session.delete(current_added_city_detail)
            db.session.commit()
            employee_logger.critical(f"City: {current_added_city_detail.city_name} Pin code: {current_added_city_detail.pin_code} deleted from City table")
            employee_logger.critical(f"{err} Error occurred!\n database transaction failed !")

            flash(f"Unable to update {employee_auth_details.username}'s profile details!", category="danger")
            return redirect(url_for('employee.update_profile', e_id=e_id))
    
    if contact_address_form.errors != {}:
        employee_logger.warning(f"@{current_user.username} - Validation errors in ContactAddressForm !")
        for error_msg in contact_address_form.errors.values():
            employee_logger.warning(f"@{current_user.username} - {error_msg[0]}")
            flash(f"{error_msg[0]}", category="danger")
    if city_form.errors != {}:
        employee_logger.warning(f"@{current_user.username} - Validation errors in CityForm !")
        for error_msg in city_form.errors.values():
            employee_logger.warning(f"@{current_user.username} - {error_msg[0]}")
            flash(f"{error_msg[0]}", category="danger")

    employee_contact_details = ContactAddress.query.filter_by(e_id=e_id).first()
    employee_auth_details = Employee.query.filter_by(e_id=e_id).first()
    context = {
        'contact_address_form': contact_address_form,
        'city_form': city_form,
        'employee_auth': employee_auth_details,
        'employee_contact_details': employee_contact_details,
    }

    return render_template("employee/update_contact_details_page.html", context=context)


@employee_bp.route("/master")
@login_required
def master_page():
    """
    View for all employee profile details
    - admin can see and edit each employee profile detail except email and phone
    - employee_profile_details: list -> [ employee_detail: tuple ]
        index ref for employee view:
        0: employee id
        1: employee username
        2: employee firstname
        3: employee lastname
        4: employee email
        5: employee city name
        6. Employee admin status

        index ref for admin view:
        0: employee id
        1: employee username
        2: employee firstname
        3: employee lastname
        4: employee email
        5: employee city name
        6: Active employee status
        7: Employee admin status
    """
    searchForm = SearchEmployeeForm()
    employees = ContactAddress.query.order_by(ContactAddress.e_id).all()
    employee_profile_details = list()
    if current_user.is_admin():
        for employee in employees:
            employee_auth = Employee.query.filter_by(e_id=employee.e_id).first()
            employee_city = City.query.filter_by(cp_id=employee.cp_id).first()
            employee_detail = (
                employee.e_id,
                employee_auth.username,
                employee.firstname,
                employee.lastname,
                employee.email,
                employee_city.city_name,
                employee_auth.is_active_employee(),
                employee_auth.is_admin(),
            )
            employee_profile_details.append(employee_detail)
    else:
        for employee in employees:
            employee_auth = Employee.query.filter_by(e_id=employee.e_id).first()
            # condition to opt out inactive employee
            if current_user.is_admin() or employee_auth.is_active_employee():
                employee_city = City.query.filter_by(cp_id=employee.cp_id).first()
                employee_detail = (
                    employee.e_id,
                    employee_auth.username,
                    employee.firstname,
                    employee.lastname,
                    employee.email,
                    employee_city.city_name,
                    employee_auth.is_admin()
                )
                employee_profile_details.append(employee_detail)

    context = {
        'employee_profile_details': employee_profile_details,
    }

    if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
        return render_template("employee/master_page.html", context=context, searchForm=searchForm)
    else:
        return make_response(jsonify(context))


@employee_bp.route("/search", methods=["POST"])
@login_required
def search_employee():
    _city = City.query
    _employee_contact = ContactAddress.query
    _employee_auth_detail = Employee.query
    _search_result_employees = list()
    context = {}
    if request.method == "POST":
        _searched_text = request.form['searched']

        context['searched-keyword'] = _searched_text  # add search item to context

        # sql query like text
        _searched_text = f"%{_searched_text}%"
        # city search
        cities = _city.filter(City.city_name.like(_searched_text))    # get cities
        cities = cities.order_by(City.pin_code).all()

        # username search
        auths = _employee_auth_detail.filter(Employee.username.like(_searched_text))    # get usernames
        auths = auths.order_by(Employee.e_id).all()

        if cities is None and auths is None:
            return jsonify("no data found !")

        if len(auths) == 0:
            for city in cities:
                # filter all employees by city id
                employees_contact_in_city = _employee_contact.order_by(
                    ContactAddress.e_id
                ).filter_by(cp_id=city.cp_id).all()  # -> list
                # Create search data for each employee
                for employee in employees_contact_in_city:
                    employee_db_obj = _employee_auth_detail.filter_by(e_id=employee.e_id).first()
                    # condition to opt out inactive employee
                    if current_user.is_admin() or employee_db_obj.is_active_employee():
                        employee_details = (
                            employee.e_id,
                            employee_db_obj.username,
                            employee.firstname,
                            employee.lastname,
                            employee.email,
                            _city.filter_by(cp_id=employee.cp_id).first().city_name,
                            employee_db_obj.is_active_employee(),
                            employee_db_obj.is_admin()
                        )
                        _search_result_employees.append(employee_details)
        elif len(cities) == 0:
            for employee_auth in auths:
                # condition to opt out inactive employee
                if current_user.is_admin() or employee_auth.is_active_employee():
                    # filter all employees by username
                    employees_contact_by_username = _employee_contact.filter_by(
                        e_id=employee_auth.e_id).all()  # -> list
                    for employee in employees_contact_by_username:
                        employee_details = (
                            employee_auth.e_id,
                            employee_auth.username,
                            employee.firstname,
                            employee.lastname,
                            employee.email,
                            _city.filter_by(cp_id=employee.cp_id).first().city_name,
                            employee_auth.is_active_employee(),
                            employee_auth.is_admin()
                        )
                        _search_result_employees.append(employee_details)

        context['employee_profile_details'] = _search_result_employees
        if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
            return render_template('employee/search.html', context=context)
        else:
            return jsonify(context)


@employee_bp.route("/<int:e_id>/make-admin", methods=["PUT", "POST"])
@login_required
@superuser_required
def make_admin(e_id):
    json_value = {'message': 'Bad request !\nUnable to make new permissions !'}
    employee = Employee.query.filter_by(e_id=e_id).first()
    admin_role = Roles.query.filter_by(role='admin').first()
    if employee is None:
        employee_logger.critical(f"Employee ID: {e_id} not found.")
        flash(f"Employee ID: {e_id} not found.", category="danger")
        return redirect(url_for("employee.master_page"))
    try:
        if current_user.is_admin() and int(current_user.get_id()) != int(e_id) and not employee.is_admin():
            if admin_role is not None:
                employee.role_id = admin_role.role_id
                employee_logger.info(f"{employee.username}'s role change to admin !")
            else:
                employee_logger.critical("No admin role found.")

            db.session.add(employee)
            db.session.commit()
            employee_logger.info(f"{employee.username}'s role change to admin !")
            flash(f"{employee.username}'s role change to admin !", category="success")
            json_value['message'] = f"{employee.username}'s role change to admin !"
        else:
            flash(f"Employee can not add permission to himself !", category="danger")
            employee_logger.debug(f"Employee can not add permission to himself or Employee is already an admin !")
            json_value['message'] = f"Employee can not add permission to himself or Employee is already an admin !"

    except (IntegrityError, OperationalError) as err:
        db.session.rollback()
        flash(f"Unable to make new permissions !", category="danger")
        employee_logger.critical(f"Unable to make new permissions !\n{err}")
        json_value['message'] = f"Unable to make new permissions !"
    finally:
        if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
            return redirect(url_for("employee.master_page"))
        else:
            return make_response(jsonify(json_value))


@employee_bp.route("/<int:e_id>/make-employee", methods=["PUT", "POST"])
@login_required
@superuser_required
def make_employee(e_id):
    json_value = {'message': 'Bad request !\nUnable to make new permissions !'}
    employee = Employee.query.filter_by(e_id=e_id).first()
    employee_role = Roles.query.filter_by(role='employee').first()
    if employee is None:
        employee_logger.critical(f"Employee ID: {e_id} not found.")
        return redirect(url_for("employee.master_page"))
    try:
        if current_user.is_admin() and employee.is_admin() and int(current_user.get_id()) != int(e_id):
            if employee_role is not None:
                employee.role_id = employee_role.role_id
                employee_logger.info(f"{employee.username}'s role change to employee !")
            else:
                employee_logger.critical("No employee role found !")
            db.session.add(employee)
            db.session.commit()
            employee_logger.info(f"{employee.username}'s role change to employee !")
            flash(f"{employee.username}'s role change to employee !", category="warning")
            json_value['message'] = f"{employee.username}'s role change to employee !"
        else:
            flash(f"Employee can not add permission to himself !", category="danger")
            employee_logger.debug(f"Employee can not add permission to himself !")
            json_value['message'] = f"Employee can not add permission to himself !"

    except IntegrityError as err:
        db.session.rollback()
        flash(f"Unable to make new permissions !", category="danger")
        employee_logger.critical(f"Unable to make new permissions !")
        json_value['message'] = f"Unable to make new permissions !"
    finally:
        if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
            return redirect(url_for("employee.master_page"))
        else:
            return make_response(jsonify(json_value))


@employee_bp.route("/<int:e_id>/remove-employee", methods=["PUT", "POST"])
@login_required
@superuser_required
def remove_employee(e_id):
    json_value = {'message': 'Bad request !\nUnable to make new permissions !'}
    if request.method == 'POST' or request.method == 'PUT':
        employee = Employee.query.filter_by(e_id=e_id).first()
        if employee is None:
            employee_logger.critical(f"Employee ID: {e_id} not found.")
            return redirect(url_for("employee.master_page"))
        if employee.role_id is None:
            employee_logger.critical(f"{employee.username} is not an active employee !")
            return redirect(url_for("employee.master_page"))
        try:
            if current_user.is_admin() and int(current_user.get_id()) != int(e_id):
                employee.role_id = None
                employee_logger.info(f"{employee.username}'s role has been removed and is now inactive employee !")
                db.session.add(employee)
                db.session.commit()
                employee_logger.info(f"{employee.username}'s role has been removed and is now inactive employee !")
                flash(f"{employee.username}'s role has been removed and is now inactive employee !", category="warning")
                json_value['message'] = f"{employee.username}'s role has been removed and is now inactive employee !"
            else:
                flash(f"Employee can not add permission to himself !", category="danger")
                employee_logger.debug(f"Employee can not remove himself !")
                json_value['message'] = f"Employee can not add permission to himself !"
        except IntegrityError as err:
            db.session.rollback()
            flash(f"Unable to remove employee !", category="danger")
            employee_logger.critical(f"{err} \n Unable to remove employee !")
            json_value['message'] = f"Unable to remove employee !"
        finally:
            if 'Mozilla' in request.headers['User-Agent']:  # true if request made by any browser
                return redirect(url_for("employee.master_page"))
            else:
                return make_response(jsonify(json_value))
