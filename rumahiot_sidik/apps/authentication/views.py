from django.shortcuts import render,HttpResponse
from rumahiot_sidik.apps.authentication.jwt import token_generator
from rumahiot_sidik.apps.authentication.utils import error_response_generator,data_response_generator,success_response_generator
from django.views.decorators.csrf import csrf_exempt
from rumahiot_sidik.apps.authentication.dynamodb import user_get_by_email,create_user_by_email
import json,requests,os
from rumahiot_sidik.apps.authentication.forms import EmailLoginForm,EmailRegistrationForm,TokenValidationForm

# functions

def recaptcha_verify(captcha_response):
    # dont forget to put the secret in environment instead
    # return value recaptcha response : boolean

    recaptcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"

    post_data = {
        'secret' : os.environ.get('RECAPTCHA_SECRET_KEY',''),
        'response' : str(captcha_response),
    }

    post_response = requests.post(recaptcha_verify_url,data=post_data)
    post_response = post_response.json()

    if str(post_response['success']) == "True":
        return True
    else:
        return False


# Create your views here.

# authenticate using email address and password
# todo : implement refresh token
@csrf_exempt
def email_authentication(request):
    if request.method != "POST":
        response_data = error_response_generator(400,"Bad request method")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            try:
                # check user email and password
                user = user_get_by_email(form.cleaned_data['email'],form.cleaned_data['password'])
            except ImportError:
                response_data = error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
            else:
                # if the account is valid
                if user['is_valid']:
                    try:
                        # create the token
                        data = {
                            "token" : token_generator(user['user']['user_uuid'])
                        }
                    except:
                        response_data = error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                    else:
                        response_data = data_response_generator(data)
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

                else:
                    response_data = error_response_generator(400, user["error_message"])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            # if the request parameter isn't complete
            response_data = error_response_generator(400, "One of the request inputs is not valid.")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

@csrf_exempt
def email_registration(request):
    if request.method != 'POST' :
        response_data = error_response_generator(400, 'Invalid request method')
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        # TODO : Generate error response for rumah iot & error response api for rumah IoT
        try:
            form = EmailRegistrationForm(request.POST)
        except KeyError:
            response_data = error_response_generator(500, "Internal server error")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
        else:
            is_recaptcha_valid = recaptcha_verify(request.POST.get("g-recaptcha-response", ""))
            if form.is_valid():
                if is_recaptcha_valid:
                    create_success = create_user_by_email(form.cleaned_data['full_name'],form.cleaned_data['email'], form.cleaned_data['password'])
                    # If dynamodb returning unknown error
                    if create_success:
                        response_data = success_response_generator(200,"User successfully registered")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)
                    else:
                        response_data = error_response_generator(400, "User already exist")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                else:
                    # if the recaptcha isn't valid
                    response_data = error_response_generator(400, "Please complete the Recaptcha")
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)

            else:
                # Todo : push the error from form to here , change the error type
                response_data = error_response_generator(400,"Missmatch password or invalid parameter submitted")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)




