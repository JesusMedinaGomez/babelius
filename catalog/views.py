###########################################################################################
#                                                                                        #
#                                    DJANGO VIEWS                                        #
#                                                                                        #
#   Este archivo contiene las vistas principales de la aplicación.                       #
#   Se encuentra organizado por secciones claras, siguiendo un esquema tipo CRUD          #
#   (Create, Read, Update, Delete) más secciones adicionales (Details, AJAX).            #
#                                                                                        #
#   Estructura del archivo:                                                              #
#                                                                                        #
#   1. CREATE   -> Vistas para creación de objetos (formularios y múltiples registros).   #
#   2. READ     -> Vistas para listados con filtros, búsquedas y cálculos adicionales.    #
#   3. UPDATE   -> Vistas para actualización de registros existentes.                     #
#   4. DELETE   -> Vistas para eliminación de registros.                                  #
#   5. DETAILS  -> Vistas de detalle de un objeto con campos y relaciones asociadas.      #
#   6. AJAX     -> Endpoints que devuelven JSON:                                          #
#                   - Encadenados (selects dependientes).                                 #
#                   - Modales (creación rápida vía AJAX).                                 #
#                   - Progreso (guardar páginas leídas).                                  #
#                                                                                        #
#   Convenciones:                                                                        #
#     - Todas las vistas están protegidas con @login_required.                           #
#     - Cada vista cuenta con un docstring breve y comentarios internos cuando aportan.  #
#     - Contextos de render incluyen siempre 'title' y 'objects' cuando aplica.          #
#     - Se mantiene estilo uniforme en nomenclatura y documentación.                     #
#                                                                                        #
###########################################################################################


# =========================================================================================
# IMPORTS
# =========================================================================================

# Django utils
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.translation import gettext as _
from django.db.models import Q

# Python utils
from datetime import date
import json
from PyPDF2 import PdfReader

# Project modules
from .forms import *
from .models import *
from .utils import LANGUAGES_ES

# =========================================================================================
#                                          CREATE
# =========================================================================================


@login_required
def create_babel(request):
    """
    Vista para crear un nuevo 'Babel'.

    - Muestra formulario para creación.
    - Permite asociar libros existentes al babel.
    - Aplica filtros de búsqueda, clasificación y género en los libros mostrados.
    """
    if request.method == "POST":
        form = BabelForm(request.POST, user=request.user)
        if form.is_valid():
            babel = form.save(commit=False)
            babel.user = request.user
            babel.save()

            # Guardar libros seleccionados (si los hay)
            books_ids = request.POST.get("books", "")
            if books_ids:
                ids = [int(bid) for bid in books_ids.split(",") if bid.isdigit()]
                books = Book.objects.filter(id__in=ids, user=request.user)
                babel.books.set(books)
            else:
                babel.books.clear()

            return redirect("read_babels")  

    else:
        form = BabelForm(user=request.user)

    # --- Filtros de búsqueda ---
    search_query = request.GET.get("search", "")
    selected_classification = request.GET.get("classification")
    selected_genre = request.GET.get("genre")

    books = Book.objects.filter(user=request.user)

    # Búsqueda por título o autor
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )

    # Filtrar por clasificación
    if selected_classification:
        books = books.filter(classification_id=selected_classification)

    # Filtrar por género
    if selected_genre:
        books = books.filter(genre_id=selected_genre)

    books = books.order_by("title")

    # Géneros disponibles (filtrados por clasificación si aplica)
    user_genres = Gender.objects.filter(user=request.user)
    if selected_classification:
        user_genres = user_genres.filter(classification_id=selected_classification)

    # IDs de libros seleccionados (vacío en creación)
    selected_books_ids = []

    return render(request, "create_update/create_babel.html", {
        "form": form,
        "books": books,
        "search_query": search_query,
        "selected_classification_id": selected_classification,
        "selected_genre_id": selected_genre,
        "user_classifications": Classification.objects.filter(user=request.user),
        "user_genres": user_genres,
        "selected_books_ids": selected_books_ids,
    })


@login_required
def create_shelf(request):
    """
    Vista para crear un nuevo 'Estante'.

    - Asigna automáticamente un nombre si se selecciona la opción de auto-nombre
      o si el nombre no se proporciona.
    """
    form = ShelfForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        shelf = form.save(commit=False)
        shelf.user = request.user

        # Autoasignar nombre si corresponde
        if form.cleaned_data.get('auto_name') == 'True' or not shelf.name:
            shelf.name = f"E{Shelf.objects.count() + 1}"

        shelf.save()
        return redirect('read_shelfs')

    return render(request,'create_update/create_shelf_form.html', {
        'form': form,
        'title': 'Crear estante'
    })


@login_required
def create_drawer(request):
    """
    Vista para crear un nuevo 'Cajón'.

    - Se asigna automáticamente un nombre secuencial basado en la cantidad
      de cajones en el estante seleccionado.
    """
    form = DrawerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        drawer = form.save(commit=False)
        drawer.user = request.user
        selected_shelf = form.cleaned_data['shelf']
        drawer.shelf = selected_shelf

        # Asignar nombre en base a la cantidad de cajones existentes en ese estante
        count_in_shelf = Drawer.objects.filter(user=request.user, shelf=selected_shelf).count()
        drawer.name = f"C{count_in_shelf + 1}"

        drawer.save()
        return redirect('read_drawers')

    return render(request, 'create_update/create_form.html', {
        'form': form,
        'title': 'Crear cajón'
    })


