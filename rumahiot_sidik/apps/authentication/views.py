from django.shortcuts import render,HttpResponse
from rumahiot_sidik.apps.authentication.dynamodb import user_check_by_email,create_jwt_token
from rumahiot_sidik.apps.authentication.utils import error_response_generator,data_response_generator
from rumahiot_sidik.apps.authentication.resources import EmailAuthenticationRequest
from django.views.decorators.csrf import csrf_exempt
import json
from throttle.decorators import throttle


# Create your views here.

# authenticate using email address and password
# max : 60 request every minute for the same ip address
# TODO : Fix ElastiCache
@csrf_exempt
@throttle(zone='email_authentication')
def email_authentication(request):
    if request.method != "POST":
        response_data = error_response_generator(400,"Bad request method")
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
    else:
        try:
            j = json.loads(request.body)
            req = EmailAuthenticationRequest(**j)
        except TypeError:
            # if the request parameter isn't complete
            response_data = error_response_generator(400,"One of the request inputs is not valid.")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        except ValueError:
            # if the JSON is malformed
            response_data = error_response_generator(400,"Malformed JSON")
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)
        else:
            try:
                # check user email and password
                user = user_check_by_email(req.email,req.password)
            except:
                response_data = error_response_generator(500, "Internal server error")
                return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
            else:
                # if the account is valid
                if user['is_valid']:
                    try:
                        # create the token
                        data = create_jwt_token(user['user']['uuid'])
                    except:
                        response_data = error_response_generator(500, "Internal server error")
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=500)
                    else:
                        response_data = data_response_generator(data)
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

                else:
                    response_data = error_response_generator(400, user["error_message"])
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)




