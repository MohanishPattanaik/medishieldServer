import os

from db import db
from flask import Flask, jsonify, make_response, redirect, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from model.log import Log
from model.user import User


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["SECRET_KEY"] = os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "database.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        reg_no = data.get("reg_no")
        password = data.get("password")
        user = User.query.filter_by(reg_no=reg_no).first()
        print(reg_no, password, user)
        if user is None:
            return jsonify(
                {
                    "message": "User not found",
                    "status": 404,
                }
            )
        if user.password != password:
            return jsonify(
                {
                    "message": "Invalid password",
                    "status": 401,
                }
            )
        session["user_id"] = user.id
        return jsonify(
            {
                "message": "Login successful",
                "status": 200,
            }
        )

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        reg_no = data.get("reg_no")
        password = data.get("password")
        username = data.get("username")
        print(reg_no, password, username)
        if User.query.filter_by(reg_no=reg_no).first() is not None:
            return jsonify(
                {
                    "message": "User already exists",
                    "status": 409,
                }
            )
        if User.query.filter_by(username=username).first() is not None:
            return jsonify(
                {
                    "message": "Username already exists",
                    "status": 409,
                }
            )
        user = User(reg_no, password, username)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"})

    @app.route("/auth", methods=["POST"])
    def auth():
        return "Auth Page"

    @app.route("/logs", methods=["GET"])
    def logs():
        return jsonify([log for log in Log.query.all()])

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
