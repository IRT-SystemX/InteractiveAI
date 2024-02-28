from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

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
    parent_event_id = db.Column(
        db.String,
        db.ForeignKey("event_model.id_event"),
        nullable=True,
        default=None,
    )
    parent_event = relationship("EventModel", remote_side=[id_event])

    def to_dict(self):
        return {
            "id_event": self.id_event,
            "of_uid": self.of_uid,
            "use_case": self.use_case,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "criticality": self.criticality,
            "data": self.data,
            "is_active": self.is_active,
            "parent_event_id": self.parent_event_id,
        }


class UseCaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    event_manager_class = db.Column(db.String(255), nullable=False)
    metadata_schema_class = db.Column(db.String(255), nullable=False)
