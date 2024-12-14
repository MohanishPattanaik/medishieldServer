from db import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    reg_no = db.Column(db.String(120), nullable=False)
    tool = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, reg_no, tool, timestamp):
        self.username = username
        self.reg_no = reg_no
        self.tool = tool
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "reg_no": self.reg_no,
            "tool": self.tool,
            "timestamp": self.timestamp.isoformat(),
        }
