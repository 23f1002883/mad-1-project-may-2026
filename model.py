from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable = False)
    status = db.Column(db.String, default = 'pending')
    contact = db.Column(db.String, nullable = True)

class treks(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, unique = True, nullable = False)
    location = db.Column(db.String, nullable = False, default = 'Unknown')
    difficulty = db.Column(db.String, nullable = False)
    duration = db.Column(db.Integer, nullable=False, default=1)  
    available_slot = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default='open')  
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=True) 
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    

class bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.String, default=datetime.now().strftime('%Y-%m-%d')) 
    status = db.Column(db.String, default='Booked')