@login_required
def create_classification(request):
    """
    Vista para crear una nueva 'Clasificación'.
    """
    form = ClassificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        classification = form.save(commit=False)
        classification.user = request.user
        classification.save()
        return redirect('read_classifications')

    return render(request, 'create_update/create_form.html', {
        'form': form,
        'title': 'Crear clasificación'
    })


@login_required
def create_gender(request):
    """
    Vista para crear un nuevo 'Género'.
    """
    form = GenderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        gender = form.save(commit=False)
        gender.user = request.user
        gender.save()
        return redirect('read_genders')

    return render(request, 'create_update/create_form.html', {
        'form': form,
        'title': 'Crear género'
    })


@login_required
def create_author(request):
    """
    Vista para crear un nuevo 'Autor'.

    - Permite ingresar años de nacimiento y defunción, que se transforman en
      fechas completas (inicio y fin de año respectivamente).
    """
    form = AuthorForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        author = form.save(commit=False)

        # Manejar fechas a partir de años ingresados
        birth_year = form.cleaned_data.get('birth_year')
        death_year = form.cleaned_data.get('death_year')
        if birth_year:
            author.birth_date = date(int(birth_year), 1, 1)
        if death_year:
            author.death_date = date(int(death_year), 12, 31)

        author.user = request.user
        author.save()
        return redirect('read_authors')

    return render(request, 'create_update/create_form.html', {
        'form': form,
        'title': 'Crear autor'
    })


@login_required
def create_book(request):
    """
    Vista para crear uno o varios 'Libros'.

    - Admite creación múltiple usando índices en los campos de formulario (ej: 0_title).
    - Valida campos obligatorios (título, editorial).
    - Maneja archivos asociados (imagen, PDF).
    - Permite asociar libro con estante, cajón, autor, clasificación y género.
    """
    # --- Datos previos del usuario ---
    user_shelfs = Shelf.objects.filter(user=request.user)
    user_drawers = Drawer.objects.filter(user=request.user)
    user_classifications = Classification.objects.filter(user=request.user)
    user_genres = Gender.objects.filter(classification__user=request.user)
    user_authors = Author.objects.filter(user=request.user)

    if request.method == "POST":
        print("=== INICIANDO CREACIÓN DE LIBROS ===")
        
        books_data = []
        idx = 0

        # Recorrer todos los posibles libros enviados
        while f"{idx}_title" in request.POST:
            books_data.append({
                "title": request.POST.get(f"{idx}_title") or None,
                "subtitle": request.POST.get(f"{idx}_subtitle") or None,
                "editorial": request.POST.get(f"{idx}_editorial") or None,
                "shelf_id": request.POST.get(f"{idx}_shelf") or None,
                "drawer_id": request.POST.get(f"{idx}_drawer") or None,
                "author_id": request.POST.get(f"{idx}_author") or None,
                "classification_id": request.POST.get(f"{idx}_classification") or None,
                "genre_id": request.POST.get(f"{idx}_genre") or None,
                "volume": request.POST.get(f"{idx}_volume") or None,
                "cover": request.POST.get(f"{idx}_cover") or None,
                "pdf_file": request.FILES.get(f"{idx}_pdf_file") or None,
                "image": request.FILES.get(f"{idx}_image") or None,
                "language": request.POST.get(f"{idx}_language") or None,
                "isbn": request.POST.get(f"{idx}_isbn") or None,
                "page_count": request.POST.get(f"{idx}_pages") or 0,
                "synopsis": request.POST.get(f"{idx}_synopsis") or "",
                "publication_year": request.POST.get(f"{idx}_publication_year") or None,
                "doi": request.POST.get(f"{idx}_doi") or None,
                "series": request.POST.get(f"{idx}_series") or None,
                "translator": request.POST.get(f"{idx}_translator") or None,
                "editor_compiler": request.POST.get(f"{idx}_editor_compiler") or None,
                "url": request.POST.get(f"{idx}_url") or None,
            })
            idx += 1

        # Procesar cada libro y guardarlo
        for i, data in enumerate(books_data):
            if not data["title"] or not data["editorial"]:
                continue  # saltar si faltan datos obligatorios

            try:
                book = Book(
                    title=data["title"],
                    subtitle=data["subtitle"],
                    editorial=data["editorial"],
                    shelf_id=data["shelf_id"],
                    drawer_id=data["drawer_id"],
                    author_id=data["author_id"],
                    classification_id=data["classification_id"],
                    genre_id=data["genre_id"],
                    volume=int(data["volume"]) if data["volume"] and data["volume"].isdigit() else None,
                    cover=data["cover"],
                    user=request.user,
                    language=data["language"],
                    isbn=data["isbn"],
                    page_count=int(data["page_count"]) if data["page_count"] and data["page_count"].isdigit() else 0,
                    synopsis=data["synopsis"] or "",
                    doi=data["doi"],
                    series=data["series"],
                    translator=data["translator"],
                    editor=data["editor_compiler"],
                    url=data["url"],
                )

                # Año de publicación
                if data["publication_year"] and data["publication_year"].isdigit():
                    try:
                        book.publication_date = date(int(data["publication_year"]), 1, 1)
                    except ValueError as e:
                        print(f"Error en fecha publicación libro {i}: {e}")

                # Archivos (PDF e imagen)
                if data["pdf_file"]:
                    book.pdf_file = data["pdf_file"]
                if data["image"]:
                    book.image = data["image"]

                book.save()
            except Exception as e:
                print(f"Error guardando libro {i}: {e}")
                continue

        print("=== FINALIZADA CREACIÓN DE LIBROS ===")
        return redirect("read_books")

    # Datos iniciales para el formulario
    languages = LANGUAGES_ES
    return render(request, "create_update/create_book_form.html", {
        "user_shelfs": user_shelfs,
        "user_drawers": user_drawers,
        "user_classifications": user_classifications,
        "user_genres": user_genres,
        "user_authors": user_authors,
        "COVERS": Book.COVERS,
        "languages": languages,
    })


