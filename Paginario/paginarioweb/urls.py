from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home
#from .views import log
from .views import books
from .views import vista_libro
from .views import register
from .views import *

from . import views

urlpatterns = [
    # path('', home, name='home'),
    path('', auth_views.LoginView.as_view(), name='login'),
    path('home/', home, name='home'),
    path('register/', register, name='register'),
    path('libro/<id_libro>', vista_libro, name='vista_libro'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('librosbuscar/', books, name='librosbuscar'),

    # Actualización del estado del libro
    path('libro/<id_libro>/<estado>/', set_estado_libro, name='set_estado_libro'),

    #Listas:
    path('libro/<id_libro>/f/', agregar_favorito, name='agregar_favorito'),

    #Reporteria
    path('usuarios-mes/', views.obtener_usuarios_mes, name='obtener_usuarios_mes'),

    # Mantenedor de Administradores:
    path('j/<int:id>/', libro, name="libro"),
    path('mantenedor/', mantenedor_libros, name="mantenedor_libros"),
    path('mantenedor/agregar_libro/', agregar_libro, name="agregar_libro"),
    path('mantenedor/agregar_libro/listar_libros_api/', libros_mantenedor, name="libros_mantenedor"),
    path('mantenedor/agregar_libro/listar_libros_api/g/<id_libro>', guardar_libro, name="guardar_libro"),
    path('mantenedor/listado_libros/', modificar_libro_lista, name="modificar_libro_lista"),
    path('mantenedor/listado_libros/u/<idlibro>/', modificar_libro, name="modificar_libro"),
    path('mantenedor/listado_libros/d/<idlibro>/', eliminar_libro, name="eliminar_libro"),
]
