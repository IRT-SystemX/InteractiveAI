from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FeedbackModel(db.Model):
    id_feedback = db.Column(db.String, primary_key=True)
    event_id = db.Column(db.String(255))
    context_id = db.Column(db.String(255))
    recommandation = db.Column(db.JSON)
    feedback = db.Column(db.Boolean)
    feedback_date = db.Column(db.DateTime)
    use_case = db.Column(db.String(10))
