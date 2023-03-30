from apiflask import Schema
from apiflask.fields import DateTime, String, Dict


class RecommendationAsk(Schema):
    context = Dict()
    event = Dict()


class BaseRecommendation(Schema):
    id_recommendation = String()
    timestamp_start = DateTime(format="iso")
    timestamp_end = DateTime(format="iso")
    data = Dict()
