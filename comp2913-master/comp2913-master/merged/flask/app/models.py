from app import db
from datetime import datetime,date
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_admin.contrib import sqla

# @LoginManager.user_loader
# def load_user(id):
#     return Customer.query.get(int(id))

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


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
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.surname)
#facilities-activities: one-to-many
#facilities-booking: one-to-many
class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilityName = db.Column(db.String(30), unique = True)
    capacity = db.Column(db.Integer())
    price = db.Column(db.Float())
    activities = db.relationship('Activity', backref='facility', lazy='dynamic')
    bookings = db.relationship('Booking', backref='facility', lazy='dynamic')

#facilities-activities: one-to-many
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activityType = db.Column(db.String(20))
    facilityId =db.Column(db.Integer, db.ForeignKey('facility.id'))
    bookings = db.relationship('Booking', backref='activity', lazy='dynamic')

#facility-Booking: one-to-many
#customer-Booking:one-to-many
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingDate = db.Column(db.DateTime())
    bookingTime = db.Column(db.Integer)#db.Column(db.DateTime, index=True, default=datetime.utcnow)
    facilityId = db.Column(db.Integer, db.ForeignKey('facility.id'))
    activityId = db.Column(db.String, db.ForeignKey('activity.id'))
    customerId =db.Column(db.Integer, db.ForeignKey('user.id'))
    counter = db.relationship("Counter", uselist=False, backref="booking")
    # tagging = db.relationship('Tag', secondary = epost, backref = db.backref('eposts', lazy = 'dynamic'))

#counter-booking: one-to-many
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingId =db.Column(db.Integer, db.ForeignKey('booking.id'))
    currentCapacity =  db.Column(db.Integer)

#customer-receipt: one-to-many
#receipt-booking: one-to-one
class Receipt(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    price = db.Column(db.Float())
    dateOfPurchase = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    customerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookingId = db.Column(db.Integer, db.ForeignKey('booking.id'))


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), index=True)
    surname = db.Column(db.String(25), index=True)
    email = db.Column(db.String(320), index=True, unique=True)
    passwordHash = db.Column(db.String(128))


    def __repr__(self):
        return '<Post {}>'.format(self.body)




# Create customized model view class
class MyModelView(sqla.ModelView):
    #exclude password from db
    column_exclude_list = ['password', ]
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
