from flask_wtf import FlaskForm
from flask_login import current_user, logout_user, login_user
from wtforms import StringField, SubmitField , TextAreaField, BooleanField, PasswordField ,DateField, IntegerField,validators
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField, EmailField
from models import User

# Customer registration form
class CustomerForm(FlaskForm):

    name= StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])

    # surname=StringField('Surname',
    #                        validators=[DataRequired(), Length(min=2, max=20)])

    email = EmailField('Email address', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=35, message='Email must be between 6 and 35 characters')])

    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=4, max=35,message='Password must be between 4 and 35 characters')])

    submit = SubmitField('Sign Up')

    # confirm_password = PasswordField('Confirm Password',
    #                                  validators=[DataRequired(), EqualTo('password')])
    #
    # DateOfBirth = DateField('Date of Birth', validators=[DataRequired()])
    #
    # CCD = IntegerField("Enter your card number",validators=[DataRequired(), Length(min=16, max=16)])
    #
    # CVV = IntegerField("Security Code",validators=[DataRequired(), Length(min=3, max=3)])
    #
    # DateOfExpire = DateField('Date of Expire', validators=[DataRequired()])
    #




# form that the user will use to log in
class LoginForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email(), validators.Length(min=6, max=35, message='Email must be between 6 and 35 characters')])

    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=4, max=35,message='Password must be between 4 and 35 characters')])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')



# form for creating bookings
class BookingForm(FlaskForm):
    Date = DateField('Date Of Booking',validators=[DataRequired])
    Time = IntegerField("Time of Booking",validators=[DataRequired])
    Facility = StringField('Facility of Booking',validators=[DataRequired])
    CustomerEmail = StringField('Email',
                        validators=[DataRequired(), Email()])
