from jwt_validator.validator import JWTValidator
import jwt
import datetime


def generate_token(secret):
    payload = {
        'sub': 'test',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def test_valid_token():
    secret = 'LAB-VALIDATOR-DUMMY-KEY-FOR-TESTS-ONLY'
    token = generate_token(secret)
    validator = JWTValidator(secret)
    result = validator.validate(token)
    assert result['valid'] is True
    assert result['payload']['sub'] == 'test'


def test_invalid_signature():
    token = generate_token('LAB-WRONG-DUMMY-KEY-FOR-TESTS-ONLY')
    validator = JWTValidator('LAB-CORRECT-DUMMY-KEY-FOR-TESTS-ONLY')
    result = validator.validate(token)
    assert result['valid'] is False
    assert result['reason'] == 'Invalid signature'


def test_expired_token():
    secret = 'LAB-VALIDATOR-DUMMY-KEY-FOR-TESTS-ONLY'
    token = jwt.encode({'sub': 'test', 'exp': datetime.datetime.now(datetime.timezone.utc)
                       - datetime.timedelta(minutes=1)}, secret, algorithm='HS256')
    assert JWTValidator(secret).validate(token) == {'valid': False, 'reason': 'Token expired'}


def test_missing_expiration():
    secret = 'LAB-VALIDATOR-DUMMY-KEY-FOR-TESTS-ONLY'
    token = jwt.encode({'sub': 'test'}, secret, algorithm='HS256')
    assert JWTValidator(secret).validate(token)['valid'] is False
