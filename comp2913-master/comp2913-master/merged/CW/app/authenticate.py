from app import app, db, models
from flask import request
from wtforms.validators import ValidationError
import hashlib



def signup(data):
    pwd = data.password.data
    # hash the password before storing it in your DB, this is important for security
    hashed = hashPWD(pwd)
    print(hashed)
    print("hashed password")

    print("checked if database is empty")
    checkEmail = models.User.query.filter_by(email = data.email.data).first()
    if checkEmail is not None:
        app.logger.warning('invalid email signup')
        return False,"invalid email"
    return True,hashed

def createUser(data, hashed):
    #store new user in database
    print(hashed)

    p = models.User(name = data.name.data,surname=data.surname.data, email = data.email.data, password = hashed,DateOfBirth=data.DateOfBirth.data,CCD=data.CCD.data,CVV=data.CVV.data,DateOfExpire=data.DateOfExpire.data,role="Customer")    #surname = data.surname.data, DateOfBirth = data.DateOfBirth, CCD = hashedCCD, CVV = hashedCVV, DateOfExpire = data.DateOfExpire ,paymentIntervals = data.paymentIntervals
    db.session.add(p)
    db.session.commit()
    app.logger.info('New User created: id = %s', p.id)


def hashPWD(password):
    hashed_pass = hashlib.md5(password.encode())
    return hashed_pass.hexdigest()

 ## returns False if email doesnt exist or password is incorrect, othrwise returns true
def logInUser(data):
    hashed = hashPWD(data.password.data)

    update = models.User.query.filter_by(email = data.email.data).first()

    if update is None:
        app.logger.warning('Invalid Email login')
        return False
    elif update.password != hashed:
        app.logger.warning('Invalid password login')
        return False
    return True
