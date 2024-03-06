from apiflask import Schema
from apiflask.fields import DateTime, Dict, String
from apiflask.validators import OneOf


class TraceIn(Schema):
    use_case = String(required=True)
    step = String(
        required=True,
        validate=OneOf(["EVENT", "ASKFORHELP", "SOLUTION", "AWARD"]),
    )
    date = DateTime(format="iso")
    data = Dict()


class TraceOut(Schema):
    id_trace = String()
    use_case = String(required=True)
    step = String(
        required=True,
        validate=OneOf(["EVENT", "ASKFORHELP", "SOLUTION", "AWARD"]),
    )
    date = DateTime(format="iso")
    data = Dict()
