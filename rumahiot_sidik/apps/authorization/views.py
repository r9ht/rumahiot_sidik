from django.shortcuts import render,HttpResponse
from rumahiot_sidik.apps.authorization.jwt import token_validator
from rumahiot_sidik.apps.authentication.utils import error_response_generator,data_response_generator,success_response_generator
from django.views.decorators.csrf import csrf_exempt
import json
from rumahiot_sidik.apps.authorization.forms import TokenValidationForm

# Create your views here.

@csrf_exempt
def token_validation(request):
    if request.method != "POST":
        response_data = error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        try:
            form = TokenValidationForm(request.POST)
        except KeyError:
            response_data = error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            if form.is_valid():
                # try to get the payload
                response = token_validator(form.cleaned_data['token'])
                if response['error'] != None:
                    response_data = error_response_generator(400, response['error'])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                else:
                    data = {
                        'token' : form.cleaned_data['token'],
                        'payload' : response['payload']
                    }
                    response_data = data_response_generator(data)
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

            else:
                response_data = error_response_generator(400, "invalid or missing parameter submitted")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)


# todo : secure the mongo & redis instance with adding ip address source range


