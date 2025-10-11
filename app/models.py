from . import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---- User ----
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy=True)
    meals = db.relationship('Meal', backref='user', lazy=True)
    progress = db.relationship('Progress', backref='user', lazy=True)
    goals = db.relationship("Goal", back_populates="user", lazy=True)

# ---- Workouts ----
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # optional
    

# ---- Meals ----
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_name = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Float, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fats = db.Column(db.Float, nullable=True)

# ---- Progress ----
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

from app import db
from datetime import date

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_weight = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    focus = db.Column(db.String(20), nullable=False)  # "gain", "loss", "strength"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="goals")
   
