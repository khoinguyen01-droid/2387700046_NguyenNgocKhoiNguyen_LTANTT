from unittest.mock import patch

from oauth_client.client import OAuthClient


def test_auth_url():
    client = OAuthClient('client_id', 'LAB-CLIENT-DUMMY', 'https://auth.example',
                         'https://token.example', 'http://localhost')
    url = client.get_auth_url()
    assert url.startswith('https://auth.example?')
    assert 'client_id=client_id' in url


@patch('oauth_client.client.requests.post')
def test_code_exchange_offline(mock_post):
    mock_post.return_value.json.return_value = {'access_token': 'dummy-token'}
    client = OAuthClient('client_id', 'LAB-CLIENT-DUMMY', 'https://auth.example',
                         'https://token.example', 'http://localhost')
    assert client.get_token('lab-code') == {'access_token': 'dummy-token'}
    mock_post.assert_called_once_with('https://token.example', data={
        'grant_type': 'authorization_code', 'code': 'lab-code',
        'redirect_uri': 'http://localhost', 'client_id': 'client_id',
        'client_secret': 'LAB-CLIENT-DUMMY',
    }, timeout=10)
