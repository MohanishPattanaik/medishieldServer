from db import db
from sqlalchemy.orm import validates


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fingerID = db.Column(db.Integer, nullable=True, unique=True)
    reg_no = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)

    def __init__(self, reg_no, password, username):
        self.reg_no = reg_no
        self.password = password
        self.username = username

    @validates("fingerID")
    def validate_fingerID(self, key, fingerID):
        if fingerID is not None and (fingerID < 1 or fingerID > 127):
            print(fingerID)
            raise ValueError("fingerID must be in the range 1-127")
        return fingerID
