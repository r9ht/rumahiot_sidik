from django import forms


# todo : check all of the max_length
class TokenValidationForm(forms.Form):
    token = forms.CharField(required=True,max_length=500)

class DeviceKeyValidationForm(forms.Form):
    device_key = forms.CharField(required=True,max_length=500)
    # r for read key, w for write key
    key_type = forms.CharField(required=True,max_length=1)

class DeviceKeyRefreshForm(forms.Form):
    device_uuid = forms.CharField(required=True,max_length=500)

