from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class EventModel(db.Model):
    id_event = db.Column(db.String, primary_key=True)
    use_case = db.Column(db.String(10))
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime)
    criticality = db.Column(db.String(10))
    data = db.Column(db.PickleType)
