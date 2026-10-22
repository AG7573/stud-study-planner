from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    hours_per_day = db.Column(db.Integer, nullable=False, default=2)

    subjects = db.relationship("Subject", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<email: {self.email}>"

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)

    tasks = db.relationship("Task", backref="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<name: {self.name}>"
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    title = db.Column(db.String(100), nullable=False)
    estimated_hours = db.Column(db.Float, default=2, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False)

    studysessions = db.relationship("StudySession", backref="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<title: {self.title}>"

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    scheduled_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<scheduled date: {self.scheduled_date}>"