from django import forms
from .models import Libro, Autor

class FormularioLibro(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ('nombre','anio', 'portada', 'id_autor', 'id_editorial')

class FormularioAutor(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ('nombre',)

class BookSearch(forms.Form):
    search = forms.CharField(
        label="Search for a book", required=False, widget=forms.TextInput(attrs={'class': "field__input", 'id': 'search', 'autofocus': True}))
    author = forms.CharField(
        label="Search for an author", required=False, widget=forms.TextInput(attrs={'class': "field__input", 'id': 'author'}))
