import json

from django.shortcuts import HttpResponse

from rumahiot_sidik.apps.authentication.utils import RequestUtils, ResponseGenerator, SidikUtils
from rumahiot_sidik.apps.authentication.jwt import SidikJWT

# Decorator to make sure the request method is post
def post_method_required(function):

    def post_check(request, *args, **kwargs):
        # Sidik class
        rg = ResponseGenerator()

        if request.method == "POST" :
            return function(request, *args, **kwargs)
        else:
            response_data = rg.error_response_generator(400, 'Bad request method')
            return HttpResponse(json.dumps(response_data), content_type='application/json', status=400)
    post_check.__doc__ = function.__doc__
    post_check.__name__ = function.__name__
    
    return post_check


# Decorator to make sure the request method is post
def get_method_required(function):
    def get_check(request, *args, **kwargs):
        # Sidik class
        rg = ResponseGenerator()

        if request.method == "GET":
            return function(request, *args, **kwargs)
        else:
            response_data = rg.error_response_generator(400, 'Bad request method')
            return HttpResponse(json.dumps(response_data), content_type='application/json', status=400)

    get_check.__doc__ = function.__doc__
    get_check.__name__ = function.__name__

    return get_check

# Decorator to make sure admin is authenticated
# This function implementation is different from other service
def admin_authentication_required(function):

    def token_check(request, *args, **kwargs):

        requtils = RequestUtils()
        rg = ResponseGenerator()
        jwt = SidikJWT()

        # Check the token
        try:
            token = requtils.get_access_token(request)
        except KeyError:
            response_data = rg.error_response_generator(2, 'Please define the authorization header')
            return HttpResponse(json.dumps(response_data), content_type='application/json', status=401)
        else:
            if token['token'] != None:
                result = jwt.admin_token_validator(token['token'])
                if result['error'] != None:
                    response_data = rg.error_response_generator(401, result['error'])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
                else:
                    return function(request, *args, **kwargs)
            else:
                response_data = rg.error_response_generator(2, token['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

    token_check.__doc__ = function.__doc__
    token_check.__name__ = function.__name__

    return token_check