# =========================================================================================
#                                           READ
# =========================================================================================

@login_required
def read_babels(request):
    """
    Vista para listar los 'Babels' del usuario autenticado.
    """
    babels = Babel.objects.filter(user=request.user)
    objects = [{"instance": b} for b in babels]

    context = {
        "title": "Mis Babels",
        "title_singular": "Babel",
        "title_plural": "Babels",
        "objects": objects,
        "create_url_name": "create_babel",
        "edit_url_name": "update_babel",
        "delete_url_name": "delete_babel",
    }
    return render(request, "read/read_babels.html", context)


@login_required
def read_shelfs(request):
    """
    Vista para listar los 'Estantes' del usuario.
    """
    objects = [{"instance": shelf} for shelf in Shelf.objects.filter(user=request.user)]
    context = {
        "objects": objects,
        "title": "Estantes",
        "title_singular": "Estante",
        "create_url_name": "create_shelf",
        "edit_url_name": "update_shelf",
        "delete_url_name": "delete_shelf",
        "detail_url_name": "detail_shelf",
    }
    return render(request, "read/read_shelfs.html", context)


@login_required
def read_drawers(request):
    """
    Vista para listar los 'Cajones' del usuario.
    """
    objects = [{"instance": drawer} for drawer in Drawer.objects.filter(user=request.user)]
    context = {
        "objects": objects,
        "title": "Cajones",
        "title_singular": "Cajón",
        "create_url_name": "create_drawer",
        "edit_url_name": None,  
        "delete_url_name": "delete_drawer",
        "detail_url_name": "detail_drawer",
    }
    return render(request, "read/read_drawers.html", context)


@login_required
def read_classifications(request):
    """
    Vista para listar las 'Clasificaciones' del usuario.
    """
    objects = [{"instance": c} for c in Classification.objects.filter(user=request.user)]
    context = {
        "objects": objects,
        "title": "Clasificaciones",
        "title_singular": "Clasificación",
        "create_url_name": "create_classification",
        "edit_url_name": None,  
        "delete_url_name": "delete_classification",
        "detail_url_name": None,
    }
    return render(request, "read/read_classifications.html", context)


@login_required
def read_genders(request):
    """
    Vista para listar los 'Géneros' del usuario.
    """
    objects = [{"instance": g} for g in Gender.objects.filter(user=request.user)]
    context = {
        "objects": objects,
        "title": "Géneros",
        "title_singular": "Género",
        "create_url_name": "create_gender",
        "edit_url_name": "update_gender",
        "delete_url_name": "delete_gender",
        "detail_url_name": "detail_gender",
    }
    return render(request, "read/read_genders.html", context)


@login_required
def read_authors(request):
    """
    Vista para listar los 'Autores' del usuario.
    """
    user_authors = Author.objects.filter(user=request.user)
    objects = [{"instance": author} for author in user_authors]

    context = {
        'title': "Autores",
        'title_singular': "Autor",
        'objects': objects,
        'detail_url_name': 'detail_author',
        'edit_url_name': 'update_author',
        'delete_url_name': 'delete_author',
        'create_url_name': 'create_author',
    }
    return render(request, "read/read_authors.html", context)


