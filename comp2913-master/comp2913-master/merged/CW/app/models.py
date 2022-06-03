from app import db,admin,generatePdf
from datetime import datetime,date
from flask import url_for,redirect,request,abort, render_template, request, flash
import flask_wtf
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model import typefmt
# from flask_security import Security, SQLAlchemyUserDatastore, \
#     UserMixin, RoleMixin, login_required, current_user
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import UserMixin, login_required, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import func
from flask_admin.menu import MenuLink
import hashlib
from flask_security import utils
from app import login
from os import path


@login.user_loader
def load_user(id):
    return User.query.get(int(id))




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    DateOfBirth = db.Column(db.Date())
    CCD = db.Column(db.String(40))
    CVV = db.Column(db.String(40))
    DateOfExpire = db.Column(db.DateTime())
    paymentIntervals = db.Column(db.String(20))
    plan=db.Column(db.String(20),default="No Plan")
    active = db.Column(db.Boolean())
    receipts = db.relationship('Receipt',uselist=True, backref='user', lazy='dynamic')
    bookings = db.relationship('Booking',uselist=True, backref='user', lazy='dynamic')
    role = db.Column(db.String(15))
    is_banned =  db.Column(db.Boolean, default=False, nullable=False)

    def getRoles(self):
        return self.role

    def __repr__(self):
        return '{}, ID: {}'.format(self.email, self.id)


#facilities-activities: one-to-many
#facilities-booking: one-to-many
class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilityName = db.Column(db.String(30), unique = True)
    capacity = db.Column(db.Integer())
    activities = db.relationship('Activity',uselist=True, backref='facility', lazy='dynamic')
    def __repr__(self):
        return '{}'.format(self.facilityName)

#facilities-activities: one-to-many
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activityType = db.Column(db.String(20))
    price = db.Column(db.Float())
    facilityId =db.Column(db.Integer, db.ForeignKey('facility.id'))
    #bookings = db.relationship('Booking', uselist=True,backref='activity', lazy='dynamic')
#facility-Booking: one-to-many
#customer-Booking:one-to-many
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingDate = db.Column(db.DateTime())
    sessionId=db.Column(db.Integer,db.ForeignKey('session.id'))
    customerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    state = db.Column(db.String(15))
    receipt = db.relationship("Receipt", uselist = False, back_populates = "booking")

    def __repr__(self):
        return 'ID: {} state: {}'.format(self.id, self.state)

#customer-receipt: one-to-many
#receipt-booking: one-to-one
class Receipt(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    type =db.Column(db.String(25))
    price = db.Column(db.Float())
    dateOfPurchase = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    customerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookingId = db.Column(db.Integer, db.ForeignKey('booking.id'))
    booking = db.relationship("Booking", back_populates="receipt")


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date())
    day=db.Column(db.String(25))
    startTime=db.Column(db.String(25))
    endTime=db.Column(db.String(25))
    facility=db.Column(db.String(25))
    activity=db.Column(db.String(25))
    availability=db.Column(db.Integer)
    bookings = db.relationship('Booking',uselist=True, backref='session', lazy='dynamic')

    def __repr__(self):
        return '{}, {}, {}:00-{}:00 {}, {} ID: {}'.format(self.date.strftime('%d/%m/%Y'),self.day, self.startTime, self.endTime, self.facility, self.activity, self.id)
    def getActivity(self):
        return self.activity
    def getDate(self):
        return self.date
    def getTime(self):
        return self.startTime + "-" +self.endTime
def date_format(view, value):
    if isinstance(value,datetime):
        return value.strftime('%d/%m/%Y %H:%M:%S')
    else:
        return value.strftime('%d/%m/%Y')


MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    date: date_format,
    # dict: json_format
})



class AdminUserView(ModelView):


    def on_model_change(self, form, User, is_created):
        User.password = hashlib.md5((User.password).encode()).hexdigest()
        db.session.commit()



    def is_visible(self):
        return current_user.role == 'Admin'

    column_filters = ['plan']
    create_modal = True
    edit_modal = True
    column_exclude_list = ['password' ]
    column_searchable_list = ['name', 'surname', 'email']
    column_editable_list = ['is_banned', 'role']


    def is_accessible(self):
        if current_user.getRoles() == "Admin" or current_user.getRoles() == 'Employee':

            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            return abort(403)




# # Create customized model view class
class MyModelView(ModelView):

    @property
    def can_delete(self):
        return current_user.role == 'Admin'


    def is_visible(self):
        return current_user.role == 'Admin'
    
    column_exclude_list = ['password' ]

    def is_accessible(self):
        if current_user.getRoles() == "Admin":


            return (current_user.is_active and
                    current_user.is_authenticated)
        elif current_user.getRoles() == "Employee":

            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            print("not admin")
            return abort(403)

