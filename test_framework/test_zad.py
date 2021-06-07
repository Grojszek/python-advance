import pytest
import requests

URL = 'https://reqres.in/api/login'
ERROR_CODE, PASS_CODE = 400, 200


@pytest.mark.parametrize('body', [{'email': 'eve.holt@reqres.in', 'password': 'cityslicka'}, {'email': 'peter@klaven'}])
def test_login(body):
    request_data = requests.post(URL, json=body)
    try:
        if body['password'] and body['email']:
            assert request_data.status_code == PASS_CODE
    except KeyError:
        assert request_data.status_code == ERROR_CODE
