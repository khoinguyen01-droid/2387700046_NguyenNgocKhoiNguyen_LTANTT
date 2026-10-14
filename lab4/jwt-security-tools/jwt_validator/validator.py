import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError


class JWTValidator:
    def __init__(self, secret, algorithms=None):
        self.secret = secret
        self.algorithms = list(algorithms) if algorithms is not None else ['HS256']
        if not self.algorithms or 'none' in self.algorithms:
            raise ValueError('A signed JWT algorithm must be configured')

    def validate(self, token: str):
        try:
            payload = jwt.decode(token, self.secret, algorithms=self.algorithms,
                                 options={'require': ['exp']})
            return {'valid': True, 'payload': payload}
        except ExpiredSignatureError:
            return {'valid': False, 'reason': 'Token expired'}
        except InvalidSignatureError:
            return {'valid': False, 'reason': 'Invalid signature'}
        except InvalidTokenError as exc:
            return {'valid': False, 'reason': str(exc)}
