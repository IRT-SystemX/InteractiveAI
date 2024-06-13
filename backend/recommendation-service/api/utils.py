from .recommendation_manager.base_recommendation import BaseRecommendation
from settings import logger


class UseCaseFactory:
    def __init__(self):
        self._use_cases = {}

    def register_use_case(self, name, use_case):
        self._use_cases[name] = use_case

    def get_use_case(self, name) -> BaseRecommendation:
        use_case = self._use_cases.get(name)
        if use_case is None:
            raise ValueError(f"Unknown use case '{name}'")
        return use_case

    def unregister_all_use_cases(self):
        self._use_cases.clear()
        logger.info("All use cases have been unregistered.")
