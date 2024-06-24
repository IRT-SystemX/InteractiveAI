from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UseCaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    manager_class = db.Column(db.String(255), nullable=False)
