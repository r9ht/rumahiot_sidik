import jwt
from jwt import exceptions
import os
from datetime import datetime
from datetime import timedelta

# generate jwt token
# uuid -> universal unique identifier
# param : user_uuid(string)
# return : token (string)
# Encoded using the secret key , algorithm : HS256
def token_generator(user_uuid):
    # Expired time hardcoded in this function
    # Current : 15 minute from the time the code was generated
    # exp in float type (unix timestap)
    exp = datetime.now() + timedelta(minutes=15)

    payload = {
        'user_uuid' : str(user_uuid),
        'exp' : exp.timestamp()
    }
    return jwt.encode(payload,os.environ.get('SIDIK_SECRET_KEY',''),algorithm='HS256').decode('utf-8')


# input parameter : token (string)
# validate jwt token
# return :  data['payload'] = payload, when the token is valid (string)
#           data['error'] = None, when the token is valid (string)
#           data['payload'] = payload, when the token is invalid or expired
#           data['error'] = Error, message when the token is invalid (string)
# data = {
#     'payload' : payload(dict),
#     'error' : error(string)
# }


