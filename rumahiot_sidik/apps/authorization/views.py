import json

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rumahiot_sidik.apps.authentication.dynamodb import SidikDynamoDB
from rumahiot_sidik.apps.authentication.jwt import SidikJWT
from rumahiot_sidik.apps.authentication.utils import SidikUtils, ResponseGenerator, RequestUtils
from rumahiot_sidik.apps.authorization.forms import TokenValidationForm, ChangePasswordForm
from rumahiot_sidik.apps.surat_modules.send_email import SidikSuratModule


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
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=403)
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
def email_activation(request, activation_uuid):
    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()
    sm = SidikSuratModule()

    if request.method == 'GET':
        user = db.get_user_by_activation_uuid(activation_uuid=activation_uuid)
        # the activation_uuid doesn't exist
        if len(user) != 0:
            if user[0]['activated'] == False:
                try:
                    db.activate_user_account(user[0]['user_uuid'])
                except:
                    response_data = rg.error_response_generator(500, "Internal server error")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    # Send welcome email
                    response = sm.send_welcome_email(user[0]['email'])
                    if response.status_code == 200:
                        response_data = rg.success_response_generator(200,
                                                                      "Your account has been activated")
                        return HttpResponse(json.dumps(response_data), content_type="application/json",
                                            status=200)
                    else:
                        # unknown client error
                        response_data = rg.error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json",
                                            status=500)


            else:
                # account already activated
                response_data = rg.error_response_generator(400, 'Activation UUID does not valid or exist')
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

        else:
            response_data = rg.error_response_generator(400, 'Activation UUID does not valid or exist')
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

    else:
        response_data = rg.error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)


