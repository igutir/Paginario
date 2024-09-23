from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.db import IntegrityError, transaction

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required

from .forms import FormularioLibro, BookSearch
from .models import Libro, Usuario, Autor, Editorial, Usuario_Genero_Literario

from string import Template

import json, traceback, requests, environ, datetime


env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

def home(request):
    return render(request, "index.html")

#def register(request):
#   return render(request, "registration/register.html")

def register(request):

    data = {
        "mensaje": ""
    }

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        usuario = User()
        usuario.username = username
        usuario.set_password(password)
        usuario.email = email

        grupo_User = Group.objects.get(name="usuario")

        usuario_Paginario = Usuario()
        usuario_Paginario.nombre = username
        usuario_Paginario.email = email
        usuario_Paginario.fecha_registro = datetime.datetime.now()

        try:
            with transaction.atomic():
                usuario.save()
                usuario.groups.add(grupo_User)
                usuario_Paginario.user = usuario
                usuario_Paginario.save()

                data["mensaje"] = "Registro OK"

                usuario = authenticate(username=usuario.username, password=password)
                login(request, usuario)

                print("OK")

                return redirect(to="home")

        except Exception as ex:
            print("NOK")
            print(traceback.format_exc())

    return render(request, "registration/register.html")


def books(request):
    search = request.GET.get('search', False)

    start_index = int(request.GET.get('start', 0))  # Paginación: inicio en 0


    if not search:
        return redirect('/')

    queries = {
        'q': f'intitle:{search}',  # Solo buscar en títulos
        'key': key,
        'maxResults': 10,  # Número de resultados por página
        'startIndex': start_index  # Índice de inicio para la paginación
        }

    print(queries)
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)
    print(r)
    if r.status_code != 200:
        return render(request, 'librosbuscar.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

    data = r.json()

    if not 'items' in data:
        return render(request, 'librosbuscar.html', {'message': 'Sorry, no books match that search term.'})

    fetched_books = data['items']
    books = []
    for book in fetched_books:
        book_dict = {
            'title': book['volumeInfo']['title'],
            'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "/static/img/default-thumbnail.jpg",
            'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
            'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
            'info': book['volumeInfo']['infoLink'],
            'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0
        }
        books.append(book_dict)

    def sort_by_pop(e):
        return e['popularity']

    books.sort(reverse=True, key=sort_by_pop)


    total_items = data.get('totalItems', 0)
    next_index = start_index + 10 if start_index + 10 < total_items else None   # Calcular el índice de la próxima página

    return render(request, 'librosbuscar.html', {
        'books': books,
        'search': search,  # Mantener la búsqueda
        'next_index': next_index  # Pasar el valor para la paginación
        })

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


# Metodos para poblar la BD con ayuda de la API Google Books:

def libros_mantenedor(request):

    search = request.GET.get('search', False)

    start_index = int(request.GET.get('start', 0))  # Paginación: inicio en 0

    if not search:
        return redirect('/mantenedor/agregar_libro/')

    queries = {
        'q': f'intitle:{search}',  # Solo buscar en títulos
        'key': key,
        'maxResults': 10,  # Número de resultados por página
        'startIndex': start_index  # Índice de inicio para la paginación
        }

    print(queries)
    r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)
    print(r)
    if r.status_code != 200:
        return render(request, 'mantenedor/libro/listar_libros_api.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

    data = r.json()

    if not 'items' in data:
        return render(request, 'mantenedor/libro/listar_libros_api.html', {'message': 'Sorry, no books match that search term.'})

    fetched_books = data['items']
    libros = []
    for book in fetched_books:
        book_dict = {
            'id': book['id'],
            'nombre': book['volumeInfo']['title'],
            'descripcion': book['volumeInfo']['description'] if 'description' in book['volumeInfo'] else "",
            'anio': book['volumeInfo']['publishedDate'] if 'publishedDate' in book['volumeInfo'] else "",
            'autor': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
            'imagen': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "/static/img/default-thumbnail.jpg"
        }
        libros.append(book_dict)

    total_items = data.get('totalItems', 0)
    next_index = start_index + 10 if start_index + 10 < total_items else None   # Calcular el índice de la próxima página

    return render(request, 'mantenedor/libro/listar_libros_api.html', {
        'libros': libros,
        'search': search,  # Mantener la búsqueda
        'next_index': next_index  # Pasar el valor para la paginación
    })

def guardar_libro(request, id_libro):

    GOOGLE_BOOKS_API_URL_BY_ID = "https://www.googleapis.com/books/v1/volumes/"

    url = f"{GOOGLE_BOOKS_API_URL_BY_ID}{id_libro}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "volumeInfo" in data:
            libro_info = data['volumeInfo']

            autor=", ".join(libro_info.get('authors', []))

            autor_libro, created = Autor.objects.get_or_create(
                nombre= autor,
            )

            año = datetime.datetime.strptime(libro_info.get('publishedDate'), '%Y-%m-%d')

            editorial = Editorial.objects.get(nombre="Otra")

            try:
                libro = Libro(
                    id=id_libro,
                    nombre=libro_info.get('title'),
                    descripcion=libro_info.get('description', ''),
                    anio=año.year,
                    portada=libro_info['imageLinks'].get('thumbnail') if 'imageLinks' in libro_info else "/static/img/default-thumbnail.jpg",
                    id_editorial=editorial,
                    id_autor=autor_libro
                )

                libro.save()

                print("OK")

                return redirect(to="agregar_libro")

            except Exception as ex:
                print("NOK")
                print(traceback.format_exc())

    return render(request, "mantenedor/libro/agregar.html")

