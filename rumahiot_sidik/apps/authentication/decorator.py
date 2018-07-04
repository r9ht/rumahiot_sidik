import json

from django.shortcuts import HttpResponse

from rumahiot_sidik.apps.authentication.utils import RequestUtils, ResponseGenerator, SidikUtils

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


