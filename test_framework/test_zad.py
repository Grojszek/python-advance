import requests
import pytest

URL = 'https://reqres.in/api/users?page=2'
URL2 = 'https://reqres.in/api/login'


@pytest.mark.parametrize('body', [{"email": "eve.holt@reqres.in", "password": "cityslicka"},
                                  {"email": "peter@klaven"}])
def test_login(body):
    request_data = requests.post(URL2, json=body)
    try:
        if body['password'] and body['email']:
            assert request_data.status_code == 200
    except KeyError:
        assert request_data.status_code == 400


