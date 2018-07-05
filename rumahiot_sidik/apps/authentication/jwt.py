import os
from datetime import datetime
from datetime import timedelta

import jwt
from jwt import exceptions


class SidikJWT:

    # Generate JWT token
    # uuid -> universal unique identifier
    # param : user_uuid(string)
    # return : token (string)
    # Encoded using the secret key , algorithm : HS256
    def token_generator(self, user_uuid):
        # Expired time hardcoded in this function
        # Current : 24 minute from the time the code was generated
        # exp in float type (unix timestap)
        exp = datetime.now() + timedelta(minutes=24)

        payload = {
            'user_uuid': str(user_uuid),
            'exp': exp.timestamp()
        }
        return jwt.encode(payload, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256').decode('utf-8')

    # Generate JWT for admin
    def admin_token_generator(self, user_uuid):
        # Expired time hardcoded in this function
        # Current : 24 minute from the time the code was generated
        # exp in float type (unix timestap)
        exp = datetime.now() + timedelta(minutes=24)

        payload = {
            'user_uuid': str(user_uuid),
            'exp': exp.timestamp(),
            'admin': True
        }
        return jwt.encode(payload, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256').decode('utf-8')

    # Admin token validator
    # Checked using the secret key , algorithm : HS256
    def admin_token_validator(self, token):
        data = {}
        try:
            payload = jwt.decode(token, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256')
        except NotImplementedError:
            data['payload'] = None
            data['error'] = 'Invalid JWT structure, please reauthenticate'
            return data
        except exceptions.DecodeError:
            data['payload'] = None
            data['error'] = 'Invalid JWT signature, please reauthenticate'
            return data
        except exceptions.InvalidAlgorithmError:
            data['payload'] = None
            data['error'] = 'Invalid JWT algorithm spesified, please reauthenticate'
            return data
        except exceptions.ExpiredSignatureError:
            data['payload'] = None
            data['error'] = 'Token expired, Please reauthenticate'
            return data
        else:
            # Check for admin tag
            if 'admin' in payload :
                if (payload['admin']) :
                    data['payload'] = payload
                    data['error'] = None
                    return data
                else:
                    data['payload'] = None
                    data['error'] = 'Invalid account used'
                    return data

            else:
                data['payload'] = None
                data['error'] = 'Invalid account used'
                return data


    # Checked using the secret key , algorithm : HS256
    def token_validator(self, token):
        data = {}
        try:
            payload = jwt.decode(token, os.environ.get('SIDIK_SECRET_KEY', ''), algorithm='HS256')
        except NotImplementedError:
            data['payload'] = None
            data['error'] = 'Invalid JWT structure, please reauthenticate'
            return data
        except exceptions.DecodeError:
            data['payload'] = None
            data['error'] = 'Invalid JWT signature, please reauthenticate'
            return data
        except exceptions.InvalidAlgorithmError:
            data['payload'] = None
            data['error'] = 'Invalid JWT algorithm spesified, please reauthenticate'
            return data
        except exceptions.ExpiredSignatureError:
            data['payload'] = None
            data['error'] = 'Token expired, Please reauthenticate'
            return data
        else:
            data['payload'] = payload
            data['error'] = None
            return data
