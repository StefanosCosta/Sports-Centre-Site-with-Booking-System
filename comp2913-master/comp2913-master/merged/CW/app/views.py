from app import app
from app import stripe_keys,models,db
import stripe
from flask import Flask, url_for, redirect, render_template, request, abort, flash
from flask_login import login_required, login_user, current_user,logout_user,LoginManager

from app.forms import LoginForm,CustomerForm,BookingForm, PlanForm, Inputs, Inputs2
from app import authenticate, generatePdf, sendEmail,gen2,login, gen3
import logging
import datetime
from datetime import datetime,timedelta,date,time
import os.path
from os import path
from functools import wraps
import _datetime

#override of login_required to accomodate role authorisation and access
def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
                print("user not authenticated")
                return abort(403)
            urole = login
            if ( (current_user.role != role) and (role != "ANY")):
                print("invalid user")
                return abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# Flask views

#home view without logging
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('workout'))
    return render_template('home.html', title = 'Home')
#facilities page
@app.route('/facilities')
def facilities():
    return render_template('facilities.html',title='Facilities')
#activity prices page
@app.route('/facprices')
@login_required(role="Customer")
def facprices():
    return render_template('activityprice.html',title='ActivityPrices')

@app.route('/payment')
@login_required(role="ANY")
def payment():
    return render_template('payment.html', title='Checkout',header="Checkout",key = stripe_keys['publishable_key'])

@app.route('/admin/')
@login_required(role="ANY")
def admin():
    return render_template('admin/admin.html')



#login page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(request.form,meta={'csrf': True})
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if not authenticate.logInUser(form):
            flash('Invalid username or password')
        else:
            print("here")
            login_user(user, remember=form.remember.data)
            app.logger.info('User with id %s successfully logged in',user.id)
            next_page = request.args.get('next')
            if current_user.role == "Admin" or current_user.role == "Employee":
                return redirect(url_for('admin'))
            if not next_page or urlparse(next_page).netloc != '':
                app.logger.info('rerouting to home')
                next_page = url_for('workout')
            return redirect(next_page)
            #return redirect(url_for('workout'))
    return render_template('security/login.html', title='Log In', form = form)


#register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CustomerForm(request.form,meta={'csrf': True})
    print("signup")
    if not form.validate_on_submit():
        print("not validated")
    if form.validate_on_submit():
        print("here")
        result,hashed  = authenticate.signup(form)
        if result is False:
            flash('An account already exists for this email')
        if result == True:
            print("creating user")
            authenticate.createUser(form, hashed)
            return redirect(url_for("login"))
    # if current_user.is_authenticated:#if already signed in go to homepage
    #     return redirect('/home')
    return render_template('security/signup.html', title='Sign Up', form=form)

#route used for testing to view all the users
# @app.route('/ppl', methods=['GET', 'POST'])
# def allposts():
#     users=models.User.query.all()
#     return render_template('ppl.html',users=users,title='Posts')


#view that diplays all bookings for the current user
@app.route('/mybookings', methods=['GET','POST'])
@login_required(role="Customer")
def mybookings():
    sessions=[]
    past=[]
    receipt=[]
    cancelled=[]
    r=[]
    bookings=models.Booking.query.filter_by(customerId=current_user.id).all()
    now = datetime.now()
    d = now.strftime("%Y-%m-%d")#day
    day =datetime.strptime(d,"%Y-%m-%d").date()
    timeNow=now.strftime("%H:%M:%S")
    receipts=models.Receipt.query.all()
    print(day)#day now
    for b in bookings:
        session=models.Session.query.filter_by(id=b.sessionId).first()
        time=session.endTime
        print(time)
        print(timeNow)
        if(time<timeNow and day==session.date and b.state == "Booked"):
            past.append(session)
        elif day>session.date and b.state == "Booked":
            past.append(session)
        elif session not in sessions and (b.state == "Booked" or b.state == "Pending"):
            print(session.date)
            sessions.append(session)
        elif b.state == "Cancelled":
            cancelled.append(session)
        elif day>session.date and b.state == "Pending":
            db.session.delete(b)
            db.session.commit()
        elif(time<timeNow and day>session.date and b.state == "Pending"):
            db.session.delete(b)
            db.session.commit()
    return render_template('mybooking.html',sessions=sessions,past=past,receipt=receipts,bookings=bookings, cancelled= cancelled)


