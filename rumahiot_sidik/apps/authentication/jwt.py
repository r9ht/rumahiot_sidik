import jwt
from jwt import exceptions
import os
from datetime import datetime
from datetime import timedelta

# verify jwt token
# input parameter : token (string)
# return : is_valid(boolean) , payload (dict) , error_message (string) -> if invalid
# verified using the secret key , algorithm : HS256
def token_verifier(token):
    data = {}
    try :
        payload = jwt.decode(token,os.environ.get('SIDIK_SECRET_KEY',''),algorithm='HS256')
    except NotImplementedError:
        data['is_valid'] = False
        data['payload'] = None
        data['error_message'] = "Invalid algorithm specified"
        return data
    except exceptions.DecodeError:
        data['is_valid'] = False
        data['payload'] = None
        data['error_message'] = "Invalid secret specified"
        return data
    except exceptions.InvalidAlgorithmError:
        data['is_valid'] = False
        data['payload'] = None
        data['error_message'] = "Invalid algorithm specified"
        return data
    except exceptions.ExpiredSignatureError:
        data['is_valid'] = False
        data['payload'] = None
        data['error_message'] = "Expired token, please generate a new one"
        return data
    else:
        data['is_valid'] = True
        data['payload'] = payload
        data['error_message'] = None
        return data

# generate jwt token
# uuid -> universal unique identifier
# param : uuid(string)
# return : token (string)
# Encoded using the secret key , algorithm : HS256
def token_generator(session_key):
    # Expired time hardcoded in this function
    # Current : 1 hour from the time the code was generated
    # exp in float type (unix timestap)
    exp = datetime.now() + timedelta(hours=1)

    payload = {
        'session' : str(session_key),
        'exp' : exp.timestamp()
    }
    return jwt.encode(payload,os.environ.get('SIDIK_SECRET_KEY',''),algorithm='HS256')