@login_required
def read_books(request):
    """
    Vista para listar los 'Libros' del usuario con filtros:

    - Filtro por clasificación.
    - Filtro por género.
    - Búsqueda por título, subtítulo o autor.
    - Cálculo de progreso de lectura y generación de referencia en formato APA.
    """
    # --- Filtros de la URL ---
    selected_classification_id = request.GET.get('classification', '')
    selected_genre_id = request.GET.get('genre', '')
    search_query = request.GET.get('search', '')

    # --- Consulta base ---
    user_books_queryset = Book.objects.filter(user=request.user).select_related(
        'author', 'genre__classification', 'drawer__shelf', 'shelf'
    )

    # Aplicar filtros
    if selected_classification_id:
        user_books_queryset = user_books_queryset.filter(
            Q(classification_id=selected_classification_id) | 
            Q(genre__classification_id=selected_classification_id)
        )
    
    if selected_genre_id:
        user_books_queryset = user_books_queryset.filter(genre_id=selected_genre_id)

    if search_query:
        user_books_queryset = user_books_queryset.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )

    # --- Preparar datos para la plantilla ---
    objects = []
    for book in user_books_queryset:
        # Progreso de lectura
        progress = ReadingProgress.objects.filter(user=request.user, book=book).first()
        last_page = progress.last_page if progress else 0
        progress_percent = int((last_page / book.page_count) * 100) if book.page_count else 0
        progress_percent = min(progress_percent, 100)

        # Construcción de referencia APA
        apa_author = (
            f"{book.author.last_name.split(' ')[0].capitalize()}, {book.author.first_name[0].upper()}."
            if book.author else "Autor desconocido"
        )
        apa_year = book.publication_date.year if book.publication_date else "¿?"
        apa_title = book.title if book.title else "Título desconocido"
        apa_subtitle = f": {book.subtitle}" if book.subtitle else ""
        apa_editorial = book.editorial or ""
        apa_volume = f"(Vol. {book.volume})" if book.volume else ""
        apa_edition = f"({book.edition} ed.)" if book.edition else ""
        apa_place = book.place_of_publication or ""
        apa_series = f"{book.series}" if getattr(book, "series", None) else ""
        apa_translator = f"(Trad. {book.translator})" if getattr(book, "translator", None) else ""
        apa_editor = f"(Ed. {book.editor})" if getattr(book, "editor", None) else ""
        apa_pages = f"{book.page_count} pp." if book.page_count else ""
        apa_doi = f"https://doi.org/{book.doi}" if book.doi else ""
        apa_url = book.url if getattr(book, "url", None) else ""

        extra_info = ", ".join(filter(None, [
            apa_volume, apa_edition, apa_place, apa_series, apa_translator, apa_editor, apa_pages
        ]))
        extra_info = f" ({extra_info})" if extra_info else ""

        apa_citation = f"{apa_author} ({apa_year}). {apa_title}{apa_subtitle}. {apa_editorial}{extra_info}."
        if apa_doi:
            apa_citation += f" {apa_doi}"
        elif apa_url:
            apa_citation += f" {apa_url}"

        objects.append({
            'instance': book,
            'progress_percent': progress_percent,
            'last_page': last_page,
            'apa_citation': apa_citation,
        })

    # Opciones para los filtros dinámicos
    user_classifications = Classification.objects.filter(user=request.user).order_by('name')
    if selected_classification_id:
        user_genres = Gender.objects.filter(
            user=request.user,
            classification_id=selected_classification_id
        ).order_by('name')

        # fallback en caso de que no existan géneros vinculados
        if not user_genres.exists():
            user_genres = Gender.objects.filter(
                user=request.user,
                classification__id=selected_classification_id
            ).order_by('name')
    else:
        user_genres = Gender.objects.none()

    context = {
        'title': "Libros",
        'title_singular': "Libro",
        'objects': objects,
        'detail_url_name': 'detail_book',
        'edit_url_name': 'update_book',
        'delete_url_name': 'delete_book',
        'create_url_name': 'create_book',
        'user_classifications': user_classifications,
        'user_genres': user_genres,
        'selected_classification_id': selected_classification_id,
        'selected_genre_id': selected_genre_id,
        'search_query': search_query,
    }
    return render(request, 'read/read_books.html', context)


@login_required
def read_pdf(request, pk):
    """
    Vista para leer un 'Libro' en formato PDF.

    - Obtiene o crea el progreso de lectura.
    - Si el PDF no tiene page_count registrado, lo calcula con PyPDF2.
    """
    book = get_object_or_404(Book, pk=pk)
    progress, _ = ReadingProgress.objects.get_or_create(user=request.user, book=book)

    # Calcular número de páginas si no está seteado
    if book.pdf_file and book.page_count == 0:
        try:
            reader = PdfReader(book.pdf_file.path)
            book.page_count = len(reader.pages)
            book.save(update_fields=['page_count'])
        except Exception as e:
            print("Error leyendo PDF:", e)

    context = {
        "book": book,
        "last_page": progress.last_page,
    }
    return render(request, "read/read_pdf.html", context)


@login_required
def read_physical(request, pk):
    """
    Vista para registrar y mostrar el progreso de lectura de un 'Libro físico'.

    - Permite actualizar el número de página alcanzado.
    - Genera referencia APA del libro.
    """
    book = get_object_or_404(Book, pk=pk, user=request.user)
    progress, _ = ReadingProgress.objects.get_or_create(user=request.user, book=book)

    if request.method == "POST":
        form = ReadingProgressForm(request.POST, instance=progress)
        if form.is_valid():
            last_page = form.cleaned_data['last_page']
            if book.page_count and last_page > book.page_count:
                form.add_error('last_page', f"No puede ser mayor que {book.page_count}")
            else:
                form.save()
    else:
        form = ReadingProgressForm(instance=progress)

    # Construcción de referencia APA
    apa_author = (
        f"{book.author.last_name.split(' ')[0].capitalize()}, {book.author.first_name.split(' ')[0][0].upper()}."
        if book.author else "Autor desconocido"
    )
    apa_year = book.publication_date.year if book.publication_date else "¿?"
    apa_title = book.title if book.title else "Título desconocido"
    apa_subtitle = f": {book.subtitle}" if book.subtitle else ""
    apa_editorial = book.editorial or ""
    apa_volume = f"Vol. {book.volume}" if book.volume else ""
    apa_edition = f"{book.edition} ed." if book.edition else ""
    apa_place = book.place_of_publication or ""
    apa_series = book.series or ""

    extra_info = ", ".join(filter(None, [apa_volume, apa_edition, apa_place, apa_series]))
    extra_info = f" ({extra_info})" if extra_info else ""

    apa_citation = f"{apa_author} ({apa_year}). {apa_title}{apa_subtitle}. {apa_editorial}{extra_info}."

    context = {
        "book": book,
        "form": form,
        "apa_citation": apa_citation,
    }
    return render(request, "read/read_physical.html", context)


# =========================================================================================
#                                         UPDATE
# =========================================================================================

