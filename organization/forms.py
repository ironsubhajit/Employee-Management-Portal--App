import logging
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    StringField, EmailField, PasswordField,
    IntegerField, DateField,
    SubmitField
)
from wtforms.validators import (
    Length, EqualTo, Email,
    DataRequired, ValidationError,
)
from .models import (
    Employee, ContactAddress
)


forms_logger = logging.getLogger()


def check_int(strg):
    if strg[0] in ('-', '+'):
        return strg[1:].isdigit()
    return strg.isdigit()


class RegisterEmployeeForm(FlaskForm):
    """Employee Registration Form class"""
    def validate_username(self, username_to_check):
        """Checking database for the entered username data"""
        employee = Employee.query.filter_by(username=username_to_check.data).first()
        if employee:
            raise ValidationError("Username already exists!")

        if check_int(username_to_check.data):
            raise ValidationError("Username can not be a number !")

    username = StringField(
        label='User Name',
        validators=[
            Length(min=3, max=40),
            DataRequired()
        ]
    )

    password1 = PasswordField(
        label="Password",
        validators=[Length(min=6), DataRequired()]
    )
    password2 = PasswordField(
        label="Confirm Password",
        validators=[EqualTo('password1'), DataRequired()]
    )

    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    """Employee Log in Form"""
    username = StringField(
        label='User Name',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        label="Password",
        validators=[DataRequired()]
    )
    submit = SubmitField(label="Sign In")


class CityDetailForm(FlaskForm):
    """City table details add form"""
    city_name = StringField(
        label='City Name',
        validators=[
            Length(max=50),
            DataRequired()
        ]
    )

    pin_code = IntegerField(
        label="Pin Code",
        validators=[
            DataRequired()
        ]
    )


class ContactAddressForm(FlaskForm):
    """Contact Address table detail add form"""
    firstname = StringField(
        label="First Name",
        validators=[
            Length(min=3, max=30),
            DataRequired()
        ]
    )
    lastname = StringField(
        label="Last Name",
        validators=[
            Length(min=3, max=30),
            DataRequired()
        ]
    )
    email = EmailField(
        label="Email Id",
        validators=[Email(), DataRequired()]
    )
    phone_number = IntegerField(
        label="Phone Number",
        validators=[
            DataRequired()
        ]
    )
    date_of_birth = DateField(
        label="Date of Birth",
        validators=[DataRequired()]
    )
    addressLine = StringField(
        label="Address",
        validators=[DataRequired()]
    )

    submit = SubmitField(label="Save Details")

    def validate_email(self, email_to_check):
        """Checking database for the entered email id data"""
        _employee_email_found = ContactAddress.query.filter_by(email=email_to_check.data).first()

        if _employee_email_found is not None:
            raise ValidationError("Email Id already exists!")

    def validate_phone_number(self, phone_number_to_check):
        """Checking database for the entered phone number data"""
        other_employee_contact_found = ContactAddress.query.filter_by(phone_number=phone_number_to_check.data).first()

        if other_employee_contact_found:
            raise ValidationError("This Mobile No. is already exists!")


class UpdateContactAddressForm(ContactAddressForm):
    email = EmailField(
        label="Email Id",
    )
    phone_number = IntegerField(
        label="Phone Number",
    )

    def validate_email(self, email_to_check):
        """
        Checking database for the entered email id data
        Not validating email as email can not be modified
        """
        pass

    def validate_phone_number(self, phone_number_to_check):
        """
        Checking database for the entered phone number data
        Not validating email as phone number can not be modified
        """
        pass


class SearchEmployeeForm(FlaskForm):
    """Search employee Form"""
    searched = StringField(
        label="Search Employee"
    )

    search = SubmitField(label="Search")
