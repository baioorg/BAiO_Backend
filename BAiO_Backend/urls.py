"""
URL configuration for BAiO_Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from userAuth.views import Info, Authentication, Register

urlpatterns = [
    path("admin/", admin.site.urls),

    # User Urls?
    path("user/info/",  Info.as_view()),
    path("user/auth/", Authentication.as_view()),
    path("user/register/", Register.as_view(), name="register_new_user"),

    
]


