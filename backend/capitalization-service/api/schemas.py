from apiflask import Schema
from apiflask.fields import DateTime, Dict, String, Boolean


class FeedbackIn(Schema):
    event_id = String(required=True)
    context_id = String()
    recommandation = Dict()
    feedback = Boolean()
    feedback_date = DateTime(format="iso")
    use_case = String(required=True)


class FeedbackOut(Schema):
    id_feedback = String()
    event_id = String()
    context_id = String()
    recommandation = Dict()
    feedback = Boolean()
    feedback_date = DateTime(format="iso")
    use_case = String()