#homw route
@app.route('/home')
def home():
    return render_template('home.html')

#cancel membership
@app.route('/cancel', methods=['GET', 'POST'])
@login_required(role="Customer")
def cancel():
    user=models.User.query.filter_by(id=current_user.id).first()
    print(current_user.id)
    print(user.id)
    form=PlanForm(request.form,meta={'csrf': True})
    if request.method == 'POST':
        print("as")
        user.plan="No Plan"
        db.session.commit()
        print(user.plan)
        return redirect(url_for("plans"))
    print(user.plan)
    return render_template('cancel.html',user=user)


#
@app.route('/plans', methods=['GET','POST'])
@login_required(role="Customer")
def plans():
    form=PlanForm(request.form,meta={'csrf': True})
    user=models.User.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        if form.name.data=="1":
            user.plan="Bronze Membership"
            newplan=models.Receipt(type="Bronze Membership",customerId=current_user.id,price=15,dateOfPurchase=datetime.today())#current_customer_id
            db.session.add(newplan)
            db.session.commit()
            # newUrl='/newpdf/'+ str(newplan.id)
            newUrl='/receipt2/'+ str(newplan.id)
            gen2.gen(user.name,"ss", datetime.today(),newplan.id,15.00,"Bronze")
            return redirect(newUrl)

        if form.name.data=="2":
            user.plan="Silver Membership"
            newplan=models.Receipt(type="Silver Membership",customerId=current_user.id,price=25,dateOfPurchase=datetime.today())#current_customer_id
            db.session.add(newplan)
            db.session.commit()
            newUrl='/receipt2/'+ str(newplan.id)
            gen2.gen(user.name,"ss", datetime.today(),newplan.id,25.00,"Silver")
            return redirect(newUrl)

        if form.name.data=="3":
            user.plan="Gold Membership"
            newplan=models.Receipt(type="Gold Membership",customerId=current_user.id,price=40,dateOfPurchase=datetime.today())#current_customer_id
            db.session.add(newplan)
            db.session.commit()
            newUrl='/receipt2/'+ str(newplan.id)
            gen2.gen(user.name,"ss", datetime.today(),newplan.id,40.00,"Gold")
            return redirect(newUrl)

    return render_template('plans.html',user=user)



@app.route('/weekly', methods=['GET', 'POST'])
@login_required(role="Customer")
def weekly():
    weekPrice=0
    startWeek =datetime.now() + timedelta(1)
    startWeek = startWeek.strftime("%Y-%m-%d")
    print(startWeek)

    endWeek =datetime.today() + timedelta(8)
    endWeek = endWeek.strftime("%Y-%m-%d")
    weekSessions=models.Session.query.all()
    notEmpty=0
    sc=0
    sp=0
    sh=0
    if request.method == "POST":
        if request.form.get('sc')=="true":
            sc=1
            notEmpty=notEmpty+1
            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):

                    if i.facility=="Squash room-2" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()

                        weekPrice=weekPrice+sessionActivity.price
                # print()
            weekPrice=weekPrice-weekPrice*0.10
            print(weekPrice)
        if request.form.get('sp')=="true":
            sp=1
            notEmpty=notEmpty+1
            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):

                    if i.facility=="Swimming Pool" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()

                        weekPrice=weekPrice+sessionActivity.price
            weekPrice=weekPrice-weekPrice*0.10
        if request.form.get('sh')=="true":
            sh=1
            notEmpty=notEmpty+1
            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):

                    if i.facility=="Sports Hall" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()

                        weekPrice=weekPrice+sessionActivity.price
            weekPrice=weekPrice-weekPrice*0.10

            weekPrice=str(round(weekPrice, 2))
            print(weekPrice)
        if notEmpty!=0 :
            newUrl='/payweek/'+ str(weekPrice) +"/" +str(sc) +"/" +str(sp) +"/" +str(sh)

            return redirect(newUrl)
        else :
            flash("Please fill in one or more options to continue")
    return render_template('weekly.html',weekPrice=weekPrice)


