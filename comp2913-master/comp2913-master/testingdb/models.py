from app import db
from datetime import datetime,date
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

#creates a database that store the title, the date,the description of a task
#and whether it is completed or not which is set as not completed by default
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task=db.Column(db.String(200))
    date1 = db.Column(db.Date)
    taskDesc=db.Column(db.String(500))
    completed=db.Column(db.Boolean,default=False)


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
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    receipts = db.relationship('Receipt', backref='user', lazy='dynamic')
    Bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class Receipt(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    price = db.Column(db.Float())
    dateOfPurchase = db.Column(db.DateTime, index=True, default=datetime.now())
    customerId = db.Column(db.Integer, db.ForeignKey('user.id'))


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

#facility-Booking: one-to-many
#customer-Booking:one-to-many
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingDate = db.Column(db.DateTime())
    bookingTime = db.Column(db.Integer)#db.Column(db.DateTime, index=True, default=datetime.utcnow)
    facilityId =db.Column(db.Integer, db.ForeignKey('facility.id'))
    customerId =db.Column(db.Integer, db.ForeignKey('user.id'))
    counter = db.relationship("Counter", uselist=False, backref="booking")
    # tagging = db.relationship('Tag', secondary = epost, backref = db.backref('eposts', lazy = 'dynamic'))

#counter-booking: one-to-many
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookingId =db.Column(db.Integer, db.ForeignKey('booking.id'))
    currentCapacity =  db.Column(db.Integer,default=0)
