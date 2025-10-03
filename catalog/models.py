from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .utils import generate_default_book_image  

# -------------------
# Estante
# -------------------
class Shelf(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del estante")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        # Mostrar cajones si existen
        drawers = self.drawer_set.all()
        if drawers.exists():
            drawer_names = ', '.join([d.name for d in drawers])
            return f"{self.name} (Cajones: {drawer_names})"
        return self.name

# -------------------
# Cajón
# -------------------
class Drawer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del cajón")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, verbose_name="Estante")

    def __str__(self):
        return f"{self.shelf} - {self.name}"

    @property
    def display_name(self):
        return f"{self.name} (Estante: {self.shelf.name})"

# -------------------
# Clasificación
# -------------------
class Classification(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la clasificación")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        genres = self.gender_set.all()
        if genres.exists():
            genre_names = ', '.join([g.name for g in genres])
            return f"{self.name} (Géneros: {genre_names})"
        return self.name

# -------------------
# Género
# -------------------
class Gender(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del género")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    start_date = models.DateField(blank=True, null=True, verbose_name="¿Cuándo inicia?")
    end_date = models.DateField(blank=True, null=True, verbose_name="¿Cuándo termina?")
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, verbose_name="Clasificación")

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        books = self.book_set.all()[:15]
        books_text = ', '.join([b.title for b in books]) if books.exists() else 'No hay libros registrados'
        return f"{self.name} (Clasificación: {self.classification.name}) - Libros: {books_text}"

# -------------------
# Autor
# -------------------
class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Nombre/s")
    last_name = models.CharField(max_length=100, verbose_name="Apellido/s")
    birth_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año de nacimiento")
    death_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año de fallecimiento")
    biography = models.TextField(blank=True, verbose_name="Biografía")
    semblance = models.TextField(blank=True, verbose_name="Semblanza")
    image = models.ImageField(
        upload_to="authors_images/",
        blank=True,
        null=True,
        verbose_name="Imagen",
    )
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self):
        if self.birth_year or self.death_year:
            life = f"{self.birth_year or '¿?'} - {self.death_year or '¿?'}"
            return f"{self.first_name} {self.last_name} ({life})"
        return f"{self.first_name} {self.last_name}"


# -------------------
# Libro
# -------------------
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .utils import generate_default_book_image  # Importar desde utils

class Book(models.Model):
    COVERS = [
        ("hard", "Dura"),
        ("soft", "Blanda"),
        ("virtual", "Virtual"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Información básica
    title = models.CharField(max_length=200, verbose_name="Título")
    subtitle = models.CharField(blank=True, null=True, max_length=200, verbose_name="Subtítulo")
    author = models.ForeignKey("Author", on_delete=models.CASCADE, verbose_name="Autor")
    publication_date = models.DateField(blank=True, null=True, verbose_name="Fecha de publicación")
    place_of_publication = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lugar de publicación")
    editorial = models.CharField(max_length=100, verbose_name="Editorial")
    volume = models.IntegerField(blank=True, null=True, verbose_name="Volumen")
    edition = models.CharField(max_length=50, blank=True, null=True, verbose_name="Edición")
    page_count = models.PositiveIntegerField(blank=True, null=True, default=0, verbose_name="Número de páginas")

    # Identificadores
    isbn = models.CharField(max_length=20, blank=True, null=True, verbose_name="ISBN")
    doi = models.CharField(max_length=100, blank=True, null=True, verbose_name="DOI")

    # Otros colaboradores
    translator = models.CharField(max_length=100, blank=True, null=True, verbose_name="Traductor")
    editor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Editor/Compilador")

    # Relacionados con la organización
    genre = models.ForeignKey("Gender", on_delete=models.SET_NULL, null=True, verbose_name="Género")
    shelf = models.ForeignKey("Shelf", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Estante")
    drawer = models.ForeignKey("Drawer", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cajón")
    classification = models.ForeignKey("Classification", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Clasificación")

    # Digital y recursos online
    cover = models.CharField(max_length=10, choices=COVERS, default="soft", blank=True, verbose_name="Tipo de portada")
    pdf_file = models.FileField(blank=True, null=True, upload_to="books/pdfs/", verbose_name="Archivo PDF")
    image = models.ImageField(upload_to="books_images/", blank=True, null=True, verbose_name="Imagen")
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    access_date = models.DateField(blank=True, null=True, verbose_name="Fecha de consulta")

    # Extras
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name="Idioma")
    series = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serie/Colección")
    synopsis = models.TextField(blank=True, null=True, verbose_name="Sinopsis")

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        pub_year = self.publication_date.year if self.publication_date else "Año desconocido"
        cover_display = dict(self.COVERS).get(self.cover, "Blanda")  
        virtual_text = " - Virtual" if self.pdf_file else ""
        return f"{self.title} ({self.author}) - {pub_year} - {cover_display}{virtual_text}"

    def save(self, *args, **kwargs):
        # Generar imagen por defecto si no existe
        if not self.image and self.title:
            try:
                image_file = generate_default_book_image(
                    self.title, 
                    width=400, 
                    height=600, 
                    bg_color="#1F2937", 
                    text_color="#FFD700"
                )
                if image_file:
                    self.image.save(
                        f"default_{self.title[:10]}.png",
                        image_file,
                        save=False
                    )
            except Exception as e:
                print(f"Error generando imagen por defecto: {e}")
                # Continuar sin imagen por defecto si hay error
        
        super().save(*args, **kwargs)

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    last_page = models.PositiveIntegerField(default=1)  # empieza en página 1

    class Meta:
        unique_together = ('user', 'book')  # un registro por usuario y libro

    def __str__(self):
        return f"{self.user.username} - {self.book.title} página {self.last_page}"
    

class Babel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    books = models.ManyToManyField("Book", blank=True, related_name="babels")  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name