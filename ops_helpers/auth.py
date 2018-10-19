import os
import json
import base64
from typing import Dict
import boto3
from botocore.exceptions import ClientError


def get_secret_file(secret_name: str, region_name: str) -> Dict:
    secret_name = secret_name
    region_name = region_name

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name)

    return get_secret_value_response


def fetch_secrets(secret_name: str, region_name: str) -> None:
    "Get secrets from AWS Secrets Manager; only works if AWS credentials are active env variables"
    try:
        get_secret_value_response = get_secret_file(secret_name, region_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e(
                "Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e('An error occurred on the server side.')
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e('You provided an invalid value for a parameter.')
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e(
                'You provided a parameter value that is not valid for the current state of the resource.')
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e('Resource cannot be found')
    else:
        # Decrypts secret using the associated KMS CMK, if applicable.
        # Depending on whether secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secrets = json.loads(get_secret_value_response['SecretString'])
            for key, value in secrets.items():
                os.environ[key] = value
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            for key, value in decoded_binary_secret.items():
                os.environ[key] = value
