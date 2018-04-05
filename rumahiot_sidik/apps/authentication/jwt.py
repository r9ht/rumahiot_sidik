import os
from datetime import datetime
from datetime import timedelta

import jwt
from jwt import exceptions


class SidikJWT:

    # generate jwt token
    # uuid -> universal unique identifier
    # param : user_uuid(string)
    # return : token (string)
    # Encoded using the secret key , algorithm : HS256
    def token_generator(self, user_uuid):
        # Expired time hardcoded in this function
        # Current : 15 minute from the time the code was generated
        # exp in float type (unix timestap)
        exp = datetime.now() + timedelta(minutes=24)

        payload = {
            'user_uuid': str(user_uuid),
            'exp': exp.timestamp()
        }
        return jwt.encode(payload, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256').decode('utf-8')

    # Checked using the secret key , algorithm : HS256
    def token_validator(self, token):
        data = {}
        try:
            payload = jwt.decode(token, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256')
        except NotImplementedError:
            data['payload'] = None
            data['error'] = 'Invalid JWT structure'
            return data
        except exceptions.DecodeError:
            data['payload'] = None
            data['error'] = 'Invalid JWT signature'
            return data
        except exceptions.InvalidAlgorithmError:
            data['payload'] = None
            data['error'] = 'Invalid JWT algorithm spesified'
            return data
        except exceptions.ExpiredSignatureError:
            data['payload'] = None
            data['error'] = 'Token expired'
            return data
        else:
            data['payload'] = payload
            data['error'] = None
            return data
