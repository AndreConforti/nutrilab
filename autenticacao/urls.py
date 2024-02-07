from django.urls import path
from . import views 


app_name = 'autenticacao'

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logar/', views.logar, name='logar'),
    path('sair/', views.sair, name='sair'),
    path('ativar_conta/<str:token>/', views.ativar_conta, name='ativar_conta'),
]