from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ContextModel(db.Model):
    id_context = db.Column(db.String, primary_key=True)
    use_case = db.Column(db.String(10))
    date = db.Column(db.DateTime)
    data = db.Column(db.PickleType)


class UseCaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    context_manager_class = db.Column(db.String(255), nullable=False)
    metadata_schema_class = db.Column(db.String(255), nullable=False)