@login_required
def update_babel(request, pk):
    """
    Vista para actualizar un 'Babel'.

    - Permite modificar datos del babel.
    - Actualiza los libros asociados al mismo.
    """
    babel = get_object_or_404(Babel, pk=pk, user=request.user)

    if request.method == "POST":
        form = BabelForm(request.POST, instance=babel, user=request.user)
        if form.is_valid():
            babel = form.save()

            # Actualizar libros asociados
            books_ids = request.POST.get("books", "")
            if books_ids:
                books = Book.objects.filter(
                    id__in=[int(bid) for bid in books_ids.split(",") if bid.isdigit()],
                    user=request.user
                )
                babel.books.set(books)
            else:
                babel.books.clear()

            return redirect("read_babels")
    else:
        form = BabelForm(instance=babel, user=request.user)

    selected_books = babel.books.all()
    user_genres = Gender.objects.filter(user=request.user)

    return render(request, "create_update/create_babel.html", {
        "form": form,
        "babel": babel,
        "books": Book.objects.filter(user=request.user).order_by("title"),
        "user_classifications": Classification.objects.filter(user=request.user),
        "user_genres": user_genres,
        "selected_books": selected_books,
        "search_query": "",
        "selected_classification_id": "",
        "selected_genre_id": "",
    })


@login_required
def update_book(request, pk):
    """
    Vista para actualizar un 'Libro'.

    - Permite modificar campos básicos, relaciones (autor, género, etc.)
      y archivos asociados (PDF, imagen).
    - Recalcula valores cuando es necesario (ej: volumen, páginas, publicación).
    """
    book = get_object_or_404(Book, pk=pk, user=request.user)

    if request.method == "POST":
        try:
            book.title = request.POST.get("title", book.title)
            book.subtitle = request.POST.get("subtitle", book.subtitle)
            book.editorial = request.POST.get("editorial", book.editorial)

            # Volumen
            volume_str = request.POST.get("volume", "")
            if volume_str and volume_str.isdigit():
                book.volume = int(volume_str)
            elif volume_str == "":
                book.volume = None

            # Relaciones
            if request.POST.get("shelf"):
                book.shelf_id = request.POST["shelf"]
            if request.POST.get("drawer"):
                book.drawer_id = request.POST["drawer"]
            if request.POST.get("author"):
                book.author_id = request.POST["author"]
            if request.POST.get("classification"):
                book.classification_id = request.POST["classification"]
            if request.POST.get("genre"):
                book.genre_id = request.POST["genre"]

            # Otros campos
            book.cover = request.POST.get("cover", book.cover)
            book.language = request.POST.get("language", book.language)
            book.isbn = request.POST.get("isbn", book.isbn)

            # Páginas
            pages_str = request.POST.get("pages", "")
            if pages_str.isdigit():
                book.page_count = int(pages_str)
            else:
                book.page_count = None

            book.synopsis = request.POST.get("synopsis", book.synopsis)
            book.series = request.POST.get("series") or None
            book.translator = request.POST.get("translator") or None
            book.editor = request.POST.get("editor_compiler") or None
            book.url = request.POST.get("url") or None

            # Año de publicación
            pub_year = request.POST.get("publication_year")
            if pub_year and pub_year.isdigit():
                try:
                    book.publication_date = date(int(pub_year), 1, 1)
                except ValueError:
                    pass  # ignorar errores en año inválido

            # Archivos
            if request.FILES.get("pdf_file"):
                book.pdf_file = request.FILES["pdf_file"]
            if request.FILES.get("image"):
                book.image = request.FILES["image"]

            book.save()
            return redirect("read_books")

        except Exception as e:
            print(f"Error actualizando libro: {e}")

    languages = LANGUAGES_ES
    return render(request, "create_update/create_book_form.html", {
        "book": book,
        "user_shelfs": Shelf.objects.filter(user=request.user),
        "user_drawers": Drawer.objects.filter(user=request.user),
        "user_classifications": Classification.objects.filter(user=request.user),
        "user_genres": Gender.objects.filter(user=request.user),
        "user_authors": Author.objects.filter(user=request.user),
        "COVERS": Book.COVERS,
        "languages": languages,
    })


@login_required
def update_author(request, pk):
    """
    Vista para actualizar un 'Autor'.
    """
    author = get_object_or_404(Author, pk=pk, user=request.user)
    if request.method == "POST":
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            return redirect("read_authors")
    else:
        form = AuthorForm(instance=author)

    return render(request, "create_update/create_form.html", {
        "form": form,
        "title": "Editar autor",
        "author": author,
    })


@login_required
def update_classification(request, pk):
    """
    Vista para actualizar una 'Clasificación'.
    """
    classification = get_object_or_404(Classification, pk=pk, user=request.user)
    if request.method == "POST":
        form = ClassificationForm(request.POST, instance=classification)
        if form.is_valid():
            form.save()
            return redirect("read_classifications")
    else:
        form = ClassificationForm(instance=classification)

    return render(request, "create_update/create_form.html", {
        "form": form,
        "title": "Editar clasificación",
        "classification": classification,
    })


@login_required
def update_gender(request, pk):
    """
    Vista para actualizar un 'Género'.
    """
    gender = get_object_or_404(Gender, pk=pk, user=request.user)
    if request.method == "POST":
        form = GenderForm(request.POST, instance=gender)
        if form.is_valid():
            form.save()
            return redirect("read_genders")
    else:
        form = GenderForm(instance=gender)

    return render(request, "create_update/create_form.html", {
        "form": form,
        "title": "Editar género",
        "gender": gender,
    })


