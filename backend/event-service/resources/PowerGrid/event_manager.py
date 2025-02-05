from api.event_manager.base_event_manager import BaseEventManager


class PowerGridEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "PowerGrid"
        self.use_case_process = "cabProcess"

    def get_unique_fields(self, data):
        input_line = data["data"].get("line")
        return {"line": input_line}
