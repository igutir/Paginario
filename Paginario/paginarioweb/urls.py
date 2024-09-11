from django.urls import path
from .views import home
from .views import base

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('base/', base, name='base'),
]
