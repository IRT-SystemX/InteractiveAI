from .base_context_manager import BaseContextManager


class RTEContextManager(BaseContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
