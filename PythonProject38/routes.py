from datetime import timezone
from flask import render_template, redirect, url_for, flash, session, request, Blueprint
from datetime import datetime, timezone
from extensions import db
from models import User, Task
from forms import RegisterForm, LoginForm, TaskForm

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return redirect(url_for("main.login"))

def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user():
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.")
            return redirect(url_for("main.register"))
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.")
            return redirect(url_for("main.register"))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully. Please log in.")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.")
            return redirect(url_for("main.login"))

        session["user_id"] = user.id
        flash("Logged in successfully.")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)

@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.")
    return redirect(url_for("main.login"))

@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("main.login"))

    form = TaskForm()

    if form.validate_on_submit():
        task_name = form.name.data.strip()
        local_dt = form.deadline.data
        now_utc = datetime.now(timezone.utc)

        if not task_name:
            flash("Error: Task name cannot be empty.")
            return redirect(url_for("main.dashboard"))

        deadline_utc = local_dt.replace(tzinfo=timezone.utc)
        if deadline_utc < now_utc:
            flash("Error: Deadline cannot be in the past.")
            return redirect(url_for("main.dashboard"))

        task = Task(
            name=task_name,
            deadline=deadline_utc,
            status="Pending",
            user_id=user.id,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully.")
        return redirect(url_for("main.dashboard"))

    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.deadline.asc()).all()

    show = request.args.get("show", "all")
    if show == "pending":
        tasks = [t for t in tasks if t.status != "Done"]
    elif show == "done":
        tasks = [t for t in tasks if t.status == "Done"]

    return render_template("dashboard.html", form=form, tasks=tasks, user=user, show=show)

@bp.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("main.login"))

    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Not allowed.")
        return redirect(url_for("main.dashboard"))

    # S3: completion tracking
    task.mark_done()
    db.session.commit()
    flash("Task marked as done.")
    return redirect(url_for("main.dashboard"))

@bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("main.login"))

    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Not allowed.")
        return redirect(url_for("main.dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.")
    return redirect(url_for("main.dashboard"))
