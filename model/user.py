from db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)

    def __init__(self, reg_no, password, username):
        self.reg_no = reg_no
        self.password = password
        self.username = username
