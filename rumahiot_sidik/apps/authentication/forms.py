from django import forms

class EmailLoginForm(forms.Form):
    email = forms.EmailField(required=True,max_length=120)
    password = forms.CharField(required=True,max_length=120)

class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(required=True,max_length=120)
    password = forms.CharField(required=True,max_length=120)
    retype_password = forms.CharField(required=True, max_length=120)

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['retype_password']:
            # TODO : Please do backup validation in frontend
            raise forms.ValidationError('Password Missmatch')
        else:
            return self.cleaned_data

