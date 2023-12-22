from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db=SQLAlchemy()

class User(UserMixin, db.Model):  #usermixin just add some functionality to the class regarding login
  """User model"""
  __tablename__="userswithemail"
  id=db.Column(db.Integer, primary_key=True)
  email=db.Column(db.String(), unique=True, nullable=False)
  password=db.Column(db.String(), nullable=False)

class Orders(db.Model):  
  """Order model"""
  __tablename__="orders"
  customer=db.Column(db.String(), nullable=False)
  customernumber = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
  orderitem=db.Column(db.String(), nullable=False)
  orderstatus=db.Column(db.String(), nullable=False)