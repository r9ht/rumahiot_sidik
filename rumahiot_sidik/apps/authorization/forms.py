from django import forms

class TokenValidationForm(forms.Form):
    token = forms.CharField(required=True,max_length=500)