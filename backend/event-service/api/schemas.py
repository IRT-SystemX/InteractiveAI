from apiflask import Schema
from apiflask.fields import DateTime, Dict, Float, Integer, String, Boolean
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema


class Metadata(Schema):
    pass


class MetadataRTE(Metadata):
    event_type = String(required=True, validate=OneOf(
        ['KPI', 'anticipation', 'agent', 'consignation']))
    zone = String(validate=OneOf(['Est', 'Ouest', 'Centre']))
    line = String()
    flux = Float()


class MetadataSNCF(Metadata):
    pass


class MetadataOrange(Metadata):
    pass


class MetadataDAFW(Metadata):
    pass


class EventIn(Schema):
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA/FW', 'ORANGE']))
    title = String(required=True, validate=Length(1, 255))
    description = String(required=True, validate=Length(1, 255))
    date = DateTime(format="iso")
    criticality = String(required=True, validate=OneOf(
        ['ND', 'HIGH', 'MEDIUM', 'LOW', 'ROUTINE']))
    data = Dict()
    is_active = Boolean()

    @validates_schema
    def validate_metadata(self, data, **kwargs):
        use_case = data.get("use_case")
        metadata = data.get("data")
        if use_case == "RTE":
            MetadataRTE().load(metadata)
        elif use_case == "SNCF":
            # MetadataSNCF().load(metadata)
            pass
        elif use_case == "ORANGE":
            # MetadataOrange().load(metadata)
            pass
        elif use_case == "DA/FW":
            # MetadataDAFW().load(metadata)
            pass
        else:
            raise ValidationError("Invalid use case")


class EventOut(Schema):
    id = Integer()
    id_event = String()
    use_case = String()
    description = String()
    date = DateTime(format="iso")
    criticality = String()
    data = Dict()
    is_active = Boolean()
