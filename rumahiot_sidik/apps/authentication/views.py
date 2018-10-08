import json
from uuid import uuid4

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rumahiot_sidik.apps.authentication.dynamodb import SidikDynamoDB
from rumahiot_sidik.apps.authentication.forms import EmailLoginForm, EmailRegistrationForm, GetUserEmailForm, UpdateUserAccountForm
from rumahiot_sidik.apps.authentication.jwt import SidikJWT
from rumahiot_sidik.apps.authentication.utils import SidikUtils, ResponseGenerator, RequestUtils
from rumahiot_sidik.apps.surat_modules.send_email import send_welcome_email, send_activation_email
from rumahiot_sidik.settings import RUMAHIOT_SIDIK_API_KEY

from rumahiot_sidik.apps.authentication.decorator import get_method_required, post_method_required, admin_authentication_required

# Create your views here.

# Get user list
@get_method_required
@admin_authentication_required
def get_user_list(request):
    # Sidik classes
    db = SidikDynamoDB()
    rg = ResponseGenerator()

    # Get all user
    users = db.get_all_user()
    user_payload = {
        'users': [],
        'user_count': len(users)
    }
    for user in users:
        # Change the boolean type for admin and activated
        activated = '0'
        admin = '0'
        if user['activated']:
            activated = '1'
        if user['admin']:
            admin ='1'

        user = {
            'user_uuid': user['user_uuid'],
            'email': user['email'],
            'activated': activated,
            'admin': admin,
            'time_created': user['time_created'],
        }
        user_payload['users'].append(user)
    response_data = rg.data_response_generator(user_payload)
    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

@csrf_exempt
@post_method_required
@admin_authentication_required
def update_user_account(request):
    # Sidik classes
    db = SidikDynamoDB()
    rg = ResponseGenerator()

    form = UpdateUserAccountForm(request.POST)
    if form.is_valid():
        user = db.get_user_by_user_uuid(user_uuid=form.cleaned_data['user_uuid'])
        if len(user) == 1:
            # Normalize the data
            activated = False
            admin = False

            if form.cleaned_data['admin'] == "1":
                admin = True
            if form.cleaned_data['activated'] == "1":
                activated = True

            # Update user account
            db.update_account_data(user_uuid=form.cleaned_data['user_uuid'], activated=activated, admin=admin)
            response_data = rg.success_response_generator(200, "User account successfully updated")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

        else:
            response_data = rg.error_response_generator(400, "Invalid user uuid")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        response_data = rg.error_response_generator(400, "Please fill the form correctly")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)


# admin authenticate using email address and password
@csrf_exempt
@post_method_required
def admin_email_authentication(request):
    # Sidik classes
    db = SidikDynamoDB()
    rg = ResponseGenerator()
    sidik_jwt = SidikJWT()

    form = EmailLoginForm(request.POST)
    if form.is_valid():
        try:
            # check user email and password
            user = db.check_admin(form.cleaned_data['email'], form.cleaned_data['password'])
        except ImportError:
            response_data = rg.error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            # if the account is valid
            if user['is_valid']:
                try:
                    # create the token
                    data = {
                        "token": sidik_jwt.admin_token_generator(user['user']['user_uuid'])
                    }
                except:
                    response_data = rg.error_response_generator(500, "Internal server error")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    response_data = rg.data_response_generator(data)
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

            else:
                response_data = rg.error_response_generator(2, user["error_message"])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    else:
        response_data = rg.error_response_generator(1, "Please fill the form correctly")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

# authenticate using email address and password
# todo : implement refresh token
@csrf_exempt
@post_method_required
def email_authentication(request):

    # Sidik classes
    db = SidikDynamoDB()
    rg = ResponseGenerator()
    sidik_jwt = SidikJWT()

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
                response_data = rg.error_response_generator(1, user["error_message"])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    else:
        response_data = rg.error_response_generator(1, "Please fill the form correctly")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

@csrf_exempt
@post_method_required
def email_registration(request):

    # Sidik classes
    db = SidikDynamoDB()
    utils = SidikUtils()
    rg = ResponseGenerator()

    # TODO : Generate error response for rumah iot & error response api for rumah IoT
    try:
        form = EmailRegistrationForm(request.POST)
    # Todo : Put key checking in the form , and remove this thing
    except KeyError:
        response_data = rg.error_response_generator(500, "Internal server error")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
    else:
        # is_recaptcha_valid = utils.recaptcha_verify(request.POST.get("g_recaptcha_response", "")) g-recaptcha-response
        if form.is_valid():
            if (utils.recaptcha_verify(request.POST.get("g-recaptcha-response", ""))):
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
                        send_activation_email(email=form.cleaned_data['email'], activation_uuid=activation_uuid, full_name=form.cleaned_data['full_name'])
                        response_data = rg.success_response_generator(200, "Successfully registered please check your email for confirmation")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
                    else:
                        response_data = rg.error_response_generator(400, "Email already registered, please use another email")
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
@post_method_required
def get_user_email(request):

    # Sidik classes
    db = SidikDynamoDB()
    rg = ResponseGenerator()
    requtils = RequestUtils()

    try:
        # API Key will be called token in this context
        token = requtils.get_access_token(request)
    except KeyError:
        response_data = rg.error_response_generator(401, "Please define the authorization header")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    else:
        if token['token'] is not None:
            form = GetUserEmailForm(request.POST)
            if form.is_valid():
                # Check the API key
                if token['token'] == RUMAHIOT_SIDIK_API_KEY:
                    user = db.get_user_by_user_uuid(user_uuid=form.cleaned_data['user_uuid'])
                    if len(user) == 1:
                        data = {
                            'user_uuid': user[0]['user_uuid'],
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
            response_data = rg.error_response_generator(401, token['error'])
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)