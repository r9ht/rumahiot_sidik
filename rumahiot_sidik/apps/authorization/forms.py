from django import forms
from django.utils.translation import ugettext_lazy as _

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
                raise forms.ValidationError(_('Invalid parameter'))

class DeviceKeyValidationForm(forms.Form):
    device_key = forms.CharField(required=True,max_length=500)
    # r for read key, w for write key
    key_type = forms.CharField(required=True,max_length=1)

class DeviceKeyRefreshForm(forms.Form):
    device_uuid = forms.CharField(required=True,max_length=500)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True, max_length=128)
    new_password = forms.CharField(required=True, max_length=128)
    new_password_retype = forms.CharField(required=True, max_length=128)

    def clean(self):
        if 'new_password' in self.cleaned_data and 'new_password_retype' in self.cleaned_data:
            if self.cleaned_data['new_password'] != self.cleaned_data['new_password_retype']:
                raise forms.ValidationError(_('Password missmatch'))
            else:
                return self.cleaned_data