from .base_context_manager import BaseContextManager
from .correlation_client_manager import CorrelationClientManager


class OrangeContextManager(BaseContextManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "Orange"
        self.correaltion_manager = CorrelationClientManager()

    def extra_operations(self):
        applications = self.context["data"]["applications"]
        self.correaltion_manager.add_correlation(applications)
