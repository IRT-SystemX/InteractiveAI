import importlib

from settings import logger

from .context_manager.base_context_manager import BaseContextManager
from .models import UseCaseModel


class UseCaseFactory:
    def __init__(self):
        self._use_cases = {}

    def register_use_case(self, name, use_case):
        self._use_cases[name] = use_case

    def get_context_manager(self, name) -> BaseContextManager:
        use_case = self._use_cases.get(name)
        if use_case is None:
            raise ValueError(f"Unknown use case '{name}'")
        return use_case

    def unregister_all_use_cases(self):
        self._use_cases.clear()
        logger.info("All use cases have been unregistered.")


def load_usecases_db(use_case_factory):
    use_cases = UseCaseModel.query.all()
    logger.info(use_cases)

    for use_case in use_cases:
        name = use_case.name
        # Dynamically import the event manager class
        context_manager_module = importlib.import_module(
            f"resources.{use_case.name}.context_manager"
        )
        context_manager_class = getattr(
            context_manager_module, f"{use_case.context_manager_class}"
        )

        context_manager_instance = context_manager_class()

        use_case_factory.register_use_case(name, context_manager_instance)
