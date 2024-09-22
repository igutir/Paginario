from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home
from .views import log
from .views import books
from .views import libro, mantenedor_libros, agregar_libro, modificar_libro_lista, modificar_libro, eliminar_libro, libros_mantenedor

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('log/', log, name='log'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('librosbuscar/', books, name='librosbuscar'),



    # Mantenedor de Administradores:
    path('j/<int:id>/', libro, name="libro"),
    path('mantenedor/', mantenedor_libros, name="mantenedor_libros"),
    path('mantenedor/agregar_libro/', agregar_libro, name="agregar_libro"),
    path('mantenedor/agregar_libro/listado_libros_api/', libros_mantenedor, name="libros_mantenedor"),
    path('mantenedor/listado_libros/', modificar_libro_lista, name="modificar_libro_lista"),
    path('mantenedor/listado_libros/u/<int:idlibro>/', modificar_libro, name="modificar_libro"),
    path('mantenedor/listado_libros/d/<idlibro>/', eliminar_libro, name="eliminar_libro"),
]
