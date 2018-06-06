# Consist of methods for accessing surat endpoint
# Move to method instead, because methods inside class is not supported by zappa async yet

import requests
from zappa.async import task

from rumahiot_sidik.settings import RUMAHIOT_SURAT_API_KEY, \
    RUMAHIOT_SURAT_SEND_EMAIL_ACTIVATION_ENDPOINT, \
    RUMAHIOT_SURAT_SEND_WELCOME_EMAIL_ENDPOINT, \
    RUMAHIOT_SURAT_SEND_FORGOT_PASSWORD_EMAIL_ENDPOINT

# Send activation email to specified email
# Input parameter (email (string), activation_uuid (string)
# Output parameter (data: {message (string), activation_uuid (string), email (string)})
@task
def send_activation_email(email, activation_uuid, full_name):
    header = {
        'Authorization': 'Bearer {}'.format(RUMAHIOT_SURAT_API_KEY)
    }
    payload = {
        'email': email,
        'activation_uuid': activation_uuid,
        'full_name': full_name
    }
    response = requests.post(url=RUMAHIOT_SURAT_SEND_EMAIL_ACTIVATION_ENDPOINT, headers=header, data=payload)
    return response

@task
def send_forgot_password_email(email, forgot_password_uuid, full_name):
    header = {
        'Authorization': 'Bearer {}'.format(RUMAHIOT_SURAT_API_KEY)
    }
    payload = {
        'email': email,
        'forgot_password_uuid': forgot_password_uuid,
        'full_name': full_name
    }
    response = requests.post(url=RUMAHIOT_SURAT_SEND_FORGOT_PASSWORD_EMAIL_ENDPOINT, headers=header, data=payload)
    return response

# Send welcome email to specified email
# Input parameter (email (string)
# Output parameter (data: {message (string), email (string)})
@task
def send_welcome_email(email, full_name):
    header = {
        'Authorization': 'Bearer {}'.format(RUMAHIOT_SURAT_API_KEY)
    }
    payload = {
        'email': email,
        'full_name': full_name
    }
    response = requests.post(url=RUMAHIOT_SURAT_SEND_WELCOME_EMAIL_ENDPOINT, headers=header, data=payload)
    return response

