

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
            return self.context["RTE"]
        elif use_case == "SNCF":
            pass
        elif use_case == "ORANGE":
            pass
        elif use_case == "DA/FW":
            pass
         

    def get_context(self):
        context_list = []
        for _, value in self.context.items():
            if value is not None:
                context_list.append(value)
        return context_list
