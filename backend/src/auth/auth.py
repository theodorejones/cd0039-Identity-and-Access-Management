import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-sbt6d75y.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://localhost:5000'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    
    header = request.headers.get("Authorization", None)

    if not header:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Expected authorization header not present"}, 401)

    parts = header.split(' ')

    if len(parts) != 2 or not parts:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header format must be as follows: '
            ' Bearer token'}, 401)

    elif parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with Bearer'}, 401)

    return parts[1]

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission Not found',
        }, 401)
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'}, 401)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {'kty': key['kty'], 'kid': key['kid'], 'use': key['use'], 'n': key['n'], 'e': key['e']}
            break
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/')
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, '
                'check the audience and issuer.'}, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'}, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'}, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator