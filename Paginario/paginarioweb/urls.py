from django.urls import path
from .views import home
from .views import base
from .views import books

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('base/', base, name='base'),
    path('librosbuscar/', books, name='librosbuscar'),
]
