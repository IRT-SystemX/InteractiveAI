import importlib

from apiflask import Schema
from apiflask.fields import DateTime, Dict, Integer, String
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema

from .models import UseCaseModel


class MetadataSchema(Schema):
    pass


class ContextIn(Schema):
    use_case = String(
        required=True, validate=OneOf(["RTE", "SNCF", "DA", "ORANGE"])
    )
    date = DateTime(format="iso")
    data = Dict()

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


class ContextOut(Schema):
    id_context = String()
    use_case = String()
    date = DateTime(format="iso")
    data = Dict()


class UseCaseIn(Schema):
    name = String(required=True, validate=Length(1, 255))
    context_manager_class = String(validate=Length(1, 255))
    metadata_schema_class = String(validate=Length(1, 255))


class UseCaseOut(Schema):
    id = Integer()
    name = String(required=True, validate=Length(1, 255))
    context_manager_class = String(validate=Length(1, 255))
    metadata_schema_class = String(validate=Length(1, 255))
