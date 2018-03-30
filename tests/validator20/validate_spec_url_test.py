# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os

import mock
import pytest

from swagger_spec_validator3.common import SwaggerValidationError
from swagger_spec_validator3.validator20 import validate_spec_url
from tests.conftest import is_urlopen_error


def test_success(petstore_contents):
    with mock.patch(
            'swagger_spec_validator3.validator20.read_url',
            return_value=json.loads(petstore_contents),
    ) as mock_read_url:
        validate_spec_url('http://localhost/api-docs')
        mock_read_url.assert_called_once_with('http://localhost/api-docs')


def test_success_crossref_url_yaml():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    urlpath = "file://{}".format(os.path.join(
        my_dir, "../data/v2.0/minimal.yaml"))
    validate_spec_url(urlpath)


def test_success_crossref_url_json():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    urlpath = "file://{}".format(os.path.join(
        my_dir, "../data/v2.0/relative_ref.json"))
    validate_spec_url(urlpath)


def test_raise_SwaggerValidationError_on_urlopen_error():
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_spec_url('http://foo')
    assert is_urlopen_error(excinfo.value)
