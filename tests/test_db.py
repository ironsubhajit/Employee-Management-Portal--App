from organization import db
from organization.models import Employee, ContactAddress, City, Roles
from datetime import date


def test_employee_db(client):
    emp = Employee(username="test", password="test", role_id=2)
    db.session.add(emp)
    db.session.commit()
    emp = Employee.query.filter_by(e_id=emp.e_id).first()
    assert emp.username == emp.username
    assert emp.is_active_employee()
    assert not emp.is_admin()
    assert emp.check_password("test")
    return


def test_employee_contact(client):
    emp = Employee(username="test", password="test")
    db.session.add(emp)
    db.session.commit()
    city = City(
        city_name='kolkata',
        pin_code=700001
    )
    db.session.add(city)
    db.session.commit()
    employee_contact = ContactAddress(
        firstname='test',
        lastname='test',
        email='test@email.com',
        phone_number=123456789,
        date_of_birth=date(2020, 2, 1),
        addressLine='kolkata',
        cp_id=city.cp_id,
        e_id=emp.e_id
    )
    db.session.add(employee_contact)
    db.session.commit()

    contact = ContactAddress.query.filter_by(e_id=emp.e_id).first()
    assert contact.firstname == employee_contact.firstname
    assert contact.lastname == employee_contact.lastname
    assert contact.email == employee_contact.email
    assert contact.phone_number == employee_contact.phone_number
    assert contact.date_of_birth == employee_contact.date_of_birth
    assert contact.addressLine == employee_contact.addressLine
    return

