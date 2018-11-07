import os
import json
import base64
from typing import Dict
import boto3
import requests
from botocore.exceptions import ClientError
from botocore.exceptions import NoRegionError


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
    """"Get secrets from AWS Secrets Manager
    Only works if AWS credentials are active env variables"""
    if secret_name is None:
        return None

    try:
        get_secret_value_response = get_secret_file(secret_name, region_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e(
                "Can't decrypt the protected secret text with provided KMS key.")
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e('An error occurred on the server side.')
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e('You provided an invalid value for a parameter.')
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e(
                'You provided an invalid parameter value for state of the resource.')
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e('Resource cannot be found')
    else:
        # Decrypts secret using the associated KMS CMK, if applicable.
        # Inserts all secerts as environment variables
        if 'SecretString' in get_secret_value_response:
            secrets = json.loads(get_secret_value_response['SecretString'])
            for key, value in secrets.items():
                os.environ[key] = value
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            for key, value in decoded_binary_secret.items():
                os.environ[key] = value


def invoke_lambda(
    department: str, service: str, stage: str, function: str, body: dict
):
    "Invoke an internal a/A Lambda function"
    function_stub = f'{department}-{service}-{stage}-{function}'
    try:
        client = boto3.client('lambda')
        r = client.invoke(
            FunctionName=function_stub,
            Payload=json.dumps(body),
            InvocationType='RequestResponse')
        result = json.loads(r['Payload'].read())
        return result
    except KeyError:
        raise KeyError('Function was not invoked correctly')
    # Exception handler for developers to execute locally without Boto3
    except NoRegionError:
        url = f'https://api.appacademy.io/internal/v1/rest/{function_stub}'
        token = os.environ['backup_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        data = json.dumps(body)
        result = (
            requests.post(url, data=data, headers=headers)
            .json()
        )
        return result
