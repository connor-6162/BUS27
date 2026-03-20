from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    # User entity for conceptual model (Portfolio 3.1)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # 1-to-many: User -> Task
    tasks = db.relationship("Task", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Task(db.Model):
    # Task entity: S1/S2/S3
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.DateTime(timezone=True), nullable=False)  # stored as UTC-aware
    status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending / Done

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def is_urgent(self) -> bool:
        """S2: due within 24 hours and not done."""
        if self.status == "Done":
            return False

        now_utc = datetime.now(timezone.utc)
        dl = self.deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)

        remaining = dl - now_utc
        return timedelta(seconds=0) < remaining <= timedelta(hours=24)

    def mark_done(self) -> None:
        """S3: mark task as done"""
        self.status = "Done"

    def __repr__(self):
        return f"<Task {self.name} {self.deadline} {self.status}>"
