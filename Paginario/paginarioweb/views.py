from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from .forms import FomrularioLibro, BookSearch
from .models import Libro

from string import Template

import requests
import environ

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')

def home(request):
    return render(request, "index.html")

def base(request):
    return render(request, "base.html")

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


#def books(request):

    author = request.GET.get('author', False)
    search = author if request.GET.get(
        'search', False) == "" else request.GET.get('search', False)

    if (search == False and author == False) or (search == "" and author == ""):
        return redirect('/')

    queries = {'q': search, 'inauthor': author, 'key': key}
    print(queries)
    r = requests.get(
        'https://www.googleapis.com/books/v1/volumes', params=queries)
    print(r)
    if r.status_code != 200:
        return render(request, 'paginarioweb/librosbuscar.html', {'message': 'Sorry, there seems to be an issue with Google Books right now.'})

    data = r.json()

    if not 'items' in data:
        return render(request, 'paginarioweb/librosbuscar.html', {'message': 'Sorry, no books match that search term.'})

    fetched_books = data['items']
    books = []
    for book in fetched_books:
        book_dict = {
            'title': book['volumeInfo']['title'],
            'image': book['volumeInfo']['imageLinks']['thumbnail'] if 'imageLinks' in book['volumeInfo'] else "",
            'authors': ", ".join(book['volumeInfo']['authors']) if 'authors' in book['volumeInfo'] else "",
            'publisher': book['volumeInfo']['publisher'] if 'publisher' in book['volumeInfo'] else "",
            'info': book['volumeInfo']['infoLink'],
            'popularity': book['volumeInfo']['ratingsCount'] if 'ratingsCount' in book['volumeInfo'] else 0
        }
        books.append(book_dict)

    def sort_by_pop(e):
        return e['popularity']

    books.sort(reverse=True, key=sort_by_pop)

    return render(request, 'paginarioweb/librosbuscar.html', {'books': books})

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
