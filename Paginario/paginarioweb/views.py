from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404
from django.db import IntegrityError, transaction, connection

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required

from .forms import FormularioLibro, BookSearch
from .models import Libro, Usuario, Autor, Editorial, Lista, Estado_Libro, Usuario_Libro, Usuario_Genero_Literario

from django.core.exceptions import ObjectDoesNotExist

from string import Template

import json, traceback, requests, environ, datetime

from django.conf import settings
import cx_Oracle

env = environ.Env()
env.read_env()  # reading .env file

key = env.str('API_KEY')


# Vista principal
def home(request):

    libros = Libro.objects.all()
    top_libros = obtener_top_libros() # Obtener los top libros

    context = {
        "libros": libros,
        "top_libros": top_libros  # Agregar los libros top al contexto
    }

    return render(request, "index.html", context)


def obtener_usuario_actual(request):

    user_actual = request.user
    usuario = get_object_or_404(Usuario, user_id=user_actual.id)

    return Usuario.objects.get(nombre=usuario)

#Vista de para el libro según id
def vista_libro(request, id_libro):

    usuario = obtener_usuario_actual(request)

    libro = get_object_or_404(Libro, id=id_libro)

    estado_libro = obtener_estado_libro(id_libro, usuario.id)

    calificacion_libro = obtener_calificacion_libro(id_libro, usuario.id)

    reseñas = obtener_reseñas(request, id_libro)

    data = {
        "libro" : libro,
        "estado_libro": estado_libro,
        "calificacion": calificacion_libro,
        "reseñas": reseñas
    }

    return render(request, "libro.html", data)

# Cambio del estado del libro
def poner_estado_libro(request, id_libro, estado):

    usuario = obtener_usuario_actual(request)

    libro = get_object_or_404(Libro, id=id_libro)

    nombre_estado = ""

    match estado:
        case "progreso":
            nombre_estado = "En progreso"
        case "espera":
            nombre_estado = "En espera"
        case "leido":
            nombre_estado = "Leido"
        case _:
            nombre_estado = ""

    estado_libro = get_object_or_404(Estado_Libro, nombre=nombre_estado)

    data = {
            "libro": libro,
            "mensaje": ""
        }

    usuario_libro, creado = Usuario_Libro.objects.update_or_create(
        id_usuario=usuario,
        id_libro=libro
        )

    usuario_libro.id_estado_libro = estado_libro

    usuario_libro.save()

    data["mensaje"] = "Estado del libro cambiado a " + estado_libro.nombre

    print(traceback.format_exc())

    return redirect(to = "/libro/"+id_libro)

# Obtener estado del libro para mostrarlo en el front
def obtener_estado_libro(id_libro, id_usuario):

    try:

        usuario_libro = Usuario_Libro.objects.get(id_libro=id_libro, id_usuario=id_usuario)

    except Usuario_Libro.DoesNotExist:

        return "None"

    if usuario_libro.id_estado_libro is None:

        return "None"

    else:

        return usuario_libro.id_estado_libro.nombre

# Agregar calificación al libro
def poner_calificacion(request, id_libro, rating):

    usuario = obtener_usuario_actual(request)

    libro = get_object_or_404(Libro, id=id_libro)

    data = {
            "libro": libro,
            "mensaje": ""
        }

    usuario_libro, creado = Usuario_Libro.objects.update_or_create(
        id_usuario=usuario,
        id_libro=libro
        )

    usuario_libro.calificacion = rating

    usuario_libro.save()

    if rating == 1:
        data["mensaje"] = "Calificación del libro cambiado a " + str(rating) + " estrella."
    else:
        data["mensaje"] = "Calificación del libro cambiado a " + str(rating) + " estrellas."

    return redirect(to = "/libro/"+id_libro)

# Obtener calificacion del libro para mostrarlo en el front
def obtener_calificacion_libro(id_libro, id_usuario):

    calificacion = 0

    try:
        calificacion = get_object_or_404(Usuario_Libro, id_libro=id_libro, id_usuario=id_usuario).calificacion

    except Http404:
        calificacion = 0

    return calificacion


def agregar_reseña(request, id_libro):

    if request.method == 'POST':

        reseña = request.POST.get('textoReseña')

        usuario = obtener_usuario_actual(request)

        libro = get_object_or_404(Libro, id=id_libro)

        data = {
                "libro": libro,
                "mensaje": ""
            }

        usuario_libro, creado = Usuario_Libro.objects.update_or_create(
            id_usuario=usuario,
            id_libro=libro
            )

        usuario_libro.resenia = reseña

        usuario_libro.save()

        data["mensaje"] = "La reseña ha sido añadida"

    return redirect(to = "/libro/"+id_libro)

# Obtener reseña del usuario actual
def obtener_reseña_usuario(id_libro, id_usuario):


    try:
        reseña = get_object_or_404(Usuario_Libro, id_libro=id_libro, id_usuario=id_usuario).resenia
        

    except Http404:

        reseña = ""

    return reseña

# Obtener todas las reseñas del libro actual
def obtener_reseñas(request, id_libro):

    reseñas = Usuario_Libro.objects.filter(id_libro=id_libro).values_list('resenia', flat=True).order_by('-id')
    conteo_resenias = reseñas.filter(resenia__isnull=False).count()

    data = {
        'resenias' : reseñas,
        'conteo_resenias': conteo_resenias,
    }

    return render(request, "mantenedor/libro/listado_libros.html", data)

