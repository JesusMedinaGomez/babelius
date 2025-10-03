# forms.py
from django import forms
from .models import *
from datetime import date

YEARS = [y for y in range(1000, date.today().year + 1)] 


# ---------------------------
# FORMULARIOS
# ---------------------------

class ShelfForm(forms.ModelForm):
    AUTO_NAME_CHOICES = [
        (True, "Asignar nombre automáticamente"),
        (False, "Escribir nombre manualmente")
    ]
    
    auto_name = forms.ChoiceField(
        choices=AUTO_NAME_CHOICES,
        widget=forms.RadioSelect,
        initial=True,
        label="Nombre de estante"
    )

    class Meta:
        model = Shelf
        exclude = ['user'] 
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Escribe un nombre...'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False


class DrawerForm(forms.ModelForm):
    class Meta:
        model = Drawer
        exclude = ['user', 'name']  
        widgets = {
            'shelf': forms.Select(attrs={'class': 'form-select'})
        }



class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Classification
        exclude = ['user']  
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Escribe el nombre de tu clasificación...'})
        }


class GenderForm(forms.ModelForm):
    start_year = forms.IntegerField(
        label="Año de inicio",
        min_value=0,
        max_value=9999,
        required=False
    )
    end_year = forms.IntegerField(
        label="Año de fin",
        min_value=0,
        max_value=9999,
        required=False
    )

    class Meta:
        model = Gender
        fields = ['name', 'description', 'classification']  



class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        exclude = ['user'] 
        fields = ['first_name', 'last_name', 'birth_year', 'death_year', 'biography', 'semblance', 'image']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre/s'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido/s'}),
            'birth_year': forms.TextInput(attrs={'placeholder': 'Ej: 1920'}),
            'death_year': forms.TextInput(attrs={'placeholder': 'Ej: 1985'}),
            'biography': forms.Textarea(attrs={'rows': 4}),
            'semblance': forms.Textarea(attrs={'rows': 4}),
        }

class BookForm(forms.ModelForm):
    publication_year = forms.ChoiceField(
        choices=[(y, y) for y in YEARS],
        required=False,
        label="Año de publicación"
    )

    # Campos extra para JS: selección inicial de estante y clasificación
    shelf_choice = forms.ModelChoiceField(
        queryset=Shelf.objects.none(),
        required=False,
        label="Estante",
        empty_label="Selecciona un estante"
    )
    classification_choice = forms.ModelChoiceField(
        queryset=Classification.objects.none(),
        required=False,
        label="Clasificación",
        empty_label="Selecciona una clasificación"
    )

    class Meta:
        model = Book
        exclude = ['user']  
        fields = [
            'title', 'subtitle', 'author', 'volume', 'editorial',
            'place_of_publication', 'edition', 'translator', 'isbn',
            'doi', 'url', 'access_date', 'synopsis',
            'genre', 'pdf_file', 'drawer', 'cover', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Título del libro',
                'class': 'form-control'
            }),
            'subtitle': forms.TextInput(attrs={
                'placeholder': 'Subtítulo (opcional)',
                'class': 'form-control'
            }),
            'editorial': forms.TextInput(attrs={
                'placeholder': 'Editorial',
                'class': 'form-control'
            }),
            'place_of_publication': forms.TextInput(attrs={
                'placeholder': 'Ciudad de publicación',
                'class': 'form-control'
            }),
            'edition': forms.TextInput(attrs={
                'placeholder': 'Ej. 2ª edición',
                'class': 'form-control'
            }),
            'translator': forms.TextInput(attrs={
                'placeholder': 'Traductor (si aplica)',
                'class': 'form-control'
            }),
            'isbn': forms.TextInput(attrs={
                'placeholder': 'ISBN',
                'class': 'form-control'
            }),
            'doi': forms.TextInput(attrs={
                'placeholder': 'DOI',
                'class': 'form-control'
            }),
            'url': forms.URLInput(attrs={
                'placeholder': 'URL (si es libro digital)',
                'class': 'form-control'
            }),
            'access_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'synopsis': forms.Textarea(attrs={
                'placeholder': 'Notas o comentarios',
                'class': 'form-control',
                'rows': 3
            }),
            'cover': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'drawer': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Título',
            'subtitle': 'Subtítulo',
            'author': 'Autor',
            'volume': 'Volumen',
            'editorial': 'Editorial',
            'place_of_publication': 'Lugar de publicación',
            'edition': 'Edición',
            'translator': 'Traductor',
            'isbn': 'ISBN',
            'doi': 'DOI',
            'url': 'URL',
            'access_date': 'Fecha de acceso',
            'synopsis': 'Sinopsis',
            'genre': 'Género',
            'drawer': 'Cajón',
            'cover': 'Tipo de cubierta',
            'image': 'Imagen',
            'pdf_file': 'Archivo PDF',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['shelf_choice'].queryset = Shelf.objects.filter(user=user)
            self.fields['classification_choice'].queryset = Classification.objects.filter(user=user)
            self.fields['drawer'].queryset = Drawer.objects.filter(user=user)
            self.fields['genre'].queryset = Gender.objects.filter(user=user)

        # 👇 Ajustes extra de usabilidad
        self.fields['author'].empty_label = "Selecciona un autor"
        self.fields['drawer'].empty_label = "Selecciona un cajón"
        self.fields['genre'].empty_label = "Selecciona un género"

class BabelForm(forms.ModelForm):
    class Meta:
        model = Babel
        fields = ["name", "description"]  # agregamos descripción aquí
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de Babel"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción (opcional)"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

class ReadingProgressForm(forms.ModelForm):
    class Meta:
        model = ReadingProgress
        fields = ['last_page']
        widgets = {
            'last_page': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            })
        }