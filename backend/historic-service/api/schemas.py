from apiflask import Schema
from apiflask.fields import DateTime, Dict, String
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema

class Event(Schema):
    id_event = String()
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA/FW', 'ORANGE']))
    title = String(required=True, validate=Length(1, 255))
    description = String(required=True, validate=Length(1, 255))
    date = DateTime(format="iso")
    criticality = String(required=True, validate=OneOf(
        ['ND', 'HIGH', 'MEDIUM', 'LOW', 'ROUTINE']))
    metadata = Dict()

class Solution(Schema):
    pass

class Actions(Schema):
    pass

class AskForHelp(Schema):
    id_event = String()


class TraceIn(Schema):
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA/FW', 'ORANGE']))
    step = String(required=True, validate=OneOf(
        ['EVENT', 'ASKFORHELP', 'SOLUTION', 'AWARD']))
    date = DateTime(format="iso")
    data = Dict()

    @validates_schema
    def validate_data(self, validate_data, **kwargs):
        step = validate_data.get("step")
        trace_data = validate_data.get("data")
        if step == "EVENT":
            Event().load(trace_data)
        elif step == "ASKFORHELP":
            AskForHelp().load(trace_data)
        elif step == "SOLUTION":
            Actions().load(trace_data)
        elif step == "AWARD":
            Solution().load(trace_data)
        else:
            raise ValidationError("Invalid use case")


class TraceOut(Schema):
    id_trace = String()
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA/FW', 'ORANGE']))
    step = String(required=True, validate=OneOf(
        ['EVENT', 'ASKFORHELP', 'SOLUTION', 'AWARD']))
    date = DateTime(format="iso")
    data = Dict()
