import base64
import logging
from flask import jsonify, session
from organization import db, bcrypt, login_manager
from flask_login import UserMixin
from flask_login._compat import text_type


models_logger = logging.getLogger()

@login_manager.user_loader
def load_user(e_id):
    employee = Employee.query.filter_by(e_id=e_id).first()
    # employee = Employee.query.filter_by(username=username).first()
    if employee:
        return employee


class City(db.Model):
    """city table stores city names and unique pin codes"""
    cp_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(length=50), nullable=False)
    pin_code = db.Column(db.Integer, nullable=False, unique=True)

    # relationship with EmployeeContactAddress
    contact_address = db.relationship('ContactAddress', backref='city', lazy=True)

    def __repr__(self) -> str:
        return f"<city: {self.city_name} pin: {self.pin_code}>"


class Roles(db.Model):
    """roles table different roles for employees"""
    role_id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(), nullable=False, unique=True)

    # Relationship with Employee
    employee = db.relationship('Employee', backref='role', lazy=True)

    def __repr__(self) -> str:
        return f"<role id: {self.role_id} role: {self.role}>"


class Employee(db.Model, UserMixin):
    """employee table stores username and password"""
    e_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=50), nullable=False, unique=True)
    hash_password = db.Column(db.String(length=256), nullable=False)
    # relationship with EmployeeContactAddress
    contact_address = db.relationship('ContactAddress', backref='employee', lazy=True)

    # Foreign key for role
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=True, default=2)
    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, entered_text_password):
        """set encrypted password in the database"""
        self.hash_password = bcrypt.generate_password_hash(entered_text_password).decode("utf-8")

    def check_password(self, attempted_password):
        """checking attempted password with stored password with bcrypt lib"""
        return bcrypt.check_password_hash(self.hash_password, attempted_password)

    def get_id(self):
        try:
            return text_type(self.e_id)
        except AttributeError:
            raise NotImplementedError('No `e_id` attribute - override `get_id`')

    def is_admin(self):
        # checks employee is admin or not
        # admin role_id -> 1
        return self.role_id == 1

    def is_active_employee(self):
        # checks employee role - role_id -> 2
        # role_id = None -> not an active employee for soft delete
        return self.role_id is not None

    def __repr__(self):
        return f"<{self.username}>"


class ContactAddress(db.Model):
    """
    after creating, table name will be contact_address
    stores employee contact related info - name, email, phone no, date of birth, address
    """
    contact_details_id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=True)     # default is username - store while register employee
    lastname = db.Column(db.String(length=30), nullable=True)
    
    email = db.Column(db.String(length=80), nullable=False, unique=True)     # store while register employee
    phone_number = db.Column(db.Integer(), nullable=False, unique=True)      # store while register employee
    
    date_of_birth = db.Column(db.Date, nullable=True)
    addressLine = db.Column(db.String(length=250), nullable=True)
    
    # 2 foreign key here cp_id, e_id
    cp_id = db.Column(db.Integer, db.ForeignKey('city.cp_id'))
    e_id = db.Column(db.Integer, db.ForeignKey('employee.e_id'), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<e_id: {self.e_id} email: {self.email}>"

