from token_manager.manager import TokenManager
import jwt


def test_token_creation_and_refresh():
    secret = 'LAB-TOKEN-MANAGER-DUMMY-KEY-FOR-TESTS'
    manager = TokenManager(secret)
    access, refresh = manager.generate_tokens('user1')
    payload = jwt.decode(access, secret, algorithms=['HS256'])
    assert payload['sub'] == 'user1'
    assert payload['type'] == 'access'
    new_access = manager.refresh_access_token(refresh)
    assert new_access is not None


def test_refresh_revocation_and_invalid_tokens():
    manager = TokenManager('LAB-TOKEN-MANAGER-DUMMY-KEY-FOR-TESTS')
    access, refresh = manager.generate_tokens('user1')
    assert manager.refresh_access_token(access) is None
    assert manager.refresh_access_token('invalid') is None
    assert manager.revoke_refresh_token(refresh) is True
    assert manager.refresh_access_token(refresh) is None
