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
    # if models.User.query.all() is None:
    #     return True,hashed
    print("checked if database is empty")
    # check if email exists
    checkEmail = models.User.query.filter_by(email = data.email.data).first()
    if checkEmail is not None:
        app.logger.warning('invalid email signup')
        return False,"invalid email"
    #print("Returning Users")
    return True,hashed

def createUser(data, hashed):
    #store new user in database
    print(hashed)
    # hashedCCD = hashPWD(data.CCD)
    # hashedCVV = hashPWD(data.CVV)
    # print(hashedCCD)
    # print(hashedCVV)
    p = models.User(name = data.name.data, email = data.email.data, password = hashed)
    #surname = data.surname.data, DateOfBirth = data.DateOfBirth, CCD = hashedCCD, CVV = hashedCVV, DateOfExpire = data.DateOfExpire ,paymentIntervals = data.paymentIntervals
    db.session.add(p)
    db.session.commit()
    app.logger.info('New User created: id = %s', p.id)


def hashPWD(password):
    hashed_pass = hashlib.md5(password.encode())
    return hashed_pass.hexdigest()

 ## returns False if email doesnt exist or password is incorrect, othrwise returns true
def logInUser(data):
    #print("logging user in")
    hashed = hashPWD(data.password.data)
    # Here you have to hash the password the user submitted,
    # and then compare it with the password stored in your database
    # ip_addr = request.remote_addr
    update = models.User.query.filter_by(email = data.email.data).first()
    print(hashed)
    print(update.password)
    if update is None:
        # app.logger.warning('Login attempt to %s from IP %s', data.username,ip_addr )
        app.logger.warning('Invalid Email login')
        #print(" Username doesnt exist")
        return False
    elif update.password != hashed:
        # app.logger.warning('Login attempt to %s from IP %s', data.username,ip_addr )
        app.logger.warning('Invalid password login')
        #print("Incorrect password")
        return False

    return True
