import importlib

from api.models import UseCaseModel
from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Dict, Integer, String
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema


class MetadataSchema(Schema):
    pass


class EventIn(Schema):
    use_case = String(required=True, validate=Length(1, 255))
    title = String(required=True, validate=Length(1, 255))
    description = String(required=True, validate=Length(1, 255))
    start_date = DateTime(format="iso", allow_none=True)
    end_date = DateTime(format="iso", allow_none=True)
    criticality = String(
        required=True,
        validate=OneOf(["ND", "HIGH", "MEDIUM", "LOW", "ROUTINE"]),
    )
    data = Dict()
    is_active = Boolean()
    parent_event_id = String(allow_none=True)

    @validates_schema
    def validate_metadata(self, data, **kwargs):
        use_case = data.get("use_case")

        usecase_db_data = UseCaseModel.query.filter(
            UseCaseModel.name == use_case
        ).first()
        if usecase_db_data is None:
            raise ValidationError("Invalid use case")

        metadata = data.get("data")

        # Dynamically import the metadata schema class
        metadata_schema_module = importlib.import_module(
            f"resources.{usecase_db_data.name}.schemas"
        )
        metadata_schema_class = getattr(
            metadata_schema_module, f"{usecase_db_data.metadata_schema_class}"
        )
        metadata_schema_class().load(metadata)


class EventOut(Schema):
    id = Integer()
    id_event = String()
    of_uid = String()
    use_case = String()
    title = String()
    description = String()
    start_date = DateTime(format="iso", allow_none=True)
    end_date = DateTime(format="iso", allow_none=True)
    criticality = String()
    data = Dict()
    is_active = Boolean()
    parent_event_id = String(allow_none=True)


class UseCaseIn(Schema):
    name = String(required=True, validate=Length(1, 255))
    event_manager_class = String(validate=Length(1, 255))
    metadata_schema_class = String(validate=Length(1, 255))


class UseCaseOut(Schema):
    id = Integer()
    name = String(required=True, validate=Length(1, 255))
    event_manager_class = String(validate=Length(1, 255))
    metadata_schema_class = String(validate=Length(1, 255))
