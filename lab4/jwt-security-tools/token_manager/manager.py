import datetime
import uuid

import jwt


class TokenManager:
    def __init__(self, secret, algorithm='HS256', access_exp=15, refresh_exp=60 * 24):
        if access_exp <= 0 or refresh_exp <= 0:
            raise ValueError('Token lifetimes must be positive (minutes)')
        if algorithm == 'none':
            raise ValueError('Unsigned tokens are not supported')
        self.secret = secret
        self.algorithm = algorithm
        self.access_exp = access_exp
        self.refresh_exp = refresh_exp
        # Addition to PDF: process-local revocation, retained until token expiry.
        self.revoked_refresh_tokens = {}

    def _generate(self, payload, exp_minutes):
        payload = dict(payload)
        now = datetime.datetime.now(datetime.timezone.utc)
        payload['iat'] = now
        payload['exp'] = now + datetime.timedelta(minutes=exp_minutes)
        payload['jti'] = uuid.uuid4().hex
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def generate_tokens(self, user_id):
        user_id = str(user_id)
        access_token = self._generate({'sub': user_id, 'type': 'access'}, self.access_exp)
        refresh_token = self._generate({'sub': user_id, 'type': 'refresh'}, self.refresh_exp)
        return access_token, refresh_token

    def _decode_refresh(self, refresh_token):
        payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm],
                             options={'require': ['exp', 'sub', 'type', 'jti']})
        if payload['type'] != 'refresh':
            raise jwt.InvalidTokenError('Expected a refresh token')
        return payload

    def _prune_revoked(self):
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        self.revoked_refresh_tokens = {
            jti: expiry for jti, expiry in self.revoked_refresh_tokens.items()
            if expiry > now
        }

    def refresh_access_token(self, refresh_token):
        try:
            payload = self._decode_refresh(refresh_token)
            self._prune_revoked()
            if payload['jti'] in self.revoked_refresh_tokens:
                return None
            return self._generate({'sub': payload['sub'], 'type': 'access'}, self.access_exp)
        except jwt.InvalidTokenError:
            return None

    def revoke_refresh_token(self, refresh_token):
        """Addition to PDF 4.4.2, implements the objective in 4.4.1."""
        try:
            payload = self._decode_refresh(refresh_token)
            self._prune_revoked()
            self.revoked_refresh_tokens[payload['jti']] = payload['exp']
            return True
        except jwt.InvalidTokenError:
            return False
