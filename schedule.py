from flask import Blueprint
from flask import Flask, render_template, redirect, session, url_for, request, flash, jsonify
from extensions import db
from auth import login_required
from models import Task, StudySession, Subject
from scheduler import sort_by_urgency, day_by_day_allocation
from llm_helper import get_schedule_summary

schedule = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule.route("/generate", methods=['POST'])
@login_required
def fetch_user_tasks():
    tasks = Task.query.join(Subject).filter(Subject.user_id == session["user_id"]).all()
    task_dictionary = []
    for task in tasks:
        task_dict = {
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date,
            "estimated_hours": task.estimated_hours,
            "id": task.id
        }
        task_dictionary.append(task_dict)

    sorted_task = sort_by_urgency(task_dictionary)
    generated_schedule, overcommitted = day_by_day_allocation(sorted_task)

    task_ids = [task.id for task in tasks]

    if task_ids:
        StudySession.query.filter(StudySession.task_id.in_(task_ids)).delete(synchronize_session=False)

    for entry in generated_schedule:
        session_obj = StudySession(
            task_id=entry["task_id"],
            scheduled_date=entry["todays_date"],
            duration=entry["allocated_amount"],
            completed=False
        )
        db.session.add(session_obj)
    db.session.commit()

    if overcommitted:
        flash(f"Could not schedule:{', '.join(entry["task_title"] for entry in overcommitted)}")

    return redirect(url_for("schedule.fetch_user_studysession_rows"))

@schedule.route("/view", methods=["GET"])
@login_required
def fetch_user_studysession_rows():
    study_sessions = StudySession.query.join(Task).join(Subject).filter(Subject.user_id == session["user_id"]).all()
    subjects = Subject.query.filter_by(user_id=session["user_id"]).all()
    schedule_by_day = {}
    for entry in study_sessions:
        if entry.scheduled_date not in schedule_by_day:
            schedule_by_day[entry.scheduled_date] = []
        schedule_by_day[entry.scheduled_date].append(entry)

    summary = None
    if study_sessions:
        summary = get_schedule_summary(study_sessions, subjects)

    return render_template("view_schedule.html", schedule_by_day=schedule_by_day)

@schedule.route("/session/<int:session_id>/complete", methods=["POST"])
@login_required
def session_completed(session_id):
    study_sessions = StudySession.query.filter_by(id=session_id).first()
    if study_sessions is None:
        flash("Doesn't exist.")
        return jsonify({
            "error": "Session not found"
        }), 404
    if study_sessions.task.subject.user_id != session["user_id"]:
        flash("Doesn't exist.")
        return jsonify({
            "error": "Session not found"
        }), 404
    study_sessions.completed = not study_sessions.completed
    db.session.commit()
    return jsonify({
        "completed": study_sessions.completed
    })