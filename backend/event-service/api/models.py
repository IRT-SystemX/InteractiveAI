from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class EventModel(db.Model):
    id_event = db.Column(db.String, primary_key=True)
    of_uid = db.Column(db.String())
    use_case = db.Column(db.String(10))
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    criticality = db.Column(db.String(10))
    data = db.Column(db.PickleType)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id_event': self.id_event,
            'of_uid': self.of_uid,
            'use_case': self.use_case,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'criticality': self.criticality,
            'data': self.data,
            'is_active': self.is_active
        }
