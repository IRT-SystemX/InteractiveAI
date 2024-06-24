import importlib

from api.exceptions import InvalidUseCase
from api.models import UseCaseModel
from settings import logger

from .manager.base_manager import BaseRecommendationManager


class UseCaseFactory:
    def __init__(self):
        self._use_cases = {}

    def register_use_case(self, name, use_case):
        self._use_cases[name] = use_case

    def get_recommendation_manager(self, name) -> BaseRecommendationManager:
        use_case = self._use_cases.get(name)
        if use_case is None:
            raise InvalidUseCase
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
        manager_module = importlib.import_module(
            f"resources.{use_case.name}.manager"
        )
        manager_class = getattr(manager_module, f"{use_case.manager_class}")

        manager_instance = manager_class()

        use_case_factory.register_use_case(name, manager_instance)
