
from django.urls import path
from dj_rest_auth.views import LoginView

urlpatterns = [
    path('login', LoginView.as_view(), name='login')

]