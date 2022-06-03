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
#from flask_login import LoginManager
import stripe
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
stripe_keys = {
    'secret_key': "sk_test_M3P2bVZ8VMVmyfnHvjmHiLhr00BeinvoQm",
    'publishable_key': "pk_test_kS2fgWK3bzaUmelIMambPIxc00KK3aljfB"
}

stripe.api_key = stripe_keys['secret_key']
#CsrfProtect(app)




admin = flask_admin.Admin(
    app,
    name='test',
    base_template='layout.html',
    url='/admin/admin.html'
    #template_mode='bootstrap3',
)
from app import views,models
from app.models import *
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

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


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(User, db.session))
