from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Estado_Libro)
admin.site.register(Genero_Literario)
admin.site.register(Autor)
admin.site.register(Editorial)
admin.site.register(Libro)
admin.site.register(Lista)
admin.site.register(Usuario_Libro)
admin.site.register(Libro_Genero_Literario)
admin.site.register(Usuario_Genero_Literario)