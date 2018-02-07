import hashlib,requests,os


class SidikUtils():
    # return : salt(string),hashed_password(string)
    # salt will be used as uuid in the user table
    def password_hasher(self,salt, password):
        return hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()

    def recaptcha_verify(self,captcha_response):
        # dont forget to put the secret in environment instead
        # return value recaptcha response : boolean

        recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"

        post_data = {
            'secret': os.environ.get('RECAPTCHA_SECRET_KEY', ''),
            'response': str(captcha_response),
        }

        post_response = requests.post(recaptcha_verify_url, data=post_data)
        post_response = post_response.json()

        if str(post_response['success']) == "True":
            return True
        else:
            return False


class ResponseGenerator():
    # generate error response in dict format
    def error_response_generator(self, code, message):
        response = {
            "error": {
                "code": code,
                "message": message
            }
        }
        return response

    # generate data response in dict format
    # input parameter data(dict)
    def data_response_generator(self, data):
        response = {
            "data": data
        }
        return response

    # generate error response in dict format
    def success_response_generator(self, code, message):
        response = {
            "success": {
                "code": code,
                "message": message
            }
        }
        return response

class RequestUtils():
    # get access token from authorization header
    # input parameter : request(request)
    # return :  data['token'] = token, when the header format is correct (string)
    #           data['error'] = None, when the header format is correct
    #           data['token'] = None, when the header format is incorrect
    #           data['error'] = Error, when the header format is incorrect(string)
    # data = {
    #     'token' : token(string),
    #     'error' : error(string)
    # }
    def get_access_token(self, request):
        data = {}
        auth_header = request.META['HTTP_AUTHORIZATION'].split()
        # verify the authorization header length (including authorization type, currently using bearer)
        if len(auth_header) != 2:
            data['token'] = None
            data['error'] = 'Invalid authorization header length'
            return data
        else:
            # check for the type
            if auth_header[0].lower() != 'bearer':
                data['token'] = None
                data['error'] = 'Invalid authorization token method'
                return data
            else:
                data['token'] = auth_header[1]
                data['error'] = None
                return data

