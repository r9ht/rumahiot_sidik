from django import forms


# todo : check all of the max_length
class TokenValidationForm(forms.Form):
    token = forms.CharField(required=True,max_length=500)
    # 1 for true , 0 for false
    email = forms.CharField(required=True,max_length=1)

    def clean(self):
        if 'email' in self.cleaned_data:
            if self.cleaned_data['email'] == "1" or self.cleaned_data['email'] == "0":
                return self.cleaned_data
            else:
                raise forms.ValidationError('Invalid parameter')

class DeviceKeyValidationForm(forms.Form):
    device_key = forms.CharField(required=True,max_length=500)
    # r for read key, w for write key
    key_type = forms.CharField(required=True,max_length=1)

class DeviceKeyRefreshForm(forms.Form):
    device_uuid = forms.CharField(required=True,max_length=500)

