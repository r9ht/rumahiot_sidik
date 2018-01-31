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
from rumahiot_sidik.apps.authorization.views import token_validation

urlpatterns = [
    url(r'^token/validate$', token_validation,name='token_validation' ),
    url(r'^writekey/validate$', token_validation,name='writekey_validation' ),
    url(r'^readkey/validate$', token_validation,name='readkey_validation' ),
    url(r'^writekey/refresh$', token_validation,name='refresh_writekey' ),
    url(r'^readkey/refresh$', token_validation,name='refresh_readkey' ),

]
