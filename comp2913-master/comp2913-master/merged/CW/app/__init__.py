from os.path import join, dirname, realpath
import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin import helpers as admin_helpers
from flask_migrate import Migrate
from flask_wtf import CsrfProtect
from flask_login import LoginManager
import stripe
import logging
from logging.handlers import RotatingFileHandler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import _datetime



app = Flask(__name__)
app.config.from_object('config')
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login=LoginManager(app)
stripe_keys = {
    'secret_key': "sk_test_M3P2bVZ8VMVmyfnHvjmHiLhr00BeinvoQm",
    'publishable_key': "pk_test_kS2fgWK3bzaUmelIMambPIxc00KK3aljfB"
}

stripe.api_key = stripe_keys['secret_key']
CsrfProtect(app)

from flask_admin import AdminIndexView, expose

#Admin's email:STC@gmail.com
        #password:12345

#generates income and usage for all facilities,sessions and activities, used as an index view for admins and employees
class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        lists=[]
        bookings2=[]
        pricesAll=0.0
        sportsPrice=0.0
        fitnessPrice=0.0
        teamPrice=0.0
        lessonsPrice=0.0
        laneSwimmingPrice=0.0
        swimmingPoolPrice=0.0
        SR1=0.0
        SR2=0.0
        SR3=0.0
        SR4=0.0
        row=[]
        bookingsCounter=0
        fitnessCounter=0
        sportsCounter=0
        swimmingCounter=0
        laneSwimming=0
        lessonsCounter=0
        teamEventsCounter=0
        sr4c=0
        sr3c=0
        sr2c=0
        sr1c=0
        sr1_1hourC=0
        SR1_1hourPrice=0
        sr2_1hourC=0
        SR2_1hourPrice=0
        sr3_1hourC=0
        SR3_1hourPrice=0
        sr4_1hourC=0
        SR4_1hourPrice=0
        sr1_teamC=0
        SR1_TeamPrice=0
        sr2_teamC=0
        SR2_TeamPrice=0
        sr3_teamC=0
        SR3_TeamPrice=0
        sr4_teamC=0
        SR4_TeamPrice=0
        date = _datetime.datetime.today()
        start_wee = date - _datetime.timedelta(date.weekday())
        start_week = start_wee.replace(hour=0, minute=0)
        end_week = start_week + _datetime.timedelta(7)
        bookings=models.Booking.query.all()
        sesh=models.Session.query.all()
        sessions2=[]
        sessionCounter=0
        for i in bookings:
            if(i.bookingDate>=start_week and i.bookingDate<=end_week and i.state!="Cancelled"):
                bookingsCounter+=1
                bookings2.append(i)
        for i in sesh:
            if(i.date>=start_week.date() and i.date<=end_week.date()):
                sessionCounter+=1
                sessions2.append(i)
        for i in bookings2:
            session=models.Session.query.filter_by(id=i.sessionId).first()
            activity=models.Activity.query.filter_by(activityType=session.activity).first()
            pricesAll=pricesAll+activity.price
            if(session.facility=="Fitness room"):
                fitnessCounter+=1
                fitnessPrice=fitnessPrice+activity.price
            if(session.facility=="Sports Hall"):
                sportsCounter+=1
                sportsPrice=sportsPrice + activity.price
            if(session.facility=="Swimming Pool"):
                swimmingCounter+=1
                swimmingPoolPrice+=activity.price
                if(session.activity=="Lane Swimming"):
                    laneSwimming+=1
                    laneSwimmingPrice=laneSwimmingPrice+activity.price
                if(session.activity=="Swimming Lessons"):
                    lessonsCounter+=1
                    lessonsPrice=lessonsPrice+activity.price
                if(session.activity=="Team Event"):
                    teamEventsCounter+=1
                    teamPrice=teamPrice+activity.price
            if(session.facility=="Squash room-4"):
                SR4+=activity.price
                sr4c+=1
                if(session.activity=="1-hour Session"):
                    sr4_1hourC+=1
                    SR4_1hourPrice+=activity.price
                if(session.activity=="Team Event"):
                    sr4_teamC+=1
                    SR4_TeamPrice+=activity.price
            if(session.facility=="Squash room-3"):
                SR3+=activity.price
                sr3c+=1
                if(session.activity=="1-hour Session"):
                    sr3_1hourC+=1
                    SR4_1hourPrice+=activity.price
                if(session.activity=="Team Event"):
                    sr3_teamC+=1
                    SR3_TeamPrice+=activity.price
            if(session.facility=="Squash room-2"):
                SR2+=activity.price
                sr2c+=1
                if(session.activity=="1-hour Session"):
                    sr2_1hourC+=1
                    SR2_1hourPrice+=activity.price
                if(session.activity=="Team Event"):
                    sr2_teamC+=1
                    SR2_TeamPrice+=activity.price
            if(session.facility=="Squash room-1"):
                SR1+=activity.price
                sr1c+=1
                if(session.activity=="1-hour Session"):
                    sr1_1hourC+=1
                    SR1_1hourPrice+=activity.price
                if(session.activity=="Team Event"):
                    sr1_teamC+=1
                    SR1_TeamPrice+=activity.price 
        for i in sessions2:
            sum=0
            sessionC=0
            activity=models.Activity.query.filter_by(activityType=i.activity).first()
            bookings=models.Booking.query.filter_by(sessionId=i.id).all()
            for j in bookings:
                if j.state!='Cancelled':
                    sum+=activity.price
                    sessionC+=1
            lists.append((i,sum,sessionC))
        
        value=([row[1] for row in lists])
        sessionAct=([row[2] for row in lists])
        label=[]
        for f in lists:
            tmp=str(f[0].getDate() )+ " " + f[0].getTime() + " " + f[0].getActivity()  
            label.append(tmp)
                
        return self.render('admin/index.html',priceAll=pricesAll,SR1=SR1,SR2=SR2,SR3=SR3,SR4=SR4,teamPrice=teamPrice,lessonsPrice=lessonsPrice,fitnessPrice=fitnessPrice,laneSwimmingPrice=laneSwimmingPrice,sportsPrice=sportsPrice
                                            ,bookingsCounter=bookingsCounter,sr1c=sr1c,sr2c=sr2c,sr3c=sr3c,sr4c=sr4c,teamEventsCounter=teamEventsCounter,laneSwimming=laneSwimming,lessonsCounter=lessonsCounter,fitnessCounter=fitnessCounter,sportsCounter=sportsCounter,swimmingCounter=swimmingCounter
                                            ,swimmingPoolPrice=swimmingPoolPrice,sr1_1hourC=sr1_1hourC,SR1_1hourPrice=SR1_1hourPrice,sr2_1hourC=sr2_1hourC,SR2_1hourPrice=SR2_1hourPrice,sr3_1hourC=sr3_1hourC,SR3_1hourPrice=SR3_1hourPrice,sr4_1hourC=sr4_1hourC,SR4_1hourPrice=SR4_1hourPrice,
                                            sr4_teamC=sr4_teamC,SR4_TeamPrice=SR4_TeamPrice,sr3_teamC=sr3_teamC,SR3_TeamPrice=SR3_TeamPrice,sr2_teamC=sr2_teamC,SR2_TeamPrice=SR2_TeamPrice,sr1_teamC=sr1_teamC,SR1_TeamPrice=SR1_TeamPrice,lists=lists,value=value,sessionAct=sessionAct,label=label)





admin = Admin(
        app,
        name = '19 Gym',
        # base_template = 'layout.html',
        template_mode='bootstrap3',
        index_view = MyHomeView()
        )





from app import views,models
from app.models import Facility

#logging system:
if not app.debug:

    if not os.path.exists('logs'):
        os.mkdir('logs')
    format = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler = RotatingFileHandler('logs/19Gym.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(format)
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info('19 Gym startup')

