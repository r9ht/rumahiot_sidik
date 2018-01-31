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


