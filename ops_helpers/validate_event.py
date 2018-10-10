import json
from os import path, getcwd
from jsonschema import validate
from jsonschema.exceptions import ValidationError

WORKDIR = getcwd()


# [START event validation]
# NB: Tightly coupled to layout of Operations-FAAS directory
def validate_event(event, schema: str) -> None:
    "Compare event input to object required by schema"
    SCHEMA = path.abspath(
        path.join(
            path.dirname(WORKDIR),
            f'../functions/schemas//{schema}'   
        )
    )

    with open(SCHEMA) as schema_file:
        schema = json.load(schema_file)
    try:
        validate(event, schema)
    except ValidationError:
        raise ValidationError(
            'Check event input against function documentation')
# [END event validation]
