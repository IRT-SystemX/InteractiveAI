import uuid
from datetime import datetime

from ..models import ContextModel, db


class BaseContextManager:
    def __init__(self) -> None:
        self.context = None
        self.use_case = None

    def set_context(self, validated_data):
        validated_data["date"] = validated_data.get("date", datetime.now())
        self.context = validated_data

        self.extra_operations()

        # save context to db
        validated_data["id_context"] = str(uuid.uuid4())
        context = ContextModel(**validated_data)
        db.session.add(context)
        db.session.commit()
        return context

    def get_context(self):
        return self.context

    def get_contexts_with_date(self, date):
        context = ContextModel.query.filter_by(date=date).filter(
            ContextModel.use_case.in_(self.use_case)).all()
        return context

    def get_context_with_date(self, date):
        context = ContextModel.query.filter_by(date=date).filter(
            ContextModel.use_case.in_(self.use_case)).first()
        return context

    def extra_operations(self):
        pass
