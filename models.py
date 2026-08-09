from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AccessRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_stale = db.Column(db.Boolean, default=False)
    risk_flag = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<AccessRecord {self.username} ({self.department})>"
