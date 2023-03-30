from .recommendation_manager.base_recommendation import BaseRecommendation


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
