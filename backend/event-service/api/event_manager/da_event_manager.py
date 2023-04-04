from .base_event_manager import BaseEventManager


class DAEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "DA"
        self.use_case_process = "daProcess"
