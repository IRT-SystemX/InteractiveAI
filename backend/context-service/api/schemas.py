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
    data = Dict()

    @validates_schema
    def validate_metadata(self, validate_data, **kwargs):
        use_case = validate_data.get("use_case")
        data = validate_data.get("data")
        if use_case == "RTE":
            ContextMetadataRTE().load(data)
        elif use_case == "SNCF":
            # ContextMetadataSNCF().load(data)
            pass
        elif use_case == "ORANGE":
            # ContextMetadataOrange().load(data)
            pass
        elif use_case == "DA/FW":
            # ContextMetadataDAFW().load(data)
            pass
        else:
            raise ValidationError("Invalid use case")


class ContextOut(Schema):
    id_context = String()
    use_case = String()
    date = DateTime(format="iso")
    data = Dict()