@app.route('/payweek/<float:price>/<int:sc>/<int:sp>/<int:sh>', methods=['GET','POST'])
@login_required(role="Customer")
def payweek(price,sc,sp,sh):
    startWeek =datetime.now() + timedelta(1)
    startWeek = startWeek.strftime("%Y-%m-%d")
    print(startWeek)

    endWeek =datetime.today() + timedelta(8)
    endWeek = endWeek.strftime("%Y-%m-%d")
    cardPrice=price*100
    if request.method=='POST':
        weekSessions=models.Session.query.all()
        if sc==1:
            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):
                    if i.facility=="Squash room-2" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()
                        i.availability=i.availability-1
                        db.session.commit()
        if sp==1:

            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):

                    if i.facility=="Swimming Pool" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()
                        i.availability=i.availability-1
                        db.session.commit()
        if sh==1:
            for i in weekSessions:
                if(str(i.date)>=startWeek and str(i.date)<=endWeek):
                    if i.facility=="Sports Hall" :
                        sessionActivity=models.Activity.query.filter_by(activityType=i.activity).first()
                        i.availability=i.availability-1
                        db.session.commit()

        weekplan=models.Receipt(type="Weekly Plan",customerId=current_user.id,price=price,dateOfPurchase=datetime.today())#current_customer_id
        db.session.add(weekplan)
        db.session.commit()
        gen3.gen(current_user.name,"ss", datetime.today(),weekplan.id,price,startWeek,endWeek,sc,sp,sh)
        newUrl='/receipt3/'+ str(weekplan.id) +"/" +str(sc) +"/" +str(sp) +"/" +str(sh)
        return redirect(newUrl)
    return render_template('payweek.html',price=price, startWeek=startWeek,endWeek=endWeek,cardPrice=cardPrice)


@app.route('/receipt3/<int:id>/<int:sc>/<int:sp>/<int:sh>', methods=['GET','POST'])
@login_required(role="Customer")
def receipt3(id,sc,sp,sh):
    weekreceipt=models.Receipt.query.filter_by(id=id).first()
    startWeek =weekreceipt.dateOfPurchase + timedelta(1)
    startWeek = startWeek.strftime("%Y-%m-%d")

    endWeek =weekreceipt.dateOfPurchase + timedelta(8)
    endWeek = endWeek.strftime("%Y-%m-%d")
    str1=""
    if sc==1:
        str1=str1+"Squash Room-2 "
        if sp==1:
            str1=str1+",Swimming Pool "
        if sh==1:
            str1=str1+",Sports Hall"
    else:
        if sp==1:
            str1=str1+"Swimming Pool "
            if sh==1:
                str1=str1+",Sports Hall"
        else:
            if sh==1:
                str1=str1+"Sports Hall"
    if request.method=='POST':
        newUrl='/newpdf/'+ str(id)
        return redirect(newUrl)
    return render_template('receipt3.html',startWeek=startWeek,endWeek=endWeek,weekreceipt=weekreceipt,str1=str1)




@app.route('/receipt2/<int:id>', methods=['GET','POST'])
@login_required(role="Customer")
def receipt2(id):
        newPlan=models.Receipt.query.filter_by(id=id).first()
        if request.method=='POST':
            newUrl='/newpdf/'+ str(id)
            return redirect(newUrl)
        return render_template('receipt2.html' ,  date =datetime.today(),newPlan=newPlan)

