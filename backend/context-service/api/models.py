from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ContextModel(db.Model):
    id_context = db.Column(db.String, primary_key=True)
    use_case = db.Column(db.String(10))
    date = db.Column(db.DateTime)
    data = db.Column(db.PickleType)
