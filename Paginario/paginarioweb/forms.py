from django import forms
from .models import Libro

class FomrularioLibro(forms.ModelForm):
    class Meta:
        model = Libro
        fields = "__all__"