# @app.route('/planreceipts', methods=['GET','POST'])
# def planreceipts():
#         user=models.User.query.filter_by(id=current_user.id).first()
#         bookings = models.Booking.query.filter_by(customerId=current_user.id).all()
#         receipts=models.Receipt.query.filter_by(customerId=current_user.id).order_by(models.Receipt.dateOfPurchase.desc())
#         if request.method=='POST':
#             type=request.form['type']
#             id = request.form['receiptId']
#             if type=="Booking":
#                 newUrl='/receipt/'+ str(id)
#             else :
#                 newUrl='/receipt2/'+ str(id)
#             return redirect(newUrl)
#         return render_template('planreceipts.html' ,  date =datetime.today(),user=user,receipts=receipts, bookings=bookings)
#

@app.route('/planreceipts', methods=['GET','POST'])
@login_required(role="Customer")
def planreceipts():
        user=models.User.query.filter_by(id=current_user.id).first()
        print(user.plan)

        currentPlan=models.Receipt.query.filter_by(customerId=current_user.id,type=user.plan).order_by(models.Receipt.dateOfPurchase.desc()).first()
        currentWeek=models.Receipt.query.filter_by(customerId=current_user.id,type="Weekly Plan").order_by(models.Receipt.dateOfPurchase.desc())
        for i in currentWeek:
            if i.dateOfPurchase+timedelta(8)<datetime.now():
                i.type="Expired Weekly Plan"
        print(currentPlan)
        receipts=models.Receipt.query.filter_by(customerId=current_user.id).order_by(models.Receipt.dateOfPurchase.desc())

        if request.method=='POST':
            type=request.form['type']
            id = request.form['receiptId']
            if type=="Weekly Plan" or type=="Expired Weekly Plan":
                newUrl='/newpdf/'+ str(id)
            else:
                newUrl='/receipt2/'+ str(id)
            return redirect(newUrl)
        return render_template('planreceipts.html' ,  date =datetime.today(),user=user,receipts=receipts,currentPlan=currentPlan,currentWeek=currentWeek)



@app.route('/newpdf/<int:plan>')
@login_required(role="Customer")
def newpdf(plan):
    newStr= '../static/receipts/' + str(plan) + '.pdf'
    return render_template('newpdf.html',str=plan,newStr=newStr)

@app.route('/table', methods=['GET','POST'])
@login_required(role="Customer")
def table():
    session=models.Session.query.all()
    priceList=[]
    for i in  session:
        activity=models.Activity.query.filter_by(activityType=i.activity).first()
        priceList.append(activity.price)
    return render_template('table.html',session=session,price=priceList)

