from api.context_manager.base_context_manager import BaseContextManager


class PowerGridContextManager(BaseContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "PowerGrid"
