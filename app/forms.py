from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField,
    IntegerField, FloatField, DateField,
    TextAreaField, SelectField
)
from wtforms.validators import (
    InputRequired, DataRequired, Length,
    Email, EqualTo
)

# ---------------------- Auth Forms ----------------------

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


# ---------------------- Workout Form ----------------------

class WorkoutForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    exercise = StringField("Exercise", validators=[DataRequired(), Length(min=2, max=100)])
    sets = IntegerField("Sets", validators=[DataRequired()])
    reps = IntegerField("Reps", validators=[DataRequired()])
    duration = IntegerField("Duration", validators=[DataRequired()])
    weight = FloatField("Weight (kg)")
    submit = SubmitField("Save")


# ---------------------- Meal Form ----------------------

class MealForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    meal_name = StringField("Meal Name", validators=[DataRequired(), Length(min=2, max=200)])
    calories = FloatField("Calories")
    protein = FloatField("Protein (g)")
    carbs = FloatField("Carbs (g)")
    fats = FloatField("Fats (g)")
    submit = SubmitField("Save")


# ---------------------- Progress Form ----------------------

class ProgressForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    weight = FloatField("Weight (kg)")
    notes = TextAreaField("Notes")
    submit = SubmitField("Save")


# ---------------------- Goal Form ----------------------

class GoalForm(FlaskForm):
    target_weight = FloatField("Target Weight (kg)", validators=[DataRequired()])
    deadline = DateField("Deadline", validators=[DataRequired()])
    focus = SelectField(
        "Focus",
        choices=[("gain", "Gain"), ("loss", "Loss"), ("strength", "Strength")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Save Goal")
