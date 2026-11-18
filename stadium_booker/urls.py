from django.urls import path
from .views import *

urlpatterns = [
    path('', home_page, name='home'),
    path('registration/', register, name='registration'),
    path('login/', login_user, 'login')
]
