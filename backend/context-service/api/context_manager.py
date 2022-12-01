import uuid

from .models import ContextModel, db


class ContextManager:
    def __init__(self) -> None:
        self.context = {"RTE": None,
                        "SNCF": None,
                        "ORANGE": None,
                        "DA/FW": None}

    def set_context(self, validated_data):
        use_case = validated_data.get("use_case")

        if use_case == "RTE":
            self.context["RTE"] = validated_data
            # return self.context["RTE"]
        elif use_case == "SNCF":
            pass
        elif use_case == "ORANGE":
            pass
        elif use_case == "DA/FW":
            pass
        # save context to db
        validated_data["id_context"] = str(uuid.uuid4())
        context = ContextModel(**validated_data)
        db.session.add(context)
        db.session.commit()
        return context

    def get_context(self):
        context_list = []
        for _, value in self.context.items():
            if value is not None:
                context_list.append(value)
        return context_list
