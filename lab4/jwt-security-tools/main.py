from api_gateway.gateway import APIGateway
from token_manager.manager import TokenManager


def main():
    # Public dummy configuration for this local exercise, never a production key.
    secret = 'LAB-ONLY-DEMO-KEY-DO-NOT-USE-IN-PRODUCTION'
    manager = TokenManager(secret)
    access_token, refresh_token = manager.generate_tokens('nguyen')
    print('Local lab only; redact token strings in screenshots and reports.')
    print('Access Token:', access_token)
    print('Refresh Token:', refresh_token)
    gateway = APIGateway(secret)
    gateway.run()


if __name__ == '__main__':
    main()
