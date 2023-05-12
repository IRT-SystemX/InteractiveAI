from .context_manager.base_context_manager import BaseContextManager


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
