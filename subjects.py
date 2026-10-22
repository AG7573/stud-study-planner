from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask import Blueprint
from auth import login_required
from models import Subject
from extensions import db
from datetime import datetime

subjects = Blueprint('subjects', __name__, url_prefix='/subjects')

@subjects.route("/", methods=["GET"])
@login_required
def list_subjects():
    subject_listed = Subject.query.filter_by(user_id=session["user_id"]).all()
    return render_template("list_subjects.html", subjects=subject_listed)

@subjects.route("/subject", methods=["POST", "GET"])
@login_required
def add_subject():
    if request.method == "POST":
        name = request.form.get("name")
        exam_date = request.form.get("exam_date")

        if not name.strip():
            flash("Name cannot be empty.")
            return redirect(url_for("subjects.add_subject"))

        try:
            exam_date_parsed = datetime.strptime(exam_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid exam date, please try again.")
            return redirect(url_for("subjects.add_subject"))

        subject = Subject(
            name=name, 
            exam_date=datetime.strptime(exam_date, "%Y-%m-%d").date(),
            user_id=session["user_id"]
        )
        db.session.add(subject)
        db.session.commit()

        return redirect(url_for("subjects.list_subjects"))

    if request.method == "GET":
        return render_template("add_subject.html")

@subjects.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    if subject == None:
        flash("Error! Try again")
        return redirect(url_for("subjects.list_subjects"))
    if subject.user_id != session["user_id"]:
        flash("Doesn't exist!")
        return redirect(url_for("subjects.list_subjects"))
    
    if request.method == "GET":
        return render_template("edit_subject.html", subject=subject)
    
    if request.method == "POST":
        name = request.form.get("name")
        exam_date = request.form.get("exam_date")

        if not name.strip():
            flash("Name cannot be empty.")
            return redirect(url_for("subjects.edit_subject", subject_id=subject_id))

        try:
            exam_date_parsed = datetime.strptime(exam_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid exam date, please try again.")
            return redirect(url_for("subjects.edit_subject", subject_id=subject_id))

        subject.name = name
        subject.exam_date_parsed = datetime.strptime(exam_date, "%Y-%m-%d").date()

        db.session.commit()

        return redirect(url_for("subjects.list_subjects"))

@subjects.route("/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    if subject is None:
        return jsonify({
            "delete": False,
            "message": "Subject not found"
        }), 404
    if subject.user_id != session["user_id"]:
        return jsonify({
            "delete": False,
            "message": "You cannot delete this subject"
        }), 403

    db.session.delete(subject)
    db.session.commit()

    return jsonify({
        "delete": True
    })