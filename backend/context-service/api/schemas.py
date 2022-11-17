from apiflask import Schema
from apiflask.fields import DateTime, Dict, Integer, String
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema


class ContextMetadata(Schema):
    pass


class ContextMetadataRTE(ContextMetadata):
    topology = String(allow_none=False)
    observation = Dict(allow_none=False)


class ContextMetadataSNCF(ContextMetadata):
    pass


class ContextMetadataOrange(ContextMetadata):
    pass


class ContextMetadataDAFW(ContextMetadata):
    pass


class ContextIn(Schema):
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA/FW', 'ORANGE']))
    date = DateTime(format="iso")
    metadata = Dict()

    @validates_schema
    def validate_metadata(self, data, **kwargs):
        use_case = data.get("use_case")
        metadata = data.get("metadata")
        if use_case == "RTE":
            ContextMetadataRTE().load(metadata)
        elif use_case == "SNCF":
            ContextMetadataSNCF().load(metadata)
        elif use_case == "ORANGE":
            ContextMetadataOrange().load(metadata)
        elif use_case == "DA/FW":
            ContextMetadataDAFW().load(metadata)
        else:
            raise ValidationError("Invalid use case")


class ContextOut(Schema):
    use_case = String()
    date = DateTime(format="iso")
    metadata = Dict()
