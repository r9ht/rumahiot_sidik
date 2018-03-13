from django import forms
from django.utils.translation import ugettext_lazy as _

class EmailLoginForm(forms.Form):
    email = forms.EmailField(required=True,max_length=254)
    password = forms.CharField(required=True,max_length=128)

class EmailRegistrationForm(forms.Form):
    full_name = forms.CharField(required=True,max_length=70)
    email = forms.EmailField(required=True,max_length=254)
    password = forms.CharField(required=True,max_length=128)
    retype_password = forms.CharField(required=True, max_length=128)

    def clean(self):
        if 'password' in self.cleaned_data and 'retype_password' in self.cleaned_data and 'full_name' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['retype_password']:
                # TODO : Please do backup validation in frontend & sent the error into the view
                raise forms.ValidationError(_('Password Missmatch'))
            else:
                return self.cleaned_data
        else:
            raise forms.ValidationError(_('Invalid parameter'))

class TokenValidationForm(forms.Form):
    token = forms.CharField(required=True,max_length=500)