class EmployeeSessionView(ModelView):
    column_display_pk = True
    column_type_formatters = MY_DEFAULT_FORMATTERS
    form_base_class = flask_wtf.FlaskForm

    column_filters = ['date', 'startTime', 'endTime', 'facility', 'activity']
    column_searchable_list = ['date', 'startTime', 'endTime']
    def is_visible(self):
        return current_user.role == 'Employee' or  current_user.getRoles() == "Admin"

    def is_accessible(self):
        if current_user.getRoles() == "Admin" or current_user.getRoles() == "Employee":


            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            return abort(403)

def makeReceipt(id):
    print(id)
    booking = Booking.query.filter_by(id = id).first()
    currentUser = booking.user.id
    print(currentUser)
    r = Receipt.query.filter_by(bookingId=id).first()


    if r is not None:
        print("Booking Receipt already exists")

    if r is None:
        print("creating receipt db object")
        bookingreceipt=Receipt(type="Booking",customerId=currentUser,dateOfPurchase=datetime.today(),bookingId=id)
        db.session.add(bookingreceipt)
        db.session.commit()
        customer = booking.user
        session = booking.session
        facility = Facility.query.filter_by(facilityName = session.facility).first()
        activity = Activity.query.filter_by(activityType = session.activity, facilityId = facility.id ).first()
        name = customer.name
        surname = customer.surname
        if surname is None:
            surname = " "
        td = booking.bookingDate.date()
        today = td.strftime("%d/%m/%Y")
        price = activity.price
        product = facility.facilityName
        dt = session.date
        dt_string = dt.strftime("%d/%m/%Y")
        tm_string = str(session.startTime) + ":00 - " + str(session.endTime) + ":00"


        file = "app/static/receipts/" + str(bookingreceipt.id) + ".pdf"
        if not path.exists(file):
            print("creating receipt file")
            generatePdf.generate(name, surname,today,bookingreceipt.id, price, product,dt_string,tm_string,"Booking")



class EmployeeBookingView(ModelView):
    # inline_models = (Session,)
    column_display_pk = True
    column_type_formatters = MY_DEFAULT_FORMATTERS
    form_base_class = flask_wtf.FlaskForm
    column_auto_select_related = True
    iniline_models = (Session,)
    column_editable_list = ['state']

    def on_model_change(self, form, Booking, is_created):
        if not is_created:
            if Booking.state == "Booked":
                print("Creating Receipt")
                print(Booking.id)
                makeReceipt(Booking.id)

    @property
    def can_edit(self):
        return current_user.role == 'Admin'
    @property
    def can_delete(self):
        return current_user.role == 'Admin'


    column_filters = ['sessionId', 'customerId', 'state','id']
    def is_visible(self):
        return current_user.role == 'Employee' or  current_user.getRoles() == "Admin"

    def is_accessible(self):
        if current_user.getRoles() == "Admin" or current_user.getRoles() == "Employee":

            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            return abort(403)

class EmployeeUserView(ModelView):

    column_display_pk = True
    form_base_class = flask_wtf.FlaskForm

    def get_query(self):
      return self.session.query(self.model).filter(self.model.role=="Customer")

    def get_count_query(self):
      return self.session.query(func.count('*')).filter(self.model.role=="Customer")
    #exclude password from db

    @property
    def can_edit(self):
        return False
    @property
    def can_delete(self):
        return False
    @property
    def can_create(self):
        return False


    column_filters = ['plan']
    create_modal = True
    edit_modal = True
    column_exclude_list = ['password' ]
    column_searchable_list = ['name', 'surname', 'email']
    column_editable_list = ['is_banned']

    def is_visible(self):
        return current_user.role == 'Employee'

    def is_accessible(self):
        if current_user.getRoles() == "Admin" or current_user.getRoles() == "Employee":

            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            return abort(403)


class EmployeeReceiptView(ModelView):
    # inline_models = (Session,)
    column_display_pk = True
    column_type_formatters = MY_DEFAULT_FORMATTERS
    form_base_class = flask_wtf.FlaskForm
    column_auto_select_related = True
    column_labels = dict(id='Receipt ID')

    @property
    def can_edit(self):
        return current_user.role == 'Admin'
    @property
    def can_delete(self):
        return current_user.role == 'Admin'

    def is_visible(self):
        return current_user.role == 'Employee' or  current_user.getRoles() == "Admin"

    def is_accessible(self):
        if current_user.getRoles() == "Admin" or current_user.getRoles() == "Employee":

            return (current_user.is_active and
                    current_user.is_authenticated)
        else:
            return abort(403)


class FileView(FileAdmin):
    can_delete = False
    can_upload = False
    can_delete_dirs = False
    can_mkdir = False
    can_rename = False
    can_download = True


admin.add_view(AdminUserView(User, db.session,endpoint = "Admin Users"))
admin.add_view(MyModelView(Facility, db.session))
admin.add_view(MyModelView(Activity, db.session))

admin.add_view(EmployeeUserView(User, db.session, endpoint = "Users"))
admin.add_view(EmployeeSessionView(Session, db.session))
admin.add_view(EmployeeBookingView(Booking, db.session))
admin.add_view(EmployeeReceiptView(Receipt,db.session))
p = path.join(path.dirname(__file__), 'static/receipts')
admin.add_view(FileView(p, '/static/receipts/', name='Receipt Files'))
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

