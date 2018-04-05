import json
from uuid import uuid4

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rumahiot_sidik.apps.authentication.dynamodb import SidikDynamoDB
from rumahiot_sidik.apps.authentication.forms import EmailLoginForm, EmailRegistrationForm, GetUserEmailForm
from rumahiot_sidik.apps.authentication.jwt import SidikJWT
from rumahiot_sidik.apps.authentication.utils import SidikUtils, ResponseGenerator, RequestUtils
from rumahiot_sidik.apps.surat_modules.send_email import SidikSuratModule
from rumahiot_sidik.settings import RUMAHIOT_SIDIK_API_KEY

# Create your views here.

# authenticate using email address and password
# todo : implement refresh token
@csrf_exempt
def email_authentication(request):
    # Sidik classes
    db = SidikDynamoDB()
    utils = SidikUtils()
    rg = ResponseGenerator()
    sidik_jwt = SidikJWT()

    if request.method != "POST":
        response_data = rg.error_response_generator(400, "Bad request method")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            try:
                # check user email and password
                user = db.check_user(form.cleaned_data['email'], form.cleaned_data['password'])
            except ImportError:
                response_data = rg.error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
            else:
                # if the account is valid
                if user['is_valid']:
                    try:
                        # create the token
                        data = {
                            "token": sidik_jwt.token_generator(user['user']['user_uuid'])
                        }
                    except:
                        response_data = rg.error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                    else:
                        response_data = rg.data_response_generator(data)
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

                else:
                    response_data = rg.error_response_generator(400, user["error_message"])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            response_data = rg.error_response_generator(400, 'invalid or missing parameter submitted')
            return HttpResponse(json.dumps(response_data), content_type='application/json', status=400)


@csrf_exempt
def email_registration(request):
    # Sidik classes
    db = SidikDynamoDB()
    utils = SidikUtils()
    rg = ResponseGenerator()
    sm = SidikSuratModule()

    if request.method != 'POST':
        response_data = rg.error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        # TODO : Generate error response for rumah iot & error response api for rumah IoT
        try:
            form = EmailRegistrationForm(request.POST)
        # Todo : Put key checking in the dorm , and remove this thing
        except KeyError:
            response_data = rg.error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            # is_recaptcha_valid = utils.recaptcha_verify(request.POST.get("g_recaptcha_response", "")) g-recaptcha-response
            is_recaptcha_valid = utils.recaptcha_verify(request.POST.get("g-recaptcha-response", ""))
            if form.is_valid():
                if is_recaptcha_valid:
                    activation_uuid = uuid4().hex
                    try:
                        create_success = db.create_user_by_email(full_name=form.cleaned_data['full_name'],
                                                                 email=form.cleaned_data['email'],
                                                                 password=form.cleaned_data['password'],
                                                                 activation_uuid=activation_uuid)
                    except:
                        # unknown client error
                        response_data = rg.error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                    else:
                        if create_success:
                            # Send confirmation email
                            response = sm.send_activation_email(email=form.cleaned_data['email'],
                                                                activation_uuid=activation_uuid)
                            if response.status_code == 200:
                                response_data = rg.success_response_generator(200,
                                                                              "Successfully registered please check your email for confirmation")
                                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                    status=200)
                            else:
                                # unknown client error
                                response_data = rg.error_response_generator(500, "Internal server error")
                                return HttpResponse(json.dumps(response_data), content_type="application/json",
                                                    status=500)
                        else:
                            response_data = rg.error_response_generator(400,
                                                                        "Email already registered, please try another email")
                            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                else:
                    # if the recaptcha isn't valid
                    response_data = rg.error_response_generator(400, "Please complete the Recaptcha")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

            else:
                # Todo : push the error from form to here , change the error type
                response_data = rg.error_response_generator(400, "Missmatch password or invalid parameter submitted")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)


# Get user email using user_uuid
# This resource only available to authenticated service
# Only accessable using SIDIK_API_KEY as authorization header
@csrf_exempt
def get_user_email(request):

    # Sidik classes
    db = SidikDynamoDB()
    utils = SidikUtils()
    rg = ResponseGenerator()
    sm = SidikSuratModule()
    requtils = RequestUtils()

    if request.method == 'POST' :
        try:
            # API Key will be called token in this context
            token = requtils.get_access_token(request)
        except KeyError:
            response_data = rg.error_response_generator(400, "Please define the authorization header")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            if token['token'] is not None:
                form = GetUserEmailForm(request.POST)
                if form.is_valid():
                    # Check the API key
                    if token['token'] == RUMAHIOT_SIDIK_API_KEY:
                        user = db.get_user_by_user_uuid(user_uuid=form.cleaned_data['user_uuid'])
                        if len(user) == 1:
                            data = {
                                'user_uuid' : user[0]['user_uuid'],
                                'email': user[0]['email']
                            }
                            # Return the data
                            response_data = rg.data_response_generator(data)
                            return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
                        else:
                            response_data = rg.error_response_generator(400, "Invalid User UUID")
                            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                    else:
                        response_data = rg.error_response_generator(400, "Invalid API key")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                else:
                        response_data = rg.error_response_generator(400, 'invalid or missing parameter submitted')
                        return HttpResponse(json.dumps(response_data), content_type='application/json', status=400)
            else:
                response_data = rg.error_response_generator(400, token['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

    else:
        response_data = rg.error_response_generator(400, "Bad request method")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
