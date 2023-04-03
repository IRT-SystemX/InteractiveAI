from apiflask import Schema
from apiflask.fields import DateTime, String, Dict


class RecommendationAsk(Schema):
    context = Dict()
    event = Dict()