@login_required
def update_shelf(request, pk):
    """
    Vista para actualizar un 'Estante'.

    - Si se selecciona auto-nombre o el campo está vacío,
      se renombra automáticamente con el ID del estante.
    """
    shelf = get_object_or_404(Shelf, pk=pk, user=request.user)

    if request.method == "POST":
        form = ShelfForm(request.POST, instance=shelf)
        if form.is_valid():
            shelf = form.save(commit=False)
            if form.cleaned_data['auto_name'] == 'True' or not shelf.name:
                shelf.name = f"E{shelf.pk}"
            shelf.save()
            return redirect("read_shelfs")
    else:
        form = ShelfForm(instance=shelf)
        form.initial['auto_name'] = True  

    return render(request, "create_update/create_shelf_form.html", {
        "form": form,
        "title": "Editar estante",
        "shelf": shelf,
    })


# =========================================================================================
#                                         DELETE
# =========================================================================================

@login_required
def delete_babel(request, pk):
    """
    Elimina un 'Babel' del usuario.
    """
    babel = get_object_or_404(Babel, pk=pk, user=request.user)
    babel.delete()
    return redirect("read_babels")


@login_required
def delete_book(request, pk):
    """
    Elimina un 'Libro' del usuario.
    """
    book = get_object_or_404(Book, pk=pk, user=request.user)
    book.delete()
    return redirect("read_books")


@login_required
def delete_author(request, pk):
    """
    Elimina un 'Autor' del usuario.
    """
    author = get_object_or_404(Author, pk=pk, user=request.user)
    author.delete()
    return redirect("read_authors")


@login_required
def delete_classification(request, pk):
    """
    Elimina una 'Clasificación' del usuario.
    """
    classification = get_object_or_404(Classification, pk=pk, user=request.user)
    classification.delete()
    return redirect("read_classifications")


@login_required
def delete_gender(request, pk):
    """
    Elimina un 'Género' del usuario.
    """
    gender = get_object_or_404(Gender, pk=pk, user=request.user)
    gender.delete()
    return redirect("read_genders")


@login_required
def delete_shelf(request, pk):
    """
    Elimina un 'Estante' del usuario.
    """
    shelf = get_object_or_404(Shelf, pk=pk, user=request.user)
    shelf.delete()
    return redirect("read_shelfs")


@login_required
def delete_drawer(request, pk):
    """
    Elimina un 'Cajón' del usuario.
    """
    drawer = get_object_or_404(Drawer, pk=pk, user=request.user)
    drawer.delete()
    return redirect("read_drawers")


# =========================================================================================
#                                     VIEW DETAILS
# =========================================================================================

@login_required
def detail_babel(request, pk):
    """
    Vista de detalle de un 'Babel'.

    - Muestra los libros asociados al babel.
    - Incluye enlaces a detalle, edición y eliminación de los libros.
    """
    babel = get_object_or_404(Babel, pk=pk, user=request.user)
    books = babel.books.all()
    objects = [{"instance": b} for b in books]

    context = {
        "title": f"Babel {babel.name}",
        "title_singular": "Libro",
        "title_plural": "Libros",
        "objects": objects,
        "babel": babel,
        "detail_url_name": "detail_book",
        "edit_url_name": "update_book",
        "delete_url_name": "delete_book",
    }
    return render(request, "read/detail_babel.html", context)


@login_required
def detail_shelf(request, pk):
    """
    Vista de detalle de un 'Estante'.

    - Muestra nombre del estante.
    - Lista los libros asociados a través de los cajones.
    """
    shelf = get_object_or_404(Shelf, pk=pk)
    fields = [
        ('Nombre', shelf.name, 'name'),
    ]
    related_books = Book.objects.filter(drawer__shelf=shelf)

    return render(request, 'read/detail.html', {
        'title': shelf.name,
        'fields': fields,
        'related_books': related_books,
        'list_url_name': 'read_shelfs',
    })


@login_required
def detail_drawer(request, pk):
    """
    Vista de detalle de un 'Cajón'.

    - Muestra nombre del cajón y su estante asociado.
    - Lista los libros contenidos en el cajón.
    """
    drawer = get_object_or_404(Drawer, pk=pk)
    fields = [
        ('Nombre', drawer.name, 'name'),
        ('Estante', drawer.shelf.name if drawer.shelf else None, 'shelf'),
    ]
    related_books = Book.objects.filter(drawer=drawer)

    return render(request, 'read/detail_shelf.html', {
        'title': drawer.name,
        'fields': fields,
        'related_books': related_books,
        'list_url_name': 'read_drawers',
    })


@login_required
def detail_classification(request, pk):
    """
    Vista de detalle de una 'Clasificación'.

    - Muestra nombre de la clasificación.
    - Lista géneros relacionados.
    - Lista libros vinculados a esos géneros.
    """
    classification = get_object_or_404(Classification, pk=pk)
    fields = [('Nombre', classification.name, 'name')]
    related_genders = classification.gender_set.all()
    related_books = Book.objects.filter(genre__classification=classification)

    return render(request, 'read/detail_classification.html', {
        'title': classification.name,
        'fields': fields,
        'related_genders': related_genders,
        'related_books': related_books,
        'list_url_name': 'read_classifications',
    })


@login_required
def detail_gender(request, pk):
    """
    Vista de detalle de un 'Género'.

    - Muestra datos del género y su clasificación asociada.
    - Lista los libros pertenecientes a ese género.
    """
    gender = get_object_or_404(Gender, pk=pk)
    fields = [
        ('Nombre', gender.name, 'name'),
        ('Descripción', gender.description, 'description'),
        ('Fecha inicio', gender.start_date, 'start_date'),
        ('Fecha fin', gender.end_date, 'end_date'),
        ('Clasificación', gender.classification.name if gender.classification else None, 'classification'),
    ]
    related_books = Book.objects.filter(genre=gender)

    return render(request, 'read/detail_gender.html', {
        'title': gender.name,
        'fields': fields,
        'related_books': related_books,
        'list_url_name': 'read_genders',
    })


