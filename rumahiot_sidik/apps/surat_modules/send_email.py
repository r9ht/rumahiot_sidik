# Consist of class and methods for accessing surat endpoint
import requests

from rumahiot_sidik.settings import RUMAHIOT_SURAT_API_KEY, RUMAHIOT_SURAT_SEND_EMAIL_ACTIVATION_ENDPOINT, \
    RUMAHIOT_SURAT_SEND_WELCOME_EMAIL_ENDPOINT


class SidikSuratModule:

    # Send activation email to specified email
    # Input parameter (email (string), activation_uuid (string)
    # Output parameter (data: {message (string), activation_uuid (string), email (string)})
    def send_activation_email(self, email, activation_uuid):
        header = {
            'Authorization': 'Bearer {}'.format(RUMAHIOT_SURAT_API_KEY)
        }
        payload = {
            'email': email,
            'activation_uuid': activation_uuid
        }
        response = requests.post(url=RUMAHIOT_SURAT_SEND_EMAIL_ACTIVATION_ENDPOINT, headers=header, data=payload)
        return response

    # Send welcome email to specified email
    # Input parameter (email (string)
    # Output parameter (data: {message (string), email (string)})
    def send_welcome_email(self, email):
        header = {
            'Authorization': 'Bearer {}'.format(RUMAHIOT_SURAT_API_KEY)
        }
        payload = {
            'email': email,
        }
        response = requests.post(url=RUMAHIOT_SURAT_SEND_WELCOME_EMAIL_ENDPOINT, headers=header, data=payload)
        return response
