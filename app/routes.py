from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from . import db
from .ai_coach import get_ai_advice
from .forms import RegisterForm, LoginForm, WorkoutForm, MealForm, ProgressForm, GoalForm
from .models import User, Workout, Meal, Progress, Goal

# -------------------------
# Blueprint
# -------------------------
main = Blueprint("main", __name__)

# -------------------------
# Home / Auth
# -------------------------
@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=16
        )
        new_user = User(
            name=form.name.data, email=form.email.data, password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# -------------------------
# Dashboard
# -------------------------
@main.route("/dashboard")
@login_required
def dashboard():
    today = date.today()

    # Recent items
    workouts = (
        Workout.query.filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc())
        .limit(5)
        .all()
    )
    meals = (
        Meal.query.filter_by(user_id=current_user.id)
        .order_by(Meal.date.desc())
        .limit(5)
        .all()
    )
    progress = (
        Progress.query.filter_by(user_id=current_user.id)
        .order_by(Progress.date.desc())
        .limit(5)
        .all()
    )

    # Workouts per week (last 8 weeks)
    start_8w = today - timedelta(days=56)
    weekly = (
        db.session.query(
            func.strftime("%Y-%W", Workout.date).label("yw"), func.count(Workout.id)
        )
        .filter(Workout.user_id == current_user.id, Workout.date >= start_8w)
        .group_by("yw")
        .order_by("yw")
        .all()
    )
    weekly_labels = [w[0] for w in weekly]
    weekly_data = [int(w[1]) for w in weekly]

    # Daily calories (last 14 days)
    start_14d = today - timedelta(days=13)
    cals = (
        db.session.query(Meal.date, func.coalesce(func.sum(Meal.calories), 0.0))
        .filter(Meal.user_id == current_user.id, Meal.date >= start_14d)
        .group_by(Meal.date)
        .order_by(Meal.date)
        .all()
    )
    cal_labels = [d[0].strftime("%Y-%m-%d") for d in cals]
    cal_values = [float(d[1] or 0) for d in cals]

    # Macro split (last 7 days)
    start_7d = today - timedelta(days=6)
    protein, carbs, fats = (
        db.session.query(
            func.coalesce(func.sum(Meal.protein), 0.0),
            func.coalesce(func.sum(Meal.carbs), 0.0),
            func.coalesce(func.sum(Meal.fats), 0.0),
        )
        .filter(Meal.user_id == current_user.id, Meal.date >= start_7d)
        .one()
    )

    # Weight trend (last 90 days)
    start_90d = today - timedelta(days=90)
    wpoints = (
        db.session.query(Progress.date, Progress.weight)
        .filter(
            Progress.user_id == current_user.id,
            Progress.date >= start_90d,
            Progress.weight.isnot(None),
        )
        .order_by(Progress.date)
        .all()
    )
    weight_labels = [wp[0].strftime("%Y-%m-%d") for wp in wpoints]
    weight_values = [float(wp[1]) for wp in wpoints]

    # AI advice
    try:
        ai_advice = get_ai_advice()
    except Exception as e:
        print("AI coach error:", e)
        ai_advice = "No advice available right now."

    # Upcoming goals
    upcoming_goals = Goal.query.filter(
        Goal.deadline >= today,
        Goal.deadline <= today + timedelta(days=3),
        Goal.completed == False,
    ).all()

    return render_template(
        "dashboard.html",
        workouts=workouts,
        meals=meals,
        progress=progress,
        weekly_labels=weekly_labels,
        weekly_data=weekly_data,
        cal_labels=cal_labels,
        cal_values=cal_values,
        protein=float(protein or 0),
        carbs=float(carbs or 0),
        fats=float(fats or 0),
        weight_labels=weight_labels,
        weight_values=weight_values,
        ai_advice=ai_advice,
        goals=upcoming_goals,
    )

# -------------------------
# Workouts CRUD
# -------------------------
@main.route("/workouts")
@login_required
def workouts():
    user_workouts = (
        Workout.query.filter_by(user_id=current_user.id)
        .order_by(Workout.date.desc())
        .all()
    )
    return render_template("workouts.html", workouts=user_workouts)

@main.route("/workouts/add", methods=["GET", "POST"])
@login_required
def add_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            user_id=current_user.id,
            date=form.date.data,
            exercise=form.exercise.data,
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
            duration=form.duration.data,
        )
        db.session.add(workout)
        db.session.commit()
        flash("Workout added!", "success")
        return redirect(url_for("main.workouts"))
    if request.method == "POST":
        flash(f"Form errors: {form.errors}", "danger")
    return render_template("workout_form.html", form=form, action="Add")

@main.route("/workouts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.workouts"))

    form = WorkoutForm(obj=workout)
    if form.validate_on_submit():
        workout.date = form.date.data
        workout.exercise = form.exercise.data
        workout.sets = form.sets.data
        workout.reps = form.reps.data
        workout.weight = form.weight.data
        db.session.commit()
        flash("Workout updated!", "success")
        return redirect(url_for("main.workouts"))

    return render_template("workout_form.html", form=form, action="Edit")

