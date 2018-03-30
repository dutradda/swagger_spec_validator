# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from swagger_spec_validator3.common import SwaggerValidationError
from swagger_spec_validator3.validator20 import validate_apis


def test_api_level_params_ok():
    # Parameters defined at the API level apply to all operations within that
    # API. Make sure we don't treat the API level parameters as an operation
    # since they are peers.
    apis = {
        '/tags/{tag-name}': {
            'parameters': [
                {
                    'name': 'tag-name',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                },
            ],
            'get': {
            }
        }
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)


def test_api_level_x_hyphen_ok():
    # Elements starting with "x-" should be ignored
    apis = {
        '/tags/{tag-name}': {
            'x-ignore-me': 'DO NOT LOOK AT ME!',
            'get': {
                'parameters': [
                    {
                        'name': 'tag-name',
                        'in': 'path',
                        'type': 'string',
                    }
                ]
            }
        }
    }
    # Success == no exception thrown
    validate_apis(apis, lambda x: x)


@pytest.mark.parametrize(
    'partial_parameter_spec',
    [
        {'type': 'integer', 'default': 1},
        {'type': 'boolean', 'default': True},
        {'type': 'null', 'default': None},
        {'type': 'number', 'default': 2},
        {'type': 'number', 'default': 3.4},
        {'type': 'object', 'default': {'a_random_property': 'valid'}},
        {'type': 'array', 'default': [5, 6, 7]},
        {'type': 'string', 'default': ''},
        {'default': -1},  # if type is not defined any value is a valid value
        {'type': ['number', 'boolean'], 'default': 8},
        {'type': ['number', 'boolean'], 'default': False},
    ],
)
def test_api_check_default_succeed(partial_parameter_spec):
    apis = {
        '/api': {
            'get': {
                'parameters': [
                    dict({'name': 'param', 'in': 'query'}, **partial_parameter_spec),
                ],
            },
        },
    }

    # Success if no exception are raised
    validate_apis(apis, lambda x: x)


@pytest.mark.parametrize(
    'partial_parameter_spec, validator, instance',
    [
        [
            {'type': 'integer', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'boolean', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'null', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'number', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'object', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'array', 'default': 'wrong_type'},
            'type', 'wrong_type',
        ],
        [
            {'type': 'string', 'default': -1},
            'type', -1,
        ],
        [
            {'type': 'string', 'minLength': 100, 'default': 'short_string'},
            'minLength', 'short_string',
        ],
        [
            {'type': ['number', 'boolean'], 'default': 'not_a_number_or_boolean'},
            'type', 'not_a_number_or_boolean',
        ],
    ],
)
def test_api_check_default_fails(partial_parameter_spec, validator, instance):
    apis = {
        '/api': {
            'get': {
                'parameters': [
                    dict({'name': 'param', 'in': 'query'}, **partial_parameter_spec),
                ],
            },
        },
    }

    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_apis(apis, lambda x: x)

    validation_error = excinfo.value.args[1]
    assert validation_error.instance == instance
    assert validation_error.validator == validator
