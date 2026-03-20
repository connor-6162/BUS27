from datetime import datetime,timezone
from flask import render_template, redirect, url_for, flash, session, request, Blueprint

from extensions import db
from models import User, Task
from forms import RegisterForm, LoginForm, TaskForm

bp = Blueprint("main", __name__)

#test user
SIMULATED_USERS = {
    1: {"username": "Li Hua", "email": "lihua@uni.edu", "password": "lihua123"},
    2: {"username": "Lucy", "email": "lucy@uni.edu", "password": "lucy123"}
}

@bp.route("/")
def index():
    return redirect(url_for("main.landing"))

#landing page
@bp.route("/landing")
def landing():
    # link to dashboard
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")

@bp.route("/simulate_login/<int:profile_id>")
def simulate_login(profile_id):
    #check profile id
    if profile_id not in SIMULATED_USERS:
        flash("Invalid profile selection.")
        return redirect(url_for("main.landing"))

    user_data = SIMULATED_USERS[profile_id]

#search or auto create profile
    user = User.query.filter_by(email=user_data["email"]).first()
    if not user:
        user = User(username=user_data["username"], email=user_data["email"])
        user.set_password(user_data["password"])
        db.session.add(user)
        db.session.commit()
        test_tasks = [
            Task(name="CS Coursework (Due Soon)",
                 deadline=datetime.now(timezone.utc).replace(hour=23, minute=59, second=59),
                 status="Pending", user_id=user.id),
            Task(name="Math Problem Set",
                 deadline=datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day+2),
                 status="Pending", user_id=user.id),
            Task(name="Biology Lab Report (Completed)",
                 deadline=datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day-1),
                 status="Done", user_id=user.id)
        ]
        db.session.add_all(test_tasks)
        flash(f"Welcome, {user.username}!")
    else:
        flash(f"Welcome back, {user.username}!")
    session["user_id"] = user.id
    return redirect(url_for("main.dashboard"))

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
    return redirect(url_for("main.landing"))

@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("main.landing"))

    form = TaskForm()

    # S1: manual task entry
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

    # S2: order by deadline; urgency computed server-side via Task.is_urgent()
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.deadline.asc()).all()

    # optional filter (all/pending/done) for demo/testing
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
        return redirect(url_for("main.landing"))

    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Not allowed.")
        return redirect(url_for("main.dashboard"))

    # S3: completion tracking
    task.mark_done()
    db.session.commit()
    flash("Task marked as done.")
    return redirect(url_for("main.dashboard"))


@bp.route("/toggle_task/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("main.landing"))

    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Not allowed.")
        return redirect(url_for("main.dashboard"))

    if task.status == "Done":
        task.status = "Pending"
        flash("Task marked as pending.")
    else:
        task.mark_done()
        flash("Task marked as done.")

    db.session.commit()
    return redirect(url_for("main.dashboard"))

@bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("main.landing"))

    task = Task.query.get_or_404(task_id)
    if task.user_id != user.id:
        flash("Not allowed.")
        return redirect(url_for("main.dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.")
    return redirect(url_for("main.dashboard"))
