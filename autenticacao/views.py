from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import Http404

from .utils import password_is_valid, email_html
from .models import Ativacao

from hashlib import sha256

import os


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')        
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')

        try:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=senha,
                                            is_active=False
                                            )
            user.save()

            ## O token vai ser o nome do usário e a senha. 
            ## O sha256 precisa que essa string esteja em binário, por isso o encode() para converter em binário
            ## O sha256 retorna um método (um endereço de memória) que precisa ser convertido para hexadecimal, por isso o hexdigest
            token = sha256(f'{username}{email}'.encode()).hexdigest()

            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            ## Pega o conteúdo do HTML que vai ser enviado
            html_content = render_to_string('emails/cadastro_confirmado.html', {'nome': username, 'link_ativacao': f"http://127.0.0.1:8000/auth/ativar_conta/{token}"})   # path_do_template / context
            ## Faz a conversão do HTML para TXT. Remove tudo que seja parecido com uma tag HTML
            text_content = strip_tags(html_content)

            ## Assunto / Body / Quem está enviando / Pra quem será enviado
            email = EmailMultiAlternatives('Confirmação de Cadastro', text_content, settings.EMAIL_HOST_USER, [email])

            ## Envio do email - Conteúdo / Formato
            email.attach_alternative(html_content, 'text/html')

            email.send()

            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso!')
            return redirect('/auth/logar')
        except:
            messages.add_message(request, constants.WARNING, 'Erro interno do sistema')
            return redirect('/auth/cadastro')
        
        ## andre / Andre10


def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

        usuario = authenticate(username=username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Nome de usuário ou senha inválidos.')
            return redirect('/auth/logar')
        else:
            login(request, usuario)
            return redirect('/pacientes')


def sair(request):
    logout(request)
    return redirect('/auth/logar')


def ativar_conta(request, token):
    try:
        token = get_object_or_404(Ativacao, token=token) ## Verifica se esse token existe. Caso contrário retorna una página 404
    except Http404:
        messages.add_message(request, constants.ERROR, f'O token não está cadastrado')
        return redirect('/auth/logar') 
    else:        
        if token.ativo:
            messages.add_message(request, constants.WARNING, 'Esse token já foi usado')
            return redirect('/auth/logar')
        
        user = User.objects.get(username=token.user.username)
        user.is_active = True
        user.save()

        token.ativo = True
        token.save()

        messages.add_message(request, constants.SUCCESS, 'Conta ativada com sucesso')
        return redirect('/auth/logar')