from django.contrib import admin
from .models import Shelf, Drawer, Classification, Gender, Author, Book

# Register your models here.
@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Drawer)
class DrawerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "shelf")
    list_filter = ("shelf",)
    search_fields = ("name",)


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "classification", "start_date", "end_date")
    list_filter = ("classification",)
    search_fields = ("name", "description")



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "birth_year", "death_year")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "author", "publication_date",
        "volume", "editorial", "genre", "drawer", "cover"
    )
    list_filter = ("genre", "drawer", "cover")
    search_fields = ("title", "subtitle", "editorial", "author__first_name", "author__last_name")
    ordering = ("title",)