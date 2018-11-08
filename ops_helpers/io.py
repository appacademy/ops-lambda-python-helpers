import json
from typing import Dict
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pandas as pd


# [START validate event/input]
def validate_event(event: object, schema_path: str) -> None:
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
    try:
        validate(event, schema)
    except ValidationError as e:
        raise ValidationError(
            f'Check event against schema: {e}')
# [END validate event/input]


# [START get_kwargs]
def get_kwargs(event: Dict) -> Dict:
    "Assumes event has a body, or else ignores"
    if not isinstance(event, dict):
        raise TypeError('event must be a dictionary')
    if 'body' not in event or isinstance(event['body'], str):
        kwargs = event
    elif isinstance(event['body'], dict):
        kwargs = event['body']
    return kwargs
# [END get_kwargs]


# [START sanitize output]
def sanitize_output(result) -> None:
    for key, value in result.items():
        if isinstance(value, pd.Series):
            result[key] = value.to_frame().to_json()
        if isinstance(value, pd.DataFrame):
            result[key] = value.to_json()
# [END sanitize output]
