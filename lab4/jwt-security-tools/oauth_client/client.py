from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

import requests


class OAuthClient:
    def __init__(self, client_id, client_secret, auth_url, token_url, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri

    def get_auth_url(self, scope='openid', state=None):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
        }
        if state is not None:
            params['state'] = state
        parsed = urlsplit(self.auth_url)
        query = parse_qsl(parsed.query, keep_blank_values=True)
        query = [(key, value) for key, value in query if key not in params]
        query.extend(params.items())
        return urlunsplit(parsed._replace(query=urlencode(query)))

    def get_token(self, code):
        # Caller must validate callback state before exchanging the code.
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(self.token_url, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