@app.route('/tableBook/<int:id>', methods=['POST'])
@login_required(role="Customer")
def tableBook(id):

    given=models.Session.query.filter_by(id=id).first()
    session=models.Session.query.filter_by(date=given.date,startTime=given.startTime, facility = given.facility).all()
    sessionList=[]
    for i in session:
        facility = models.Facility.query.filter_by(facilityName = given.facility).first()
        
        activity = models.Activity.query.filter_by(activityType = given.activity, facilityId = facility.id).first()
        sessionList.append([i,activity.price])
    choices = ["Pay By Cash", "Pay By Card"]
    form = Inputs(request.form,meta={'csrf': True})
    form2 = Inputs2(request.form,meta={'csrf': True})
    if not form.validate_on_submit():
        print(form.myField.data)
        print(form.sessionId.data)
        print("Form not validated")
    if form.validate_on_submit() and request.method == 'POST':
        #get current user
        member=models.User.query.filter_by(id=current_user.id).first()
        #get current user's plan
        plan=member.plan
        #if no plan reject
        if plan=="No Plan":
            flash("You don't have a membership plan!")
            return redirect(url_for('plans'))
        sId = int(form.sessionId.data)
        sesh=models.Session.query.filter_by(id=sId).first()
        if sesh.availability==0:
            flash("That activity is fully booked")
        today = datetime.now()
        booking=models.Booking.query.filter_by( sessionId=sId,customerId=current_user.id, state = "Booked").first()
        b = models.Booking.query.filter_by( sessionId=sId,customerId=current_user.id, state = "Pending").first()
        if booking is None :
            if form.myField.data == "Cash":
                print("cash payment")
                if b is None:
                    booking=models.Booking(bookingDate = today,sessionId=sId,customerId=current_user.id, state = "Pending")#state = "pending"
                    db.session.add(booking)
                    db.session.commit()
                    sesh.availability=sesh.availability-1
                    db.session.commit()
                    return redirect(url_for('cash', id = booking.id))
                else:
                    flash("You have already attempted to book this booking with cash. Please give your ID to an employee and pay to finalize your booking")
            if form.myField.data == "Card":
                if b is not None:
                    db.session.delete(b)
                booking=models.Booking(bookingDate = today,sessionId=sId,customerId=current_user.id, state = "Booked")#state = "pending"
                db.session.add(booking)
                db.session.commit()
                sesh.availability=sesh.availability-1
                db.session.commit()
                bookingreceipt=models.Receipt(type="Booking",customerId=current_user.id,dateOfPurchase=datetime.today(),bookingId=booking.id)
                db.session.add(bookingreceipt)
                db.session.commit()
                return redirect(url_for('receipt', id = booking.id))
        else:
            flash("You have already booked that activity for that time")
    if not form2.validate_on_submit():
        print(form.sessionId.data)
        print("Form not validated")
    if form2.validate_on_submit() and request.method == 'POST':
        print("form2 validated")
        print(form.sessionId.data)
        #get current user
        member=models.User.query.filter_by(id=current_user.id).first()
        #get current user's plan
        plan=member.plan
        #if no plan reject
        if plan=="No Plan":
            flash("You don't have a membership plan!")
            return redirect(url_for('plans'))
        sId = int(form2.sessionId.data)
        sesh=models.Session.query.filter_by(id=sId).first()
        if sesh.availability==0:
            flash("That activity is fully booked")
            # return redirect(url_for('table'))
        today = datetime.now()
        booking=models.Booking.query.filter_by( sessionId=sId,customerId=current_user.id, state = "Booked").first()
        b = models.Booking.query.filter_by( sessionId=sId,customerId=current_user.id, state = "Pending").first()
        if booking is None :
            booking=models.Booking(bookingDate = today,sessionId=sId,customerId=current_user.id, state = "Booked")#state = "pending"
            db.session.add(booking)
            db.session.commit()
            sesh.availability=sesh.availability-1
            db.session.commit()
            bookingreceipt=models.Receipt(type="Booking",customerId=current_user.id,dateOfPurchase=datetime.today(),bookingId=booking.id)
            db.session.add(bookingreceipt)
            db.session.commit()
            return redirect(url_for('receipt', id = booking.id))
        else:
            flash("You have already booked that activity for that time")
        
    return render_template('table.html',sessionList =sessionList, choices = choices, form = form, form2 = form2)


@app.route('/cash/<int:id>',methods=['GET','POST'])
@login_required(role="Customer")
def cash(id):
    return render_template('cashConfirm.html',id =id)


@app.route('/delete/<int:id>',methods=['POST'])
@login_required(role="Customer")
def delete(id):
    if request.method=='POST':
        booking=models.Booking.query.filter_by(sessionId=id,customerId=current_user.id, state = "Booked").first()
        b = models.Booking.query.filter_by(sessionId=id,customerId=current_user.id, state = "Pending").first()
        if booking is None and b is None:
            flash("You have not booked this session so you cannot unbook it")
            return redirect(url_for('table'))
        if booking is None:
            b.state = "Cancelled"
            db.session.commit()
            session=models.Session.query.filter_by(id=id).first()
            session.availability=session.availability+1
            db.session.commit()
        if b is None:
            booking.state = "Cancelled"
            db.session.commit()
            session=models.Session.query.filter_by(id=id).first()
            session.availability=session.availability+1
            db.session.commit()
        # file = "app/static/receipts/" + str(booking.id) + ".pdf"
        # os.remove(file)
    return redirect(url_for('mybookings'))

