import importlib

from api.exceptions import InvalidUseCase
from api.models import UseCaseModel
from settings import logger

from .event_manager.base_event_manager import BaseEventManager


class UseCaseFactory:
    def __init__(self):
        self._use_cases = {}

    def register_use_case(self, name, use_case):
        self._use_cases[name] = use_case

    def get_event_manager(self, name) -> BaseEventManager:
        use_case = self._use_cases.get(name)
        if use_case is None:
            raise InvalidUseCase
        return use_case


def load_usecases_db(use_case_factory):
    use_cases = UseCaseModel.query.all()
    logger.info(use_cases)

    for use_case in use_cases:
        name = use_case.name
        # Dynamically import the event manager class
        event_manager_module = importlib.import_module(
            f"resources.{use_case.name}.event_manager"
        )
        event_manager_class = getattr(
            event_manager_module, f"{use_case.event_manager_class}"
        )

        event_manager_instance = event_manager_class()

        use_case_factory.register_use_case(name, event_manager_instance)
