from os import getcwd, path
import sys
import pytest
from ops_helpers import concat_path, add_path, validate_event
from jsonschema.exceptions import ValidationError

__THISDIR__ = path.abspath(path.join(getcwd(), 'test'))
__FUNCDIR__ = path.abspath(path.join(__THISDIR__, '../ops_helpers'))
__MISSINGDIR__ = path.abspath(path.join(__THISDIR__, '../missing'))

__SCHEMA__ = path.abspath(
    path.join(path.dirname(__file__), 'mock_schema.json')
)
EVENT = {'body': "test"}


def test_concat_path():
    __PATH__ = concat_path(__file__, '..')
    assert __PATH__ == f'{__THISDIR__}/..'


class TestAddPath():
    def test_fail_pre_add_path(self):
        assert __FUNCDIR__ not in sys.path

    def test_succeed_post_add_path(self):
        add_path(__file__, '../ops_helpers')
        assert __FUNCDIR__ in sys.path

    def test_missing_path(self):
        assert __MISSINGDIR__ not in sys.path


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
