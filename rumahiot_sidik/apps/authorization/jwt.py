import jwt
from jwt import exceptions
import os
# Checked using the secret key , algorithm : HS256
def token_validator(token):
    data = {}
    try :
        payload = jwt.decode(token,os.environ.get('SIDIK_SECRET_KEY',''),algorithm='HS256')
    except NotImplementedError:
        data['payload'] = None
        data['error'] = 'Invalid JWT structure'
        return data
    except exceptions.DecodeError:
        data['payload'] = None
        data['error'] = 'Invalid signature'
        return data
    except exceptions.InvalidAlgorithmError:
        data['payload'] = None
        data['error'] = 'Invalid algorithm spesified'
        return data
    except exceptions.ExpiredSignatureError:
        data['payload'] = None
        data['error'] = 'Token expired'
        return data
    else:
       data['payload'] = payload
       data['error'] = None
       return data