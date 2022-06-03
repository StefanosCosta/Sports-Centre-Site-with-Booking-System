from app import app, stripe_keys,models,db
import stripe
from flask import Flask, url_for, redirect, render_template, request, abort, flash
from flask_security import login_required, login_user
from app.forms import *
import authenticate
import logging
#from app.models import User

# Flask views
@app.route('/')
def index():
    return render_template('index.html', title = 'Home')

@app.route('/payment')
@login_required
def payment():
    return render_template('payment.html', title='Checkout',header="Checkout",key = stripe_keys['publishable_key'])

@app.route('/admin/')
def admin():
    return render_template('admin/admin.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(request.form,meta={'csrf': True})
    #print("here")
    if form.validate_on_submit():
        #print("here")
        if form.email.data == "admin@admin.com" and form.password.data == "admin":
            return redirect(url_for("admin"))
        user = models.User.query.filter_by(email=form.email.data).first()
        if not authenticate.logInUser(form):
            flash('Invalid username or password')
        else:
            login_user(user, remember=form.remember.data)
            app.logger.info('User with id %s successfully logged in',user.id)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                app.logger.info('rerouting to home')
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('security/login.html', title='Log In', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CustomerForm(request.form,meta={'csrf': True})
    print("signup")
    # p = models.User(name = "stefa", surname = "costa", email = "stefcost@gmail.com", password = "12345678")
    # db.session.add(p)
    # db.session.commit()
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

@app.route('/ppl', methods=['GET', 'POST'])
def allposts():
    users=models.User.query.all()
    return render_template('ppl.html',users=users,title='Posts')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/activity')
def activity():
    return render_template('activity.html')

@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/table', methods=['GET','POST'])
def table():
    return render_template('table.html')

@app.route('/workout')
def workout():
    return render_template('workouts.html')

@app.route('/logout')
def logout():
    app.logger.info('Logging User id: %s Out', current_user.get_id())
    logout_user()#log user out
    return redirect('/home')
