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

from rumahiot_sidik.apps.authentication.views import email_authentication, email_registration, get_user_email, admin_email_authentication

urlpatterns = [
    url(r'^email$', email_authentication, name='email_authentication'),
    url(r'^admin/email$', admin_email_authentication, name='admin_email_authentication'),
    url(r'^email/register$', email_registration, name='email_registration'),
    # This url resource can be accessed by authorized service only (With API Key)
    # Get user email address from user_uuid
    url(r'^email/get$', get_user_email, name='get_user_email'),
]
