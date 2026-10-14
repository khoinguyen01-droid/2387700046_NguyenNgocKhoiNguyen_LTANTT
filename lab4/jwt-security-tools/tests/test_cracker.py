from jwt_cracker.cracker import JWTCracker
import jwt


def test_crack_token(tmp_path):
    # Weak dummy key is intentional and used only for this offline lab token.
    secret = 'supersecret'
    token = jwt.encode({'sub': 'test'}, secret, algorithm='HS256')
    wordlist = tmp_path / 'wordlist.txt'
    # Closed before worker threads read it: compatible with Windows.
    wordlist.write_text('wrongpass\n123456\nsupersecret\n', encoding='utf-8')
    cracker = JWTCracker(token, wordlist)
    found = cracker.crack()
    assert found == 'supersecret'
