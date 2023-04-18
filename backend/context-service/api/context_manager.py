import uuid
from datetime import datetime

from cab_common_auth.decorators import get_use_cases

from .correlation_client_manager import CorrelationClientManager
from .models import ContextModel, db


class ContextManager:
    def __init__(self) -> None:
        self.context = {"RTE": None,
                        "SNCF": None,
                        "ORANGE": None,
                        "DA": None}

        self.correaltion_manager = CorrelationClientManager()

    def set_context(self, validated_data):
        validated_data["date"] = validated_data.get("date", datetime.now())
        use_case = validated_data.get("use_case")
        self.context[use_case] = validated_data

        self.extra_operations(use_case)

        # save context to db
        validated_data["id_context"] = str(uuid.uuid4())
        context = ContextModel(**validated_data)
        db.session.add(context)
        db.session.commit()
        return context

    def get_context(self):
        use_cases = get_use_cases()
        context_list = []
        for key, value in self.context.items():
            if value is not None and key in use_cases:
                context_list.append(value)
        return context_list

    def get_contexts_with_date(self, date):
        use_cases = get_use_cases()
        context = ContextModel.query.filter_by(date=date).filter(
            ContextModel.use_case.in_(use_cases)).all()
        return context

    def get_context_with_date(self, date):
        use_cases = get_use_cases()
        context = ContextModel.query.filter_by(date=date).filter(
            ContextModel.use_case.in_(use_cases)).first()
        return context

    def extra_operations(self, use_case):
        if use_case == "ORANGE":
            applications = self.context["ORANGE"]["data"]["applications"]
            self.correaltion_manager.add_correlation(applications)