@app.route('/workout')
@login_required(role="Customer")
def workout():
    return render_template('workouts.html')


@app.route('/logout')
@login_required(role="ANY")
def logout():
    app.logger.info('Logging User id: %s Out', current_user.get_id())
    logout_user()#log user out
    return redirect('/home')


@app.route('/download/<id>', methods=['GET','POST'])
@login_required(role="Customer")
def download(id):
    print(id)
    return render_template('viewpdf.html', id = id)

@app.route('/receipt/<int:id>',methods=['GET','POST'])
@login_required(role="Customer")
def receipt(id):
    # id = 1
    booking = models.Booking.query.filter_by(id = id).first()
    customer = booking.user
    session = booking.session
    facility = models.Facility.query.filter_by(facilityName = session.facility).first()
    activity = models.Activity.query.filter_by(activityType = session.activity, facilityId = facility.id ).first()
    name = customer.name
    surname = customer.surname
    if surname is None:
        surname = " "
    td = booking.bookingDate.date()
    today = td.strftime("%d/%m/%Y")
    price = activity.price
    product = facility.facilityName
    bookingreceipt=models.Receipt.query.filter_by(bookingId=booking.id).first()

    dt = session.date
    dt_string = dt.strftime("%d/%m/%Y")
    tm_string = str(session.startTime) + ":00 - " + str(session.endTime) + ":00"

    file = "app/static/receipts/" + str(bookingreceipt.id) + ".pdf"
    print(customer.email)
    generatePdf.generate(name, surname,today,bookingreceipt.id, price, product,dt_string,tm_string,"Booking")
    sendEmail.sendReceipt(file, customer.email)
    return render_template('receipt.html' ,  date = today, recid = bookingreceipt.id,id=id, price = price, product = product, booking = booking, bookingDate = dt_string, bookingTime =tm_string)



