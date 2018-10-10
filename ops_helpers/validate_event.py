import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError


# [START event validation]
def validate_event(event, schema: str) -> None:
    "Compare event input to object required by schema"
    with open(schema) as schema_file:
        schema = json.load(schema_file)
    try:
        validate(event, schema)
    except ValidationError:
        raise ValidationError(
            'Check event input against function documentation')
# [END event validation]
