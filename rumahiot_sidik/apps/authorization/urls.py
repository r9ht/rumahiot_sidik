"""rumahiot_sidik URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url

from rumahiot_sidik.apps.authorization.views import token_validation, email_activation, change_password, forgot_password, confirm_forgot_password

urlpatterns = [
    url(r'^token/validate$', token_validation, name='token_validation'),
    url(r'^email/activate/(?P<activation_uuid>.+)$', email_activation, name='email_activation'),
    url(r'^password/change$', change_password, name='change_password'),
    url(r'^password/forgot$', forgot_password, name='forgot_password'),
    url(r'^password/forgot/confirm/$', confirm_forgot_password, name='confirm_forgot_password'),


]
