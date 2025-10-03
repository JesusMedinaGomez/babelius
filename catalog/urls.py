from django.urls import path
from . import views

urlpatterns = [
    # Encadenados
    path("ajax/load-drawers/", views.load_drawers, name="ajax_load_drawers"),
    path("ajax/load-genres/", views.load_genres, name="ajax_load_genres"),
    # Create
    path('crear_estante/', views.create_shelf, name='create_shelf'),
    path('crear_cajon/', views.create_drawer, name='create_drawer'),
    path('crear_clasificacion/', views.create_classification, name='create_classification'),
    path('crear_genero/', views.create_gender, name='create_gender'),
    path('crear_autor/', views.create_author, name='create_author'),
    path('crear_libro/', views.create_book, name='create_book'),
    path("babels/create/", views.create_babel, name="create_babel"),
    path("babels/<int:pk>/", views.detail_babel, name="detail_babel"),

    # Read
    path('libros/', views.read_books, name='read_books'),
    path('autores/', views.read_authors, name='read_authors'),
    path('clasificaciones/', views.read_classifications, name='read_classifications'),
    path('generos/', views.read_genders, name='read_genders'),
    path('estantes/', views.read_shelfs, name='read_shelfs'),
    path('cajones/', views.read_drawers, name='read_drawers'),
    path('save_last_page/', views.save_last_page, name='save_last_page'),
    path('book/<int:pk>/read/', views.read_pdf, name='read_pdf'),
    path('book/<int:pk>/read_physical/', views.read_physical, name='read_physical'),
    path("babels/", views.read_babels, name="read_babels"),

    # Update
    path('editar_libro/<int:pk>/', views.update_book, name='update_book'),
    path('editar_autor/<int:pk>/', views.update_author, name='update_author'),
    path('editar_clasificacion/<int:pk>/', views.update_classification, name='update_classification'),
    path('editar_genero/<int:pk>/', views.update_gender, name='update_gender'),
    path('editar_estante/<int:pk>/', views.update_shelf, name='update_shelf'),
    path("babels/<int:pk>/update/", views.update_babel, name="update_babel"),

    # Delete
    path('eliminar_libro/<int:pk>/', views.delete_book, name='delete_book'),
    path('eliminar_autor/<int:pk>/', views.delete_author, name='delete_author'),
    path('eliminar_clasificacion/<int:pk>/', views.delete_classification, name='delete_classification'),
    path('eliminar_genero/<int:pk>/', views.delete_gender, name='delete_gender'),
    path('eliminar_estante/<int:pk>/', views.delete_shelf, name='delete_shelf'),
    path('eliminar_cajon/<int:pk>/', views.delete_drawer, name='delete_drawer'),
    path("babels/<int:pk>/delete/", views.delete_babel, name="delete_babel"),

    # Details
    path('estante/<int:pk>/', views.detail_shelf, name='detail_shelf'),
    path('cajon/<int:pk>/', views.detail_drawer, name='detail_drawer'),
    path('genero/<int:pk>/', views.detail_gender, name='detail_gender'),
    path('autor/<int:pk>/', views.detail_author, name='detail_author'),
    path('libro/<int:pk>/', views.detail_book, name='detail_book'),

    # Modales
    path("crear_estante_modal/", views.create_shelf_modal, name="crear_shelf_modal"),
    path("crear_cajon_modal/", views.create_drawer_modal, name="crear_drawer_modal"),
    path("crear_clasificacion_modal/", views.create_classification_modal, name="crear_classification_modal"),
    path("crear_genero_modal/", views.create_gender_modal, name="crear_gender_modal"),
    path("crear_autor_modal/", views.create_author_modal, name="crear_author_modal"),
]
