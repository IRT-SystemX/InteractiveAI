from apiflask import Schema
from apiflask.fields import Dict, List, String


class RecommendationAsk(Schema):
    context = Dict()
    event = Dict()


class RecommendationOut(Schema):
    title = String()
    description = String()
    use_case = String()
    description = String()
    agent_type = String()
    actions = List(Dict())
