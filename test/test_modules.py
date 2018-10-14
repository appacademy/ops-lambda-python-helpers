from os import getcwd, path
import sys
from copy import deepcopy
import json
import pytest
from ops_helpers import (
    concat_path, add_path,
    validate_event, sanitize_output,
    retry_after_class_action, APIError)
from jsonschema.exceptions import ValidationError
import pandas as pd

# [[START change_path tests]]
__THISDIR__ = path.abspath(path.join(getcwd(), 'test'))
__FUNCDIR__ = path.abspath(path.join(__THISDIR__, '../ops_helpers'))
__MISSINGDIR__ = path.abspath(path.join(__THISDIR__, '../missing'))


# [START concat_path test]
def test_concat_path():
    __PATH__ = concat_path(__file__, '..')
    assert __PATH__ == f'{__THISDIR__}/..'
# [END concat_path test]


# [START add_path tests]
class TestAddPath():
    def test_fail_pre_add_path(self):
        assert __FUNCDIR__ not in sys.path

    def test_succeed_post_add_path(self):
        add_path(__file__, '../ops_helpers')
        assert __FUNCDIR__ in sys.path

    def test_missing_path(self):
        assert __MISSINGDIR__ not in sys.path
# [END add_path tests]

# [[END change_path tests]]


# [START validate_event tests]
EVENT = {'body': "test"}
__SCHEMA__ = path.abspath(
    path.join(path.dirname(__file__), 'mock_schema.json')
)


class TestValidateEvent():
    def test_success(self):
        validate_event(EVENT, __SCHEMA__)

    def test_fail_wrong_type(self):
        with pytest.raises(ValidationError):
            validate_event('string_not_dict', __SCHEMA__)

    def test_fail_missing_parameter(self):
        with pytest.raises(ValidationError):
            validate_event({'not_body': "test"}, __SCHEMA__)

    def test_fail_no_schema(self):
        with pytest.raises(FileNotFoundError):
            validate_event('string_not_dict', '')
# [END validate_event tests]


# [START sanitize_output tests]
class TestSanitizeOutput():
    def test_success(self):
        result = {'body': pd.DataFrame([1, 2, 3])}
        sanitize_output(result)
        json.loads(result['body'])

    def test_fails(self):
        with pytest.raises(TypeError):
            result = {'body': pd.DataFrame([1, 2, 3])}
            json.loads(result['body'])

    def test_no_change(self):
        result = {'body': 'not pd'}
        result_copy = deepcopy(result)
        sanitize_output(result)
        result = result_copy
# [END sanitize_output tests]


# [[START retry tests]]

# [START simple retry tests]
class RetrySample():
    token = 'Invalid'

    @retry_after_class_action(
        max_tries=2, error_type=ValueError, corrective_method='reset_token')
    def return_eventually(self, val):
        if self.token != 'Valid':
            raise ValueError
        return val

    def reset_token(self):
        self.token = 'Valid'

    @retry_after_class_action(
        max_tries=1, error_type=ValueError, corrective_method='reset_token',)
    def return_solo_run(self, val):
        if self.token != 'Valid':
            raise ValueError
        return val

    @retry_after_class_action(
        max_tries=2, error_type=ValueError, corrective_method='reset_token_no_action',)
    def return_no_correction(self, val):
        if self.token != 'Valid':
            raise ValueError
        return val

    @retry_after_class_action(
        max_tries=2, error_type=ValueError, corrective_method='reset_token',)
    def return_unanticipated_error_type(self, val):
        if self.token != 'Valid':
            raise TypeError
        return val

    def reset_token_no_action(self):
        pass
# [END simple retry tests]


# [START nested retry tests]
class TokenManager():
    def __init__(self):
        self.value = 'Invalid'

    def reset_token(self):
        self.value = 'Valid'

    def reset_token_no_action(self):
        pass


class RetrySampleNested():
    def __init__(self):
        self.token = TokenManager()

    @retry_after_class_action(
        max_tries=2, error_type=ValueError, corrective_method='token.reset_token')
    def return_eventually(self, val):
        if self.token.value != 'Valid':
            raise ValueError
        return val

    @retry_after_class_action(
        max_tries=2, error_type=ValueError, corrective_method='reset_token_no_action')
    def return_wrong_method_reference(self, val):
        if self.token.value != 'Valid':
            raise ValueError
        return val


class TestRetry():
    def test_succeed_after_correction(self):
        sample = RetrySample()
        assert sample.return_eventually('Hello') == 'Hello'

    def test_fail_solo_run(self):
        with pytest.raises(APIError):
            sample = RetrySample()
            sample.return_solo_run('Hello')

    def test_fail_no_correction(self):
        with pytest.raises(APIError):
            sample = RetrySample()
            sample.return_no_correction('Hello')

    def test_fail_unanticipated_error_type(self):
        with pytest.raises(TypeError):
            sample = RetrySample()
            sample.return_unanticipated_error_type('Hello')

    def test_succeed_nested(self):
        sample = RetrySampleNested()
        assert sample.return_eventually('Hello') == 'Hello'

    def test_fail_nested_wrong_attribute(self):
        with pytest.raises(AttributeError):
            sample = RetrySampleNested()
            sample.return_wrong_method_reference('Hello')
# [END nested retry tests]

# [[END retry tests]]
