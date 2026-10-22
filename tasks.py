from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from extensions import db
from models import Task, Subject
from auth import login_required
from datetime import datetime

tasks = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks.route("/subjects/<int:subject_id>", methods=["GET"])
@login_required
def list_tasks(subject_id):

    subject = Subject.query.filter_by(id=subject_id).first()

    if subject is None:
        flash("Invalid Input, enter a subject.")
        return redirect(url_for("subjects.list_subjects"))
    if subject.user_id != session["user_id"]:
        flash("Subject doesn't exist.")
        return redirect(url_for("subjects.list_subjects"))
    
    task_listed = Task.query.filter_by(subject_id=subject_id).all()
    return render_template("tasks_list.html", tasks=task_listed, subject=subject)

@tasks.route("/subjects/<int:subject_id>/add", methods=["POST", "GET"])
@login_required
def add_tasks(subject_id):

    subject = Subject.query.filter_by(id=subject_id).first()

    if subject is None:
        flash("Invalid Input, enter a subject.")
        return redirect(url_for("subjects.list_subjects"))
    if subject.user_id != session["user_id"]:
        flash("Subject doesn't exist.")
        return redirect(url_for("subjects.list_subjects"))
    
    if request.method == "POST":
        title = request.form.get("title")
        estimated_hours = request.form.get("estimated_hours")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")
        status = request.form.get("status")

        if not title.strip():
            flash("Title cannot be empty.")
            return redirect(url_for("tasks.add_tasks", subject_id=subject_id))

        try:
            due_date_parsed = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid due date, please enter again.")
            return redirect(url_for("tasks.add_tasks", subject_id=subject_id))

        try:
            estimated_hours_parsed = float(estimated_hours)
        except ValueError:
            flash("Invalid estimated hours, please try again.")
            return redirect(url_for("tasks.add_tasks", subject_id=subject_id))

        if estimated_hours_parsed <= 0:
            flash("Estimated hours can't be negative or 0.")
            return redirect(url_for("tasks.add_tasks", subject_id=subject_id))
        
        task = Task(
            title=title,
            estimated_hours=float(estimated_hours),
            priority=priority,
            due_date=datetime.strptime(due_date, "%Y-%m-%d").date(),
            status=status,
            subject_id=subject_id
        )

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("tasks.list_tasks", subject_id=subject_id))

    if request.method == "GET":
        return render_template("add_task.html", subject=subject)

@tasks.route("/tasks/<int:task_id>/edit", methods=["POST", "GET"])
@login_required
def edit_tasks(task_id):

    task = Task.query.filter_by(id=task_id).first()

    if task is None:
        flash("Invalid")
        return redirect(url_for("subjects.list_subjects"))
    if task.subject.user_id != session["user_id"]:
        flash("Task doesn't exist.")
        return redirect(url_for("subjects.list_subjects"))

    if request.method == "GET":
        return render_template("edit_task.html", task=task)

    if request.method == "POST":
        title = request.form.get("title")
        estimated_hours = request.form.get("estimated_hours")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")
        status = request.form.get("status")

        if not title.strip():
            flash("Title cannot be empty.")
            return redirect(url_for("tasks.edit_tasks", task_id=task_id))

        try:
            due_date_parsed = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid due date, please enter again.")
            return redirect(url_for("tasks.edit_tasks", task_id=task_id))

        try:
            estimated_hours_parsed = float(estimated_hours)
        except ValueError:
            flash("Estimated hours must be a number.")
            return redirect(url_for("tasks.edit_tasks", task_id=task_id))

        if estimated_hours_parsed <= 0:
            flash("Estimated hours can't be negative or 0.")
            return redirect(url_for("tasks.edit_tasks", task_id=task_id))

        task.title = title
        task.estimated_hours_parsed = float(estimated_hours)
        task.priority = priority
        task.due_date_parsed = datetime.strptime(due_date, "%Y-%m-%d").date()
        task.status = status

        db.session.commit()

        return redirect(url_for("tasks.list_tasks", subject_id=task.subject_id))

@tasks.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_tasks(task_id):

    task = Task.query.filter_by(id=task_id).first()

    if task is None:
        return jsonify({
            "delete": False,
            "message": "Task is invalid"
        }), 403
    if task.subject.user_id != session["user_id"]:
        return jsonify({
            "delete": False,
            "message": "You cannot delete this task"
        }), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "delete": True
    }), 200