from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TraceModel(db.Model):
    id_trace = db.Column(db.String, primary_key=True)
    use_case = db.Column(db.String(10))
    step = db.Column(db.String(10))
    date = db.Column(db.DateTime)
    data = db.Column(db.PickleType)
