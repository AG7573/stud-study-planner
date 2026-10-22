from flask import Flask, render_template, redirect, session, url_for
from config import Config
from extensions import db
from auth import auth
from subjects import subjects
from tasks import tasks
from schedule import schedule

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("subjects.list_subjects"))
        return redirect(url_for("auth.signup"))

    # blueprints will be registered
    app.register_blueprint(auth)
    app.register_blueprint(subjects)
    app.register_blueprint(tasks)
    app.register_blueprint(schedule)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)