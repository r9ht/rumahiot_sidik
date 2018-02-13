from django.shortcuts import render,HttpResponse
from rumahiot_sidik.apps.authentication.jwt import SidikJWT
from rumahiot_sidik.apps.authentication.dynamodb import SidikDynamoDB
from rumahiot_sidik.apps.authentication.utils import SidikUtils,ResponseGenerator, RequestUtils
from django.views.decorators.csrf import csrf_exempt
import json
from rumahiot_sidik.apps.authorization.forms import TokenValidationForm,DeviceKeyValidationForm,DeviceKeyRefreshForm

# Create your views here.
# Todo : Protect this endpoint with key

# Validate token that sent , returning user_uuid and other data based on the request
@csrf_exempt
def token_validation(request):

    # Sidik classes
    jwt = SidikJWT()
    rg = ResponseGenerator()
    db = SidikDynamoDB()

    if request.method != "POST":
        response_data = rg.error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:

        try:
            form = TokenValidationForm(request.POST)
        except KeyError:
            response_data = rg.error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            if form.is_valid():
                # try to get the payload
                result = jwt.token_validator(form.cleaned_data['token'])
                if result['error'] != None:
                    response_data = rg.error_response_generator(400, result['error'])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                else:

                    # If email address requested
                    if form.cleaned_data['email'] == "1":
                        user = db.get_user_by_user_uuid(result['payload']['user_uuid'])
                        result['payload']['email'] = user[0]['email']
                    data = {
                        'token': form.cleaned_data['token'],
                        'payload': result['payload']
                    }
                    response_data = rg.data_response_generator(data)
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

            else:
                response_data = rg.error_response_generator(400, "invalid or missing parameter submitted")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

@csrf_exempt
def device_key_validation(request):

    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()

    if request.method != "POST":
        response_data = rg.error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        try:
            form = DeviceKeyValidationForm(request.POST)
        except KeyError:
            response_data = rg.error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            if form.is_valid():
                # for write key
                if form.cleaned_data['key_type'] == 'w':
                    try:
                        device_uuid = db.get_device_uuid_by_write_key(form.cleaned_data['device_key'])
                    except:
                        response_data = rg.error_response_generator(400, "Invalid write key")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                    else:
                        data = {
                            'device_uuid': device_uuid
                        }
                        response_data = rg.data_response_generator(data)
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

                # for read key
                elif form.cleaned_data['key_type'] == 'r':
                    try:
                        device_uuid = db.get_device_uuid_by_read_key(form.cleaned_data['device_key'])
                    except:
                        response_data = rg.error_response_generator(400, "Invalid read key")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                    else:
                        data = {
                            'device_uuid': device_uuid
                        }
                        response_data = rg.data_response_generator(data)
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
                else:
                    response_data = rg.error_response_generator(400, "Invalid key type")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
            else:
                response_data = rg.error_response_generator(400, "invalid or missing parameter submitted")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)



# todo : secure the mongo & redis instance with adding ip address source range

@csrf_exempt
def device_key_refresh(request):
    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()
    requtils = RequestUtils()
    jwt = SidikJWT()

    if request.method != "POST":
        response_data = rg.error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        try:
            token = requtils.get_access_token(request)
        except KeyError:
            response_data = rg.error_response_generator(400, "Please define the authorization header")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            if token['token'] is None:
                response_data = rg.error_response_generator(400, token['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
            else:
                try:
                    data = jwt.token_validator(token['token'])

                # catch unknown error
                except:
                    response_data = rg.error_response_generator(500, "Internal server error")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    if data['payload'] == None:
                        response_data = rg.error_response_generator(400, data['error'])
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                    else:
                        try:
                            user_uuid = data['payload']['user_uuid']
                        # catch unknown error
                        except :
                            response_data = rg.error_response_generator(500, "Internal server error")
                            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                        else:
                            # initiate the form
                            try:
                                form = DeviceKeyRefreshForm(request.POST)
                            except KeyError:
                                response_data = rg.error_response_generator(500, "Internal server error")
                                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                    status=500)
                            else:
                                if form.is_valid():
                                    try:
                                        data = db.get_device_detail(form.cleaned_data['device_uuid'])
                                    # catch unknown error
                                    except:
                                        response_data = rg.error_response_generator(500, "Internal server error")
                                        return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                            status=500)
                                    else:
                                        # when the result is empty
                                        if len(data) == 0:
                                            response_data = rg.error_response_generator(400, "Invalid device UUID")
                                            return HttpResponse(json.dumps(response_data),
                                                                content_type="application/json",
                                                                status=400)
                                        else:
                                            if data[0]['user_uuid'] != user_uuid:
                                                response_data = rg.error_response_generator(400, "Bad request")
                                                return HttpResponse(json.dumps(response_data),
                                                                    content_type="application/json",
                                                                    status=400)
                                            else:
                                                try:
                                                    db.refresh_device_key(form.cleaned_data['device_uuid'])
                                                    # catch unknown error
                                                except:
                                                    response_data = rg.error_response_generator(500,"Internal server error")
                                                    return HttpResponse(json.dumps(response_data),
                                                                        content_type="application/json",
                                                                        status=500)
                                                else:
                                                    response_data = rg.success_response_generator(200,'Device read & write key refreshed')
                                                    return HttpResponse(json.dumps(response_data),
                                                                        content_type="application/json", status=200)
                                else:
                                    response_data = rg.error_response_generator(400,
                                                                                "invalid or missing parameter submitted")
                                    return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                        status=400)






