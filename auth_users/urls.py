from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('crear_cuenta/', views.create_account, name='create_account'),
    path('logout/', views.log_out, name='log_out'),
]
