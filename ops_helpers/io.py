import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pandas as pd


# [START validate event/input]
def validate_event(event: object, schema_path: str) -> None:
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
    try:
        validate(event, schema)
    except ValidationError:
        raise ValidationError(
            'Check event input against function documentation')
# [END validate event/input]


# [START sanitize output]
def sanitize_output(result) -> None:
    for key, value in result.items():
        if isinstance(value, pd.DataFrame):
            result[key] = value.to_json()
# [END sanitize output]
