###########################################################################################
#                                                                                        #
#                                   AUTHENTICATION VIEWS                                 #
#                                                                                        #
#   Este archivo contiene las vistas relacionadas con autenticación de usuarios.          #
#   Permite registrar nuevos usuarios, iniciar sesión y cerrar sesión.                    #
#                                                                                        #
#   Estructura del archivo:                                                              #
#                                                                                        #
#   1. create_account  -> Registro de un nuevo usuario con validaciones básicas.          #
#   2. user_login      -> Inicio de sesión con verificación de credenciales.              #
#   3. log_out         -> Cierre de sesión y redirección al home.                         #
#                                                                                        #
#   Convenciones:                                                                        #
#     - Todas las vistas devuelven mensajes de error claros al usuario.                   #
#     - Se utiliza el sistema de autenticación de Django (authenticate, login, logout).   #
#     - Tras el login o creación de cuenta se redirige siempre a 'home'.                  #
#                                                                                        #
###########################################################################################

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def create_account(request):
    """
    Vista para crear una cuenta de usuario.

    - Valida campos obligatorios.
    - Verifica que las contraseñas coincidan.
    - Comprueba que el usuario no exista previamente.
    - Si es válido, crea el usuario y lo autentica automáticamente.
    """
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if not username or not password1 or not password2:
            error = "Todos los campos son obligatorios"
        elif password1 != password2:
            error = "Las contraseñas no coinciden"
        elif User.objects.filter(username=username).exists():
            error = "Este usuario ya existe"
        else:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect('home')

    return render(request, "create_account.html", {"error": error})


def user_login(request):
    """
    Vista para iniciar sesión de usuario.

    - Valida campos obligatorios.
    - Verifica credenciales con `authenticate`.
    - Si son correctas, inicia sesión y redirige a 'home'.
    """
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if not username or not password:
            error = "Todos los campos son obligatorios"
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                error = "Usuario o contraseña incorrectos"

    return render(request, "login.html", {"error": error})


def log_out(request):
    """
    Vista para cerrar sesión de usuario.
    """
    logout(request)
    return redirect('home')
