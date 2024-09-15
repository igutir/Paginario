from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .forms import FomrularioLibro
from .models import Libro

def home(request):
    return render(request, "index.html")


def base(request):
    return render(request, "base.html")



def libro(request, id):

    libro = get_object_or_404(Libro, id = id)

    data = {
        'libro' : libro
    }

    return render(request, "libro.html", data)

## Mantenedor de libros:
"""
## Permisos en base a lo otorgado al perfil de administrador en el panel de administrador
@login_required(login_url = "login/")
@permission_required(['Paginario.add_libro', 'Paginario.delete_libro'], login_url = "login/")
"""
def mantenedor_libros(request):

    return render(request, "mantenedor/libro/mantenedor_libros.html")

"""
## Permisos en base a lo otorgado al perfil de administrador en el panel de administrador
@login_required(login_url = "login/")
@permission_required(['Paginario.add_libro'], login_url = "login/")
"""
def agregar_libro(request):

    data = {
        "form_libro": FomrularioLibro,
        "mensaje": ""
    }

    if request.method == "POST":
        formulario = FomrularioLibro(data = request.POST, files = request.FILES)

        if formulario.is_valid:
            formulario.save()
            data["mensaje"] = "Libro agregado"
        else:
            data["mensaje"] = "Error"
            data["form"] = formulario

    return render(request, "mantenedor/libro/agregar.html", data)
"""
@login_required(login_url = "login/")
@permission_required(['Paginario.change_libro', 'Paginario.delete_libro'], login_url = "login/")
"""
def modificar_libro_lista(request):

    libros = Libro.objects.all()

    data = {
        'libros' : libros
    }

    return render(request, "mantenedor/libro/listado_libros.html", data)

"""
@login_required(login_url = "login/")
@permission_required(['Paginario.change_libro'], login_url = "login/")
"""
def modificar_libro(request, idlibro):

    libro = get_object_or_404(Libro, id = idlibro)

    data = {
        "form_libro": FomrularioLibro(instance = libro)
    }

    if request.method == "POST":
        formulario = FomrularioLibro(data = request.POST, instance = libro, files = request.FILES)

        if formulario.is_valid:
            formulario.save()
            return redirect(to="modificar_libro_lista")
        else:
            data["mensaje"] = "Error"
            data["form"] = formulario

    return render(request, "mantenedor/libro/modificar.html", data)

"""
@login_required(login_url="login/")
@permission_required(['Paginario.delete_libro'], login_url = "login/")
"""
def eliminar_libro(idlibro):

    libro = get_object_or_404(Libro, id = idlibro)

    libro.delete()

    return redirect(to = "modificar_libro_lista")