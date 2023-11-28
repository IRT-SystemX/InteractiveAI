from apiflask import Schema
from apiflask.fields import Dict, List, String, Integer


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


class ProcedureOut(Schema):
    procedure = List(Dict())
    max_speed = Integer()
    min_speed = Integer()