@app.route('/timetable/<header>', methods = ['GET','POST'])
@login_required(role="Customer")
def timetable(header):
    create()

    booking = datetime.now()
    dt_string = booking.strftime("%d/%b/%Y")
    day = dt_string
    dt = datetime.strptime(day, '%d/%b/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    starts = start.strftime('%d/%b/%Y')
    ends = end.strftime('%d/%b/%Y')
    dates =[]
    stringDates = []
    startss = start.date()
    todayDate=_datetime.date.today()
    print(todayDate)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    for p in range(0,7):
        stringdate = startss.strftime('%d/%m/%Y')
        dates.append(startss)
        stringDates.append(stringdate)
        startss = startss + timedelta(days=1)
    for l in dates:
        print(l)


    days=[["Monday",stringDates[0],dates[0]],["Tuesday",stringDates[1],dates[1]],["Wednesday",stringDates[2],dates[2]],["Thursday",stringDates[3],dates[3]],["Friday",stringDates[4],dates[4]],["Saturday",stringDates[5],dates[5]],["Sunday",stringDates[6],dates[6]]]
    times=[["8","9"],["9","10"],["10","11"],["11","12"],["12","13"],["13","14"],["14","15"],["15","16"],["16","17"],["17","18"]]
    
    a = models.Session.query.all()
    return render_template("timetable.html", header = header, days = days, times = times, sessions =a, start = starts, end = ends, todayDate = todayDate, todayTime = current_time)

@app.route('/schedule/<facility>/<header>', methods = ['GET','POST'])
@login_required(role="Customer")
def schedule(facility,header):
    booking = datetime.now()
    dt_string = booking.strftime("%d/%b/%Y")
    day = dt_string
    dt = datetime.strptime(day, '%d/%b/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    starts = start.strftime('%d/%b/%Y')
    ends = end.strftime('%d/%b/%Y')
    dates =[]
    stringDates = []
    startss = start.date()
    todayDate=_datetime.date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(todayDate)
    for p in range(0,7):
        stringdate = startss.strftime('%d/%m/%Y')
        dates.append(startss)
        stringDates.append(stringdate)
        startss = startss + timedelta(days=1)
    for l in dates:
        print(l)
    
    days=[["Monday",stringDates[0],dates[0]],["Tuesday",stringDates[1],dates[1]],["Wednesday",stringDates[2],dates[2]],["Thursday",stringDates[3],dates[3]],["Friday",stringDates[4],dates[4]],["Saturday",stringDates[5],dates[5]],["Sunday",stringDates[6],dates[6]]]

    times=[["8","9"],["9","10"],["10","11"],["11","12"],["12","13"],["13","14"],["14","15"],["15","16"],["16","17"],["17","18"]]

    
    a = models.Session.query.filter_by(facility = facility)
    return render_template("timetable.html",header = header, days = days, times = times, sessions =a,start = starts, end = ends, todayDate = todayDate, todayTime = current_time)


def create():
    a=models.Facility.query.filter_by(facilityName="Swimming Pool").first()
    if a is None:

        swimmingPool=models.Facility(facilityName="Swimming Pool",capacity=32)

        db.session.add(swimmingPool)
        db.session.commit()

        activity=models.Activity(activityType="General Use",price=0,facilityId=swimmingPool.id)
        activity1=models.Activity(activityType="Lane Swimming",price=0,facilityId=swimmingPool.id)
        activity2=models.Activity(activityType="Swimming Lessons",price=5,facilityId=swimmingPool.id)
        activity3=models.Activity(activityType="Team events",price=5,facilityId=swimmingPool.id)

        db.session.add(activity)
        db.session.add(activity1)
        db.session.add(activity2)
        db.session.add(activity3)
        db.session.commit()


    a=models.Facility.query.filter_by(facilityName="Fitness room").first()
    print(a)
    if a is None:

        fitnessRoom=models.Facility(facilityName="Fitness room",capacity=25)

        db.session.add(fitnessRoom)
        db.session.commit()

        activity4=models.Activity(activityType="General use",price=0,facilityId=fitnessRoom.id)

        db.session.add(activity4)
        db.session.commit()


    a=models.Facility.query.filter_by(facilityName="Squash room-1").first()
    if a is None:
        squashRoom=models.Facility(facilityName="Squash room-1",capacity=4)

        db.session.add(squashRoom)
        db.session.commit()

        activity5=models.Activity(activityType="1-hour Session",price=0,facilityId=squashRoom.id)
        activity6=models.Activity(activityType="Team Event",price=0,facilityId=squashRoom.id)

        db.session.add(activity5)
        db.session.add(activity6)
        db.session.commit()

    a=models.Facility.query.filter_by(facilityName="Squash room-2").first()
    if a is None:
        squashRoom2=models.Facility(facilityName="Squash room-2",capacity=4)

        db.session.add(squashRoom2)
        db.session.commit()

        activity7=models.Activity(activityType="1-hour Session",price=0,facilityId=squashRoom2.id)
        activity8=models.Activity(activityType="Team Event",price=0,facilityId=squashRoom2.id)

        db.session.add(activity7)
        db.session.add(activity8)
        db.session.commit()

    a=models.Facility.query.filter_by(facilityName="Squash room-3").first()
    if a is None:
        squashRoom3=models.Facility(facilityName="Squash room-3",capacity=4)

        db.session.add(squashRoom3)
        db.session.commit()

        activity9=models.Activity(activityType="1-hour Session",price=0,facilityId=squashRoom3.id)
        activity10=models.Activity(activityType="Team Event",price=0,facilityId=squashRoom3.id)

        db.session.add(activity9)
        db.session.add(activity10)
        db.session.commit()

    a=models.Facility.query.filter_by(facilityName="Squash room-4").first()
    if a is None:
        squashRoom4=models.Facility(facilityName="Squash room-4",capacity=4)

        db.session.add(squashRoom4)
        db.session.commit()

        activity11=models.Activity(activityType="1-hour Session",price=0,facilityId=squashRoom4.id)
        activity12=models.Activity(activityType="Team Event",price=0,facilityId=squashRoom4.id)

        db.session.add(activity11)
        db.session.add(activity12)
        db.session.commit()

    a=models.Facility.query.filter_by(facilityName="Sports Hall").first()
    if a is None:
        sportsHall=models.Facility(facilityName="Sports Hall",capacity=20)

        db.session.add(sportsHall)
        db.session.commit()

        activity13=models.Activity(activityType="1-hour Session",price=0,facilityId=sportsHall.id)

        db.session.add(activity13)
        db.session.commit()


    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    times=[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14],[14,15],[15,16],[16,17],[17,18],[18,19],[19,20],[20,21],[21,22],[22,23],[23,24]]
    f = models.Session.query.filter_by(day = days[0]).first()

    dates =[]
    #get current datetime
    booking = datetime.now()

    dt_string = booking.strftime("%d/%m/%Y")
    day = dt_string

    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    starts = start.date()
    

    for p in range(0,7):
        dates.append(starts)
        starts = starts + timedelta(days=1)

    s=models.Session.query.all()
    sessionCounter=0
    date = _datetime.datetime.today()
    start_wee = date - _datetime.timedelta(date.weekday())
    start_week = start_wee.replace(hour=0, minute=0)
    end_week = start_week + _datetime.timedelta(7)
    for i in s:
        if(i.date>=start_week.date() and i.date<=end_week.date()):
            sessionCounter+=1
   
    if sessionCounter==0:
        Monday=models.Session(date = dates[0],day = "Monday", startTime = 10, endTime = 11,facility="Squash room-4", activity = "1-hour Session",availability=4)
        Monday3=models.Session(date = dates[0],day = "Monday", startTime = 10, endTime = 11,facility="Squash room-4", activity = "Team Event",availability=4)
        Tuesday=models.Session(date = dates[1],day = "Tuesday", startTime = 11, endTime = 12,facility="Swimming Pool", activity = "Lane Swimming",availability=32)
        Tuesday1=models.Session(date = dates[1],day = "Tuesday", startTime = 11, endTime = 12,facility="Swimming Pool", activity = "Team events",availability=32)
        Wednesday =models.Session(date = dates[2], day = "Wednesday", startTime = 12, endTime = 13,facility="Fitness room", activity = "General use",availability=25)
        Thursday =models.Session(date = dates[3], day = "Thursday", startTime = 13, endTime = 14,facility="Sports Hall", activity = "1-hour Session",availability=20)
        Friday =models.Session(date = dates[4], day = "Friday", startTime = 14, endTime = 15,facility="Swimming Pool", activity = "Swimming Lessons",availability=32)
        Saturday =models.Session(date = dates[5], day = "Saturday", startTime = 12, endTime = 13,facility="Squash room-2", activity = "Team Event",availability=4)
        Sunday =models.Session(date = dates[6], day = "Sunday", startTime = 11, endTime = 12,facility="Swimming Pool", activity = "Team events",availability=32)
        Monday2=models.Session(date = dates[0], day = "Monday", startTime = 10, endTime = 11,facility="Squash room-3", activity = "1-hour Session",availability=4)
        db.session.add(Monday)
        db.session.add(Tuesday)
        db.session.add(Tuesday1)
        db.session.add(Wednesday)
        db.session.add(Thursday)
        db.session.add(Friday)
        db.session.add(Saturday)
        db.session.add(Sunday)
        db.session.add(Monday2)
        db.session.add(Monday3)
        db.session.commit()