@main.route("/workouts/delete/<int:id>")
@login_required
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.workouts"))

    db.session.delete(workout)
    db.session.commit()
    flash("Workout deleted!", "info")
    return redirect(url_for("main.workouts"))

# -------------------------
# Meals CRUD
# -------------------------
@main.route("/meals")
@login_required
def meals():
    user_meals = (
        Meal.query.filter_by(user_id=current_user.id)
        .order_by(Meal.date.desc())
        .all()
    )
    return render_template("meals.html", meals=user_meals)

@main.route("/meals/add", methods=["GET", "POST"])
@login_required
def add_meal():
    form = MealForm()
    if form.validate_on_submit():
        meal = Meal(
            user_id=current_user.id,
            date=form.date.data,
            meal_name=form.meal_name.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
        )
        db.session.add(meal)
        db.session.commit()
        flash("Meal added!", "success")
        return redirect(url_for("main.meals"))
    return render_template("meal_form.html", form=form, action="Add")

@main.route("/meals/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_meal(id):
    meal = Meal.query.get_or_404(id)
    if meal.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.meals"))

    form = MealForm(obj=meal)
    if form.validate_on_submit():
        meal.date = form.date.data
        meal.meal_name = form.meal_name.data
        meal.calories = form.calories.data
        meal.protein = form.protein.data
        meal.carbs = form.carbs.data
        meal.fats = form.fats.data
        db.session.commit()
        flash("Meal updated!", "success")
        return redirect(url_for("main.meals"))

    return render_template("meal_form.html", form=form, action="Edit")

@main.route("/meals/delete/<int:id>")
@login_required
def delete_meal(id):
    meal = Meal.query.get_or_404(id)
    if meal.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.meals"))

    db.session.delete(meal)
    db.session.commit()
    flash("Meal deleted!", "info")
    return redirect(url_for("main.meals"))

# -------------------------
# Progress CRUD
# -------------------------
@main.route("/progress")
@login_required
def progress_list():
    user_progress = (
        Progress.query.filter_by(user_id=current_user.id)
        .order_by(Progress.date.desc())
        .all()
    )
    return render_template("progress.html", progress=user_progress)

@main.route("/progress/add", methods=["GET", "POST"])
@login_required
def add_progress():
    form = ProgressForm()
    if form.validate_on_submit():
        prog = Progress(
            user_id=current_user.id,
            date=form.date.data,
            weight=form.weight.data,
            notes=form.notes.data,
        )
        db.session.add(prog)
        db.session.commit()
        flash("Progress added!", "success")
        return redirect(url_for("main.progress_list"))
    return render_template("progress_form.html", form=form, action="Add")

@main.route("/progress/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_progress(id):
    prog = Progress.query.get_or_404(id)
    if prog.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.progress_list"))

    form = ProgressForm(obj=prog)
    if form.validate_on_submit():
        prog.date = form.date.data
        prog.weight = form.weight.data
        prog.notes = form.notes.data
        db.session.commit()
        flash("Progress updated!", "success")
        return redirect(url_for("main.progress_list"))

    return render_template("progress_form.html", form=form, action="Edit")

@main.route("/progress/delete/<int:id>")
@login_required
def delete_progress(id):
    prog = Progress.query.get_or_404(id)
    if prog.user_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.progress_list"))

    db.session.delete(prog)
    db.session.commit()
    flash("Progress deleted!", "info")
    return redirect(url_for("main.progress_list"))

# -------------------------
# Goals CRUD
# -------------------------
@main.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            target_weight=form.target_weight.data,
            deadline=form.deadline.data,
            focus=form.focus.data,
            user_id=current_user.id,
        )
        db.session.add(goal)
        db.session.commit()
        flash("Goal added successfully!", "success")
        return redirect(url_for("main.goals"))

    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template("goals.html", form=form, goals=goals)

@main.route("/goals/add", methods=["GET", "POST"])
@login_required
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            target_weight=form.target_weight.data,
            deadline=form.deadline.data,
            focus=form.focus.data,
            user_id=current_user.id,
        )
        db.session.add(goal)
        db.session.commit()
        flash("Goal added successfully!", "success")
        return redirect(url_for("main.goals"))
    return render_template("goals_form.html", action="Add", form=form)

@main.route("/goals/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_goal(id):
    goal = Goal.query.get_or_404(id)
    form = GoalForm(obj=goal)
    if form.validate_on_submit():
        goal.target_weight = form.target_weight.data
        goal.deadline = form.deadline.data
        goal.focus = form.focus.data
        db.session.commit()
        flash("Goal updated successfully!", "success")
        return redirect(url_for("main.goals"))
    return render_template("goals_form.html", action="Edit", form=form, goal=goal)

@main.route("/goals/delete/<int:id>")
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for("main.goals"))

@main.route("/goals/<int:goal_id>/complete", methods=["POST"])
@login_required
def complete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    goal.completed = True
    db.session.commit()
    return redirect(url_for("main.goals"))