@login_required
def detail_author(request, pk):
    """
    Vista de detalle de un 'Autor'.

    - Muestra información biográfica.
    - Calcula rango de vida (nacimiento - fallecimiento).
    - Lista libros asociados al autor.
    """
    author = get_object_or_404(Author, pk=pk)

    # Calcular rango de vida
    life = ""
    if author.birth_year:
        life += str(author.birth_year)
    life += " - "
    if author.death_year:
        life += str(author.death_year)
    if life == " - ":
        life = "Desconocidos"

    fields = [
        ("Nombre completo", f"{author.first_name} {author.last_name}", "name"),
        ("Nacimiento - Fallecimiento", life, "life"),
        ("Biografía", author.biography, "biography"),
        ("Semblanza", author.semblance, "semblance"),
        ("Cantidad de libros", author.book_set.count(), "books_count"),
    ]

    return render(request, "read/detail_author.html", {
        "title": f"{author.first_name} {author.last_name}",
        "fields": fields,
        "list_url_name": "read_authors",
        "related_books": author.book_set.all(),
    })


@login_required
def detail_book(request, pk):
    """
    Vista de detalle de un 'Libro'.

    - Muestra todos los campos del libro.
    - Construye una cita en formato APA.
    """
    book = get_object_or_404(Book, pk=pk)

    fields = [
        ('Título', book.title, 'title'),
        ('Subtítulo', book.subtitle, 'subtitle'),
        ('Autor', f"{book.author.first_name} {book.author.last_name}" if book.author else None, 'author'),
        ('Fecha publicación', book.publication_date, 'publication_date'),
        ('Volumen', book.volume, 'volume'),
        ('Edición', book.edition, 'edition'),
        ('Editorial', book.editorial, 'editorial'),
        ('Número de páginas', book.page_count, 'page_count'),
        ('Género', book.genre.name if book.genre else None, 'genre'),
        ('Estante', book.shelf.name if book.shelf else None, 'shelf'),
        ('Cajón', book.drawer.name if book.drawer else None, 'drawer'),
        ('Clasificación', book.classification.name if book.classification else None, 'classification'),
        ('Portada', book.cover, 'cover'),
        ('PDF', book.pdf_file.url if book.pdf_file else None, 'pdf_file'),
        ('Imagen', book.image.url if book.image else None, 'image'),
        ('URL', book.url, 'url'),
        ('Fecha de consulta', book.access_date, 'access_date'),
        ('Idioma', book.language, 'language'),
        ('Serie/Colección', book.series, 'series'),
        ('Traductor', book.translator, 'translator'),
        ('Editor/Compilador', book.editor, 'editor'),
        ('ISBN', book.isbn, 'isbn'),
        ('DOI', book.doi, 'doi'),
        ('Sinopsis', book.synopsis, 'notes'),
    ]

    # Construcción de referencia APA
    if book.author:
        apa_last_name = book.author.last_name.split(' ')[0].capitalize()
        apa_first_initial = book.author.first_name.split(' ')[0][0].upper()
        apa_author = f"{apa_last_name}, {apa_first_initial}."
    else:
        apa_author = "Autor desconocido"

    apa_year = book.publication_date.year if book.publication_date else "¿?"
    apa_title = book.title if book.title else "Título desconocido"
    apa_subtitle = f": {book.subtitle}" if book.subtitle else ""
    apa_editorial = book.editorial or ""
    apa_place = book.place_of_publication or ""
    apa_volume = f"(Vol. {book.volume})" if book.volume else ""
    apa_edition = f"({book.edition} ed.)" if book.edition else ""
    apa_series = f"{book.series}" if book.series else ""
    apa_translator = f"(Trad. {book.translator})" if book.translator else ""
    apa_editor = f"(Ed. {book.editor})" if book.editor else ""
    apa_pages = f"{book.page_count} pp." if book.page_count else ""
    apa_doi = f"https://doi.org/{book.doi}" if book.doi else ""
    apa_url = book.url if book.url else ""

    extra_info = ", ".join(filter(None, [
        apa_volume, apa_edition, apa_place, apa_series, apa_translator, apa_editor, apa_pages
    ]))
    extra_info = f" ({extra_info})" if extra_info else ""

    apa_citation = f"{apa_author} ({apa_year}). {apa_title}{apa_subtitle}. {apa_editorial}{extra_info}."
    if apa_doi:
        apa_citation += f" {apa_doi}"
    elif apa_url:
        apa_citation += f" {apa_url}"

    return render(request, 'read/detail_book.html', {
        'title': book.title,
        'fields': fields,
        'list_url_name': 'read_books',
        'apa_citation': apa_citation,
    })

# =========================================================================================
#                                     AJAX ENDPOINTS
# =========================================================================================

# -------------------
# AJAX encadenados
# -------------------

@login_required
def load_drawers(request):
    """
    Devuelve los cajones pertenecientes a un estante específico (para selects encadenados).
    """
    shelf_id = request.GET.get("shelf_id")
    drawers = Drawer.objects.filter(shelf_id=shelf_id, user=request.user).values("id", "name")
    return JsonResponse(list(drawers), safe=False)


