from apiflask import Schema
from apiflask.fields import Dict, Integer, List, String
from apiflask.validators import Length


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
    kpis = Dict(allow_none=True)


class ProcedureOut(Schema):
    procedure = List(Dict())
    max_speed = Integer()
    min_speed = Integer()


class UseCaseIn(Schema):
    name = String(required=True, validate=Length(1, 255))
    event_manager_class = String(validate=Length(1, 255))


class UseCaseOut(Schema):
    id = Integer()
    name = String(required=True, validate=Length(1, 255))
    event_manager_class = String(validate=Length(1, 255))
