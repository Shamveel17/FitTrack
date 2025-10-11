from datetime import date, timedelta
from .models import Meal, Workout, Progress
from . import db
from flask_login import current_user
from sqlalchemy import func

def get_ai_advice():
    """
    Gives simple rule-based fitness advice .
    Uses the last 1-2 weeks of data.
    """
    try:
        today = date.today()
        start_date = today - timedelta(days=14)  # last 2 weeks

        # Meals summary
        protein, carbs, fats, calories = db.session.query(
            func.coalesce(func.sum(Meal.protein), 0.0),
            func.coalesce(func.sum(Meal.carbs), 0.0),
            func.coalesce(func.sum(Meal.fats), 0.0),
            func.coalesce(func.sum(Meal.calories), 0.0)
        ).filter(Meal.user_id == current_user.id,
                 Meal.date >= start_date).one()

        # Workouts summary
        workout_count = db.session.query(func.count(Workout.id)).filter(
            Workout.user_id == current_user.id,
            Workout.date >= start_date
        ).scalar()

        # Weight trend
        progress = db.session.query(Progress.date, Progress.weight).filter(
            Progress.user_id == current_user.id,
            Progress.date >= start_date,
            Progress.weight.isnot(None)
        ).order_by(Progress.date).all()

        weight_change = None
        if len(progress) >= 2:
            weight_change = progress[-1][1] - progress[0][1]

        # ---- Rules ----
        advice = []

        # Protein guideline: ~1.6–2.2g per kg of bodyweight (let’s assume 70kg = ~120g min)
        if protein < 120:
            advice.append(" Increase protein intake — aim for at least 120g per day.")
        else:
            advice.append(" Good protein intake! Keep it consistent.")

        # Calories
        avg_cals = calories / 14 if calories else 0
        if avg_cals < 1800:
            advice.append(" Calories seem very low — make sure you're fueling enough.")
        elif avg_cals > 3000:
            advice.append(" High calorie intake — watch portion sizes if fat loss is a goal.")
        else:
            advice.append(" Calories look balanced.")

        # Workouts
        if workout_count < 4:
            advice.append(f" Only {workout_count} workouts in 2 weeks — try to increase frequency.")
        else:
            advice.append(f" Solid! {workout_count} workouts logged in the last 2 weeks.")

        # Weight
        if weight_change is not None:
            if weight_change < -1:
                advice.append(f" You lost {abs(weight_change):.1f} kg — ensure it's not too rapid.")
            elif weight_change > 1:
                advice.append(f" You gained {weight_change:.1f} kg — check if this aligns with your goal.")
            else:
                advice.append(" Weight is stable — good for maintenance.")

        if not advice:
            advice = [" Not enough data yet. Log meals, workouts, and progress to see advice."]

        return " ".join(advice)

    except Exception as e:
        print("Rule-based AI error:", e)
        return "AI Coach advice not available right now."