@login_required
def load_genres(request):
    """
    Devuelve los géneros pertenecientes a una clasificación específica (para selects encadenados).
    """
    classification_id = request.GET.get("classification_id")
    genres = Gender.objects.filter(classification_id=classification_id, user=request.user).values("id", "name")
    return JsonResponse(list(genres), safe=False)


# -------------------
# AJAX modales
# -------------------

@csrf_exempt
@login_required
def create_shelf_modal(request):
    """
    Crea un 'Estante' desde un modal vía AJAX.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        auto = request.POST.get("auto") in ["true", "True", True]

        if auto or not name:
            name = f"E{Shelf.objects.count() + 1}"

        shelf = Shelf.objects.create(user=request.user, name=name)
        return JsonResponse({"success": True, "id": shelf.id, "name": shelf.name})

    return JsonResponse({"success": False, "error": "Método no permitido."})


@csrf_exempt
@login_required
def create_drawer_modal(request):
    """
    Crea un 'Cajón' desde un modal vía AJAX, asignado a un estante.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"success": False, "error": "Datos inválidos"})

        shelf_id = data.get("shelf_id")
        if not shelf_id:
            return JsonResponse({"success": False, "error": "Debes seleccionar un estante."})

        try:
            shelf = Shelf.objects.get(id=shelf_id, user=request.user)
        except Shelf.DoesNotExist:
            return JsonResponse({"success": False, "error": "Estante no encontrado."})

        # Asignar nombre automático en función de la cantidad existente
        count_in_shelf = Drawer.objects.filter(user=request.user, shelf=shelf).count()
        drawer = Drawer.objects.create(
            user=request.user,
            shelf=shelf,
            name=f"C{count_in_shelf + 1}"
        )
        return JsonResponse({"success": True, "id": drawer.id, "name": drawer.name})

    return JsonResponse({"success": False, "error": "Método no permitido."})


@csrf_exempt
@login_required
def create_classification_modal(request):
    """
    Crea una 'Clasificación' desde un modal vía AJAX.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name", "").strip()

        if not name:
            return JsonResponse({"success": False, "error": "El nombre es obligatorio"})
        if Classification.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({"success": False, "error": "Ya existe una clasificación con ese nombre"})

        classification = Classification.objects.create(user=request.user, name=name)
        return JsonResponse({"success": True, "id": classification.id, "name": classification.name})

    return JsonResponse({"success": False, "error": "Método inválido"})


@csrf_exempt
@login_required
def create_gender_modal(request):
    """
    Crea un 'Género' desde un modal vía AJAX, vinculado a una clasificación.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        classification_id = data.get("classification_id")

        if not classification_id:
            return JsonResponse({"success": False, "error": "Debes seleccionar una clasificación"})

        try:
            classification = Classification.objects.get(id=classification_id, user=request.user)
        except Classification.DoesNotExist:
            return JsonResponse({"success": False, "error": "Clasificación inválida"})

        if Gender.objects.filter(user=request.user, classification=classification, name=name).exists():
            return JsonResponse({"success": False, "error": "Ese género ya existe en esta clasificación"})

        genre = Gender.objects.create(user=request.user, classification=classification, name=name)
        return JsonResponse({"success": True, "id": genre.id, "name": genre.name})

    return JsonResponse({"success": False, "error": "Método inválido"})


@csrf_exempt
@login_required
def create_author_modal(request):
    """
    Crea un 'Autor' desde un modal vía AJAX.
    """
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        birth_year = request.POST.get("birth_year")
        death_year = request.POST.get("death_year")
        biography = request.POST.get("biography", "")
        semblance = request.POST.get("semblance", "")
        image = request.FILES.get("image")

        if not first_name or not last_name:
            return JsonResponse({"success": False, "error": "Debe ingresar nombre y apellido."})

        author = Author.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            birth_year=birth_year or None,
            death_year=death_year or None,
            biography=biography,
            semblance=semblance,
            image=image
        )

        return JsonResponse({"success": True, "id": author.id, "name": str(author)})

    return JsonResponse({"success": False, "error": "Método no permitido."})


# -------------------
# AJAX progreso de lectura
# -------------------

@csrf_exempt
@login_required
def save_progress(request, pk):
    """
    Guarda el progreso de lectura (última página) de un 'Libro' vía AJAX.
    """
    if request.method == "POST":
        book = get_object_or_404(Book, pk=pk)
        data = json.loads(request.body)
        page = data.get("last_page", 1)

        progress, _ = ReadingProgress.objects.get_or_create(user=request.user, book=book)
        progress.last_page = page
        progress.save()

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


@csrf_exempt
@login_required
def save_last_page(request):
    """
    Actualiza la última página leída de un 'Libro' vía AJAX.

    - Valida que el libro pertenezca al usuario.
    - Verifica que la página no exceda el total.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            book_id = data.get("book_id")
            last_page = data.get("last_page", 1)

            # Validaciones básicas
            try:
                book_id = int(book_id)
                last_page = int(last_page)
            except (ValueError, TypeError):
                return JsonResponse({"status": "error", "message": "ID de libro o página inválidos"}, status=400)

            book = get_object_or_404(Book, pk=book_id, user=request.user)

            if book.page_count and last_page > book.page_count:
                return JsonResponse({
                    "status": "error",
                    "message": f"La página no puede ser mayor que {book.page_count}"
                }, status=400)

            progress, created = ReadingProgress.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={"last_page": last_page}
            )

            if not created:
                progress.last_page = last_page
                progress.save()

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)
