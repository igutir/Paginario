from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=False)
    fecha_registro = models.DateField(null=False)

    def __str__(self):
        return str(self.nombre)

class Estado_Libro(models.Model):
    nombre = models.CharField(max_length=100, null=False)

    def __str__(self):
        return str(self.nombre)

class Genero_Literario(models.Model):
    nombre = models.CharField(max_length=100, null=False)

    def __str__(self):
        return str(self.nombre)

class Autor(models.Model):
    nombre = models.CharField(max_length=100, null=False)

    def __str__(self):
        return str(self.nombre)

class Editorial(models.Model):
    nombre = models.CharField(max_length=100, null=False)

    def __str__(self):
        return str(self.nombre)

class Libro(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    autor = models.IntegerField(null=False)
    anio = models.IntegerField(null=False)
    portada = models.ImageField(upload_to='covers/%Y/%m/%d', height_field=None, width_field=None, max_length=None)
    id_editorial = models.ForeignKey(Editorial, on_delete = models.CASCADE)
    id_autor = models.ForeignKey(Autor, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.nombre)

class Lista(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    id_libro = models.ForeignKey(Libro, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.nombre)

class Usuario_Libro(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    id_libro = models.ForeignKey(Libro, on_delete = models.CASCADE)
    calificacion = models.IntegerField(null=True)
    resenia = models.TextField(null=True, blank=True)
    id_estado_libro = models.ForeignKey(Estado_Libro, on_delete = models.CASCADE)

    def __str__(self):
        return str("ID USUARIO: " + self.id_usuario + " | " + "ID LIBRO: " + self.id_libro)

class Libro_Genero_Literario(models.Model):
    id_libro = models.ForeignKey(Libro, on_delete = models.CASCADE)
    id_genero_literario = models.ForeignKey(Genero_Literario, on_delete = models.CASCADE)

    def __str__(self):
        return str("ID LIBRO: " + self.id_libro  + " | " + "ID GENERO LITERARIO: " + self.id_genero_literario)

class Usuario_Genero_Literario(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    id_genero_literario = models.ForeignKey(Genero_Literario, on_delete = models.CASCADE)

    def __str__(self):
        return str("ID USUARIO: " + self.id_usuario + " | " + "ID GENERO LITERARIO: " + self.id_genero_literario)