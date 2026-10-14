from concurrent.futures import ThreadPoolExecutor

import jwt


class JWTCracker:
    """Offline HS256 wordlist exercise, only for JWTs created in this lab."""

    def __init__(self, token, wordlist_path):
        self.token = token
        self.wordlist_path = wordlist_path

    def _try_secret(self, secret):
        try:
            jwt.decode(self.token, secret, algorithms=['HS256'])
            return secret
        except jwt.InvalidTokenError:
            return None

    def crack(self):
        with open(self.wordlist_path, 'r', encoding='utf-8') as wordlist:
            secrets = [line for line in wordlist.read().splitlines() if line]
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self._try_secret, secrets)
            for result in results:
                if result:
                    return result
        return None
