from flask import Flask, request, jsonify
import jwt


class APIGateway:
    def __init__(self, secret, algorithm='HS256'):
        if algorithm == 'none':
            raise ValueError('Unsigned tokens are not supported')
        self.secret = secret
        self.algorithm = algorithm
        self.app = Flask(__name__)
        self.routes()

    def routes(self):
        @self.app.route('/protected')
        def protected():
            parts = request.headers.get('Authorization', '').split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'message': 'Access denied'}), 401
            try:
                payload = jwt.decode(parts[1], self.secret, algorithms=[self.algorithm],
                                     options={'require': ['exp', 'sub', 'type']})
                if payload['type'] != 'access':
                    return jsonify({'message': 'Access denied'}), 401
                return jsonify({'message': 'Access granted', 'user': payload['sub']}), 200
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Access denied'}), 401

    def run(self):
        self.app.run(host='127.0.0.1', port=5000, debug=False)
