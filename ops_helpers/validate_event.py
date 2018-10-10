import json
from os import path
from jsonschema import validate
from jsonschema.exceptions import ValidationError


# [START event validation]
def validate_event(event, schema_path: str) -> None:
    SCHEMA = path.join(path.dirname(__file__), schema_path)

    with open(SCHEMA) as schema_file:
        schema = json.load(schema_file)
    try:
        validate(event, schema)
    except ValidationError:
        raise ValidationError(
            'Check event input against function documentation')
# [END event validation]
