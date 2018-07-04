import json
from uuid import uuid4

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rumahiot_sidik.apps.authentication.dynamodb import SidikDynamoDB
from rumahiot_sidik.apps.authentication.jwt import SidikJWT
from rumahiot_sidik.apps.authentication.utils import SidikUtils, ResponseGenerator, RequestUtils
from rumahiot_sidik.apps.authorization.forms import TokenValidationForm, ChangePasswordForm, ForgotPasswordForm, ConfirmForgotPasswordForm
from rumahiot_sidik.apps.surat_modules.send_email import send_activation_email, send_welcome_email, send_forgot_password_email

from rumahiot_sidik.apps.authentication.decorator import get_method_required, post_method_required


# Create your views here.
# Todo : Protect this endpoint with key

# Validate token that sent , returning user_uuid and other data based on the request
@csrf_exempt
@post_method_required
def token_validation(request):

    # Sidik classes
    jwt = SidikJWT()
    rg = ResponseGenerator()
    db = SidikDynamoDB()

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
                response_data = rg.error_response_generator(401, result['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
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
@get_method_required
def email_activation(request, activation_uuid):

    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()

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
                # Get user profile
                profile = db.get_user_profile_data(user_uuid=user[0]['user_uuid'])
                # Send welcome email
                send_welcome_email(email=user[0]['email'], full_name=profile[0]['full_name'])
                response_data = rg.success_response_generator(200, "Your account has been activated")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

        else:
            # account already activated
            response_data = rg.error_response_generator(400, 'Activation UUID does not valid or exist')
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

    else:
        response_data = rg.error_response_generator(400, 'Invalid email activation request')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

@csrf_exempt
@post_method_required
def change_password(request):
    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()
    su = SidikUtils()
    requtils = RequestUtils()
    jwt = SidikJWT()

    try:
        token = requtils.get_access_token(request)
    except KeyError:
        response_data = rg.error_response_generator(401, "Please define the authorization header")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
    else:
        if token['token'] is not None:
            data = jwt.token_validator(token['token'])
            if data['payload'] != None:
                form = ChangePasswordForm(request.POST)
                if form.is_valid():
                    user = db.get_user_by_user_uuid(data['payload']['user_uuid'])
                    # check for unknown error
                    if len(user) != 0:
                        hashed_old_password = su.password_hasher(salt=user[0]['salt'], password=form.cleaned_data['old_password'])
                        # Check if the old password match
                        if hashed_old_password == user[0]['password']:
                            try:
                                db.change_user_password(user_uuid=user[0]['user_uuid'], new_password=form.cleaned_data['new_password'])
                            except:
                                # Catch unknown client error
                                response_data = rg.error_response_generator(500, "Internal server error")
                                return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                            else:
                                response_data = rg.success_response_generator(200, "Your password successfully changed")
                                return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
                        else:
                            response_data = rg.error_response_generator(400, "Incorrect old password")
                            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
                    else:
                        # unknown client error
                        response_data = rg.error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    # Todo : push the error from form to here , change the error type
                    response_data = rg.error_response_generator(400, "Missmatch password or invalid parameter submitted")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
            else:
                response_data = rg.error_response_generator(401, data['error'])
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)
        else:
            response_data = rg.error_response_generator(401, token['error'])
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=401)

@csrf_exempt
@post_method_required
def forgot_password(request):

    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()
    utils = SidikUtils()

    form = ForgotPasswordForm(request.POST)
    if (utils.recaptcha_verify(request.POST.get("g-recaptcha-response", ""))):
        if form.is_valid():
            # Check the mail
            user = db.get_user_by_email(email=form.cleaned_data['email'])
            if len(user) != 0:
                forgot_password_uuid = uuid4().hex
                # Invalidate existing forgor password request
                forgot_requests = db.get_user_forgot_password_request(user_uuid=user[0]['user_uuid'])
                for forgot_request in forgot_requests:
                    db.invalidate_forgot_password_request(forgot_request['forgot_password_uuid'])
                # Put new request
                try:
                    db.create_forgot_password_request(user_uuid=user[0]['user_uuid'], forgot_password_uuid=forgot_password_uuid)
                except:
                    # unknown client error
                    response_data = rg.error_response_generator(500, "Internal server error")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    # Get user profile
                    profile = db.get_user_profile_data(user_uuid=user[0]['user_uuid'])
                    # Send the email
                    send_forgot_password_email(email=user[0]['email'], forgot_password_uuid=forgot_password_uuid, full_name=profile[0]['full_name'])
                    response_data = rg.success_response_generator(200, "If a RumahIoT account exists for {}, an e-mail will be sent with further instructions.".format(form.cleaned_data['email']))
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
            else:
                response_data = rg.success_response_generator(200, "If a RumahIoT account exists for {}, an e-mail will be sent with further instructions.".format(form.cleaned_data['email']))
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
        else:
            response_data = rg.error_response_generator(400, "Invalid or missing parameter submitted")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        # if the recaptcha isn't valid
        response_data = rg.error_response_generator(400, "Please complete the Recaptcha")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

@csrf_exempt
@post_method_required
def confirm_forgot_password(request):

    # Sidik classes
    rg = ResponseGenerator()
    db = SidikDynamoDB()

    form = ConfirmForgotPasswordForm(request.POST)
    if form.is_valid():
        forgot_password_request = db.get_forgot_password_request(forgot_password_uuid=form.cleaned_data['forgot_password_uuid'])
        # Verify the forgot_request_uuid
        if len(forgot_password_request) == 1:
            # Change the password
            try:
                db.change_user_password(user_uuid=forgot_password_request[0]['user_uuid'], new_password=form.cleaned_data['new_password_retype'])
            except:
                # Catch unknown client error
                response_data = rg.error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
            else:
                try:
                    db.invalidate_forgot_password_request(forgot_password_uuid=form.cleaned_data['forgot_password_uuid'])
                except:
                    # Catch unknown client error
                    response_data = rg.error_response_generator(500, "Internal server error")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    response_data = rg.success_response_generator(200, "Your password successfully resetted")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
        else:
            response_data = rg.error_response_generator(400, 'Invalid forgot password request')
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        response_data = rg.error_response_generator(400, "Invalid or missing parameter submitted")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)



