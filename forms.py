from flask_wtf import FlaskForm
from wtforms import ( StringField, IntegerField, SubmitField, DateField, FloatField)
from wtforms.validators import (DataRequired, Length, NumberRange)

class WorkoutForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    exercise = StringField("Workout Name", validators=[DataRequired(), Length(min=2, max=50)])
    sets = IntegerField("Sets", validators=[DataRequired(), NumberRange(min=1, max=50)])
    reps = IntegerField("Reps", validators=[DataRequired(), NumberRange(min=1, max=100)])
    duration = IntegerField("Duration (mins)", validators=[DataRequired(), NumberRange(min=1, max=300)])
    weight = FloatField("Weight (kg)")
    submit = SubmitField("Save Workout")