@csrf_exempt
def change_password(request):
    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()
    su = SidikUtils()
    requtils = RequestUtils()
    jwt = SidikJWT()

    if request.method == "POST":
        try:
            token = requtils.get_access_token(request)
        except KeyError:
            response_data = rg.error_response_generator(400, "Please define the authorization header")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            if token['token'] is not None:
                data = jwt.token_validator(token['token'])
                if data['payload'] != None:
                    form = ChangePasswordForm(request.POST)
                    if form.is_valid():
                        user = db.get_user_by_user_uuid(data['payload']['user_uuid'])
                        # check for unknown error
                        if len(user) != 0:
                            hashed_old_password = su.password_hasher(salt=user[0]['salt'],
                                                                     password=form.cleaned_data['old_password'])
                            # Check if the old password match
                            if hashed_old_password == user[0]['password']:
                                try:
                                    db.change_user_password(user_uuid=user[0]['user_uuid'],
                                                            new_password=form.cleaned_data['new_password'])
                                except:
                                    # Catch unknown client error
                                    # unknown client error
                                    response_data = rg.error_response_generator(500, "Internal server error")
                                    return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                        status=500)
                                else:
                                    response_data = rg.success_response_generator(200,
                                                                                  "Your password successfully changed")
                                    return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                        status=200)
                            else:
                                response_data = rg.error_response_generator(400,
                                                                            "Incorrect old password")
                                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                    status=400)
                        else:
                            # unknown client error
                            response_data = rg.error_response_generator(500, "Internal server error")
                            return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                status=500)
                    else:
                        # Todo : push the error from form to here , change the error type
                        response_data = rg.error_response_generator(400,
                                                                    "Missmatch password or invalid parameter submitted")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                else:
                    response_data = rg.error_response_generator(400, data['error'])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
            else:
                response_data = rg.error_response_generator(400, token['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

    else:
        response_data = rg.error_response_generator(400, "Bad request method")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

# @csrf_exempt
# def device_key_validation(request):
#
#     # Sidik classes
#     rg = ResponseGenerator()
#     db = SidikDynamoDB()
#
#     if request.method != "POST":
#         response_data = rg.error_response_generator(400, 'Invalid request method')
#         return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#     else:
#         try:
#             form = DeviceKeyValidationForm(request.POST)
#         except KeyError:
#             response_data = rg.error_response_generator(500, "Internal server error")
#             return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
#         else:
#             if form.is_valid():
#                 # for write key
#                 if form.cleaned_data['key_type'] == 'w':
#                     try:
#                         device_uuid = db.get_device_uuid_by_write_key(form.cleaned_data['device_key'])
#                     except:
#                         response_data = rg.error_response_generator(400, "Invalid write key")
#                         return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#                     else:
#                         data = {
#                             'device_uuid': device_uuid
#                         }
#                         response_data = rg.data_response_generator(data)
#                         return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
#
#                 # for read key
#                 elif form.cleaned_data['key_type'] == 'r':
#                     try:
#                         device_uuid = db.get_device_uuid_by_read_key(form.cleaned_data['device_key'])
#                     except:
#                         response_data = rg.error_response_generator(400, "Invalid read key")
#                         return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#                     else:
#                         data = {
#                             'device_uuid': device_uuid
#                         }
#                         response_data = rg.data_response_generator(data)
#                         return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
#                 else:
#                     response_data = rg.error_response_generator(400, "Invalid key type")
#                     return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
#             else:
#                 response_data = rg.error_response_generator(400, "invalid or missing parameter submitted")
#                 return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#

#
# # todo : secure the mongo & redis instance with adding ip address source range
#
# @csrf_exempt
# def device_key_refresh(request):
#     # Sidik classes
#     rg = ResponseGenerator()
#     db = SidikDynamoDB()
#     requtils = RequestUtils()
#     jwt = SidikJWT()
#
#     if request.method != "POST":
#         response_data = rg.error_response_generator(400, 'Invalid request method')
#         return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#     else:
#         try:
#             token = requtils.get_access_token(request)
#         except KeyError:
#             response_data = rg.error_response_generator(400, "Please define the authorization header")
#             return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#         else:
#             if token['token'] is None:
#                 response_data = rg.error_response_generator(400, token['error'])
#                 return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#             else:
#                 try:
#                     data = jwt.token_validator(token['token'])
#
#                 # catch unknown error
#                 except:
#                     response_data = rg.error_response_generator(500, "Internal server error")
#                     return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
#                 else:
#                     if data['payload'] == None:
#                         response_data = rg.error_response_generator(400, data['error'])
#                         return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
#                     else:
#                         try:
#                             user_uuid = data['payload']['user_uuid']
#                         # catch unknown error
#                         except :
#                             response_data = rg.error_response_generator(500, "Internal server error")
#                             return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
#                         else:
#                             # initiate the form
#                             try:
#                                 form = DeviceKeyRefreshForm(request.POST)
#                             except KeyError:
#                                 response_data = rg.error_response_generator(500, "Internal server error")
#                                 return HttpResponse(json.dumps(response_data), content_type="application/json",
#                                                     status=500)
#                             else:
#                                 if form.is_valid():
#                                     try:
#                                         data = db.get_device_detail(form.cleaned_data['device_uuid'])
#                                     # catch unknown error
#                                     except:
#                                         response_data = rg.error_response_generator(500, "Internal server error")
#                                         return HttpResponse(json.dumps(response_data), content_type="application/json",
#                                                             status=500)
#                                     else:
#                                         # when the result is empty
#                                         if len(data) == 0:
#                                             response_data = rg.error_response_generator(400, "Invalid device UUID")
#                                             return HttpResponse(json.dumps(response_data),
#                                                                 content_type="application/json",
#                                                                 status=400)
#                                         else:
#                                             if data[0]['user_uuid'] != user_uuid:
#                                                 response_data = rg.error_response_generator(400, "Bad request")
#                                                 return HttpResponse(json.dumps(response_data),
#                                                                     content_type="application/json",
#                                                                     status=400)
#                                             else:
#                                                 try:
#                                                     db.refresh_device_key(form.cleaned_data['device_uuid'])
#                                                     # catch unknown error
#                                                 except:
#                                                     response_data = rg.error_response_generator(500,"Internal server error")
#                                                     return HttpResponse(json.dumps(response_data),
#                                                                         content_type="application/json",
#                                                                         status=500)
#                                                 else:
#                                                     response_data = rg.success_response_generator(200,'Device read & write key refreshed')
#                                                     return HttpResponse(json.dumps(response_data),
#                                                                         content_type="application/json", status=200)
#                                 else:
#                                     response_data = rg.error_response_generator(400,
#                                                                                 "invalid or missing parameter submitted")
#                                     return HttpResponse(json.dumps(response_data), content_type="application/json",
#                                                         status=400)
#
#
#
#
#
