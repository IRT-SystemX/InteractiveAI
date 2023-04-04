from .base_event_manager import BaseEventManager


class OrangeEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
        self.use_case_process = "orangeProcess"
        
