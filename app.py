import datetime
import os

from arduino import Arduino
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

    # change the port to the port of the arduino
    arduino = Arduino("COM10", 9600)

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

        # Manually manage the auto-increment logic
        if User.query.count() == 0:
            next_id = 1
        else:
            last_user = User.query.order_by(User.fingerID.desc()).first()
            next_id = (
                (last_user.fingerID + 1)
                if last_user and last_user.fingerID < 127
                else 1
            )

        user = User(reg_no=reg_no, password=password, username=username)
        user.fingerID = next_id

        # tell arduino to create a new user
        arduino.write("1")
        # wait for the arduino to ask for the user id
        arduino.wait_for(["enter finger print id from 1 to 127"])
        # send the user id to the arduino
        arduino.write(str(user.fingerID))
        # wait for the prints to match
        arduino.wait_for(["stored!"])

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully"})

    @app.route("/auth", methods=["POST"])
    def auth():
        arduino.write("3")
        arduino.wait_for(["Found a print match!"])
        FingerID = arduino.wait_for(["Found ID #"])
        FingerID = FingerID.split("#")[1].strip()
        user = User.query.filter_by(fingerID=FingerID).first()
        if user is None:
            return jsonify(
                {
                    "message": "User not found",
                    "status": 404,
                }
            )
        tool = request.get_json().get("tool")
        log = Log(
            username=user.username,
            reg_no=user.reg_no,
            tool=tool,
            timestamp=datetime.datetime.now(),
        )
        db.session.add(log)
        db.session.commit()
        return jsonify(
            {
                "message": "User authenticated successfully",
                "status": 200,
            }
        )

    @app.route("/logs", methods=["GET"])
    def logs():
        logs = Log.query.all()
        logs_list = [log.to_dict() for log in logs]
        return jsonify(logs_list)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
