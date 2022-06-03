from flask import render_template, flash
from app import app
from app import models,db
from flask import request,redirect,url_for
from datetime import datetime



@app.route('/rec')
def rec():
    usr=models.User(first_name='s',last_name='p',email='w152341@gmail.com',password='1234567',active=True)
    db.session.add(usr)
    db.session.commit()

    newp=models.Receipt(price=5,customerId=newtask.id)
    db.session.add(newp)
    db.session.commit()

    fn=models.Facility(facilityName='Sports Hall 5',capacity=25,price=20)
    db.session.add(fn)
    db.session.commit()

    ad1=models.Activity(activityType='HOUR SESSION',facilityId=fn.id)
    db.session.add(ad1)
    db.session.commit()


    b1=models.Booking(bookingDate=datetime(2020, 4, 4, 10, 10, 10),bookingTime=1,facilityId=1,customerId=1)
    # c1=models.Counter(bookingId=1)


     # bdb1=models.Booking.query.filter_by(facilityId=b1.facilityId).first()
    cdb=models.Counter.query.filter_by(bookingId=1).first()
    c1=models.Counter(currentCapacity=cdb.currentCapacity+1,bookingId=1)


    db.session.add(c1)
    db.session.commit()
    db.session.delete(cdb)

    db.session.commit()

    cdb1=models.Counter.query.all()
    bdb=models.Booking.query.all()
    fdb=models.Facility.query.all()
    database=models.User.query.all()
    db1=models.Receipt.query.all()
    adb=models.Activity.query.all()
    bdb=models.Booking.query.all()
    return render_template('pl.html',title='Testing',database=database,db1=db1,fdb=fdb,adb=adb,bdb=bdb,cdb1=cdb1)
