from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path

# db.drop_all()
db.create_all()
