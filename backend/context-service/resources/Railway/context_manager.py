# backend/context-service/resources/Railway/context_manager.py

from api.context_manager.base_context_manager import BaseContextManager

class RailwayContextManager(BaseContextManager):
    def __init__(self):
        super().__init__()
        self.use_case = "Railway"