# Método para registrar un nuevo usuario al sistema
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

# Método para la búsqueda de libros mediante la API Google Books en la homepage
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

## Permisos en base a lo otorgado al perfil de administrador en el panel de administrador
""" @login_required(login_url = "login/")
@permission_required(['Paginario.add_libro', 'Paginario.delete_libro'], login_url = "login/") """
def mantenedor_libros(request):

    return render(request, "mantenedor/libro/mantenedor_libros.html")

"""
## Permisos en base a lo otorgado al perfil de administrador en el panel de administrador
@login_required(login_url = "login/")
@permission_required(['Paginario.add_libro'], login_url = "login/")
"""
def agregar_libro(request):

    data = {
        "form_libro": FormularioLibro,
        "mensaje": ""
    }

    if request.method == "POST":
        formulario = FormularioLibro(data = request.POST, files = request.FILES)

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
        "form_libro": FormularioLibro(instance = libro)
    }

    if request.method == "POST":
        formulario = FormularioLibro(data = request.POST, instance = libro, files = request.FILES)

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
def eliminar_libro(request, idlibro):

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

    r = requests.get('https://www.googleapis.com/books/v1/volumes', params=queries)

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

    param = {
        'key': key
        }

    response = requests.get("https://www.googleapis.com/books/v1/volumes/" + id_libro, params=param)

    if response.status_code == 200:
        data = response.json()

        if "volumeInfo" in data:
            libro_info = data['volumeInfo']

            autor=", ".join(libro_info.get('authors', []))

            autor_libro, created = Autor.objects.get_or_create(
                nombre= autor,
            )

            fecha = libro_info.get('publishedDate')

            if len(fecha) == 4:
                fecha = fecha + "-01-01"
            elif len(fecha) == 7:
                fecha = fecha + "-01"

            año = datetime.datetime.strptime(fecha, '%Y-%m-%d')

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

                return redirect(to="agregar_libro")

            except Exception as ex:
                print("NOK")
                print(traceback.format_exc())
        else:
            print("No data")

    return render(request, "mantenedor/libro/listar_libros_api.html")

## Agregar libro a la lista de favoritos
def agregar_favorito(request, id_libro):

    user_actual = request.user

    libro = get_object_or_404(Libro, id=id_libro)

    usuario = get_object_or_404(Usuario, user_id=user_actual.id)
    usuario = Usuario.objects.get(nombre=usuario)

    data = {
            "libro": libro,
            "mensaje": ""
        }

    Lista_favoritos, creado = Lista.objects.get_or_create(nombre="Favoritos", id_usuario=usuario, id_libro=libro)

    if creado:
        data["mensaje"] = "Libro agregado a la lista de favoritos"
    else:
        data["mensaje"] = "Este libro ya existe en tu lista de favoritos"

    return render(request, "libro.html", data)

# Reportería:
def obtener_usuarios_mes(request):
    mes = request.GET.get('mes', datetime.datetime.now().month)  # Mes actual por defecto
    ano = request.GET.get('ano', datetime.datetime.now().year)  # Año actual por defecto

    # Validar que mes y año sean enteros
    try:
        mes = int(mes)
        ano = int(ano)
    except ValueError:
        mes = datetime.datetime.now().month
        ano = datetime.datetime.now().year

    # Ejecutar el procedimiento o consulta SQL con los parámetros
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ID, NOMBRE, EMAIL, TO_CHAR(FECHA_REGISTRO, 'DD/MM/YYYY'), USER_ID
            FROM usuario
            WHERE EXTRACT(YEAR FROM FECHA_REGISTRO) = %s
              AND EXTRACT(MONTH FROM FECHA_REGISTRO) = %s
        """, [ano, mes])
        rows = cursor.fetchall()

    # datos para el template
    usuarios = [{'id': row[0], 'nombre': row[1], 'email': row[2], 'fecha_registro': row[3], 'user_id': row[4]} for row in rows]

    current_year = datetime.datetime.now().year
    years = list(range(current_year - 2, current_year + 1))

    return render(request, 'usuarios_mes.html', {'usuarios': usuarios, 'years': years})

# Muestra el top 10 de calificaciones de los libros
def obtener_top_libros():
    # Crear un cursor y una conexión a la base de datos
    connection = cx_Oracle.connect(settings.DATABASES['default']['USER'],
                                    settings.DATABASES['default']['PASSWORD'],
                                    settings.DATABASES['default']['NAME'])
    cursor = connection.cursor()
    
    # Llamar al procedimiento
    try:
        p_top_libros = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('obtener_top_libros_mejor_calificados', [p_top_libros])
        
        # Recuperar los resultados
        top_libros = p_top_libros.getvalue().fetchall()

        # Convertir a lista de diccionarios
        resultados = []
        for libro in top_libros:
            resultados.append({
                'id_libro': libro[0],              
                'promedio_calificacion': libro[1], 
                'total_resenas': libro[2]          
            })
    finally:
        cursor.close()
        connection.close()
    
    return resultados