from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Pacientes, DadosPaciente, Refeicao, Opcao

from datetime import datetime

@login_required(login_url='/auth/logar')
def pacientes(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')

        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')

        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')

        pacientes = Pacientes.objects.filter(email=email)

        if pacientes.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')

        try:
            paciente = Pacientes(
                nome=nome,
                sexo=sexo,
                idade=idade,
                email=email,
                telefone=telefone,
                nutri=request.user,
            )
            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
        finally:
            return redirect('/pacientes/')


@login_required(login_url='/auth/logar')
def dados_paciente_listar(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})
    

@login_required(login_url='/auth/logar')
def dados_paciente(request, id):
    try:
        paciente = get_object_or_404(Pacientes, id=id) ## Verifica se esse paciente existe. Caso contrário retorna una página 404
    except Http404:
        messages.add_message(request, constants.ERROR, f'Paciente com o ID {id} não está cadastrado')
        return redirect('/dados_paciente/')   
    else:    ## somente será efetuado caso o try for bem-sucedido
        if not paciente.nutri == request.user:  ## Verifica se o paciente é do usuário (nutricionista) que está logado
            messages.add_message(request, constants.ERROR, 'Não é possível acessar os pacientes de outro usuário.')
            return redirect('/dados_paciente/')
        if request.method == 'GET':
            dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
            return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})
        elif request.method == "POST":
            # TODO: realizar as validações para preenchimento dos campos corretamente
            peso = request.POST.get('peso')
            altura = request.POST.get('altura')
            gordura = request.POST.get('gordura')
            musculo = request.POST.get('musculo')

            hdl = request.POST.get('hdl')
            ldl = request.POST.get('ldl')
            colesterol_total = request.POST.get('ctotal')
            triglicerídios = request.POST.get('triglicerídios')

            paciente = DadosPaciente(paciente=paciente,
                                data=datetime.now(),
                                peso=peso,
                                altura=altura,
                                percentual_gordura=gordura,
                                percentual_musculo=musculo,
                                colesterol_hdl=hdl,
                                colesterol_ldl=ldl,
                                colesterol_total=colesterol_total,
                                trigliceridios=triglicerídios)

            paciente.save()

            messages.add_message(request, constants.SUCCESS, 'Dados cadastrado com sucesso')

            return redirect('/dados_paciente/')
        

@login_required(login_url='/auth/logar')
@csrf_exempt  ## Desativa a verificação CSRF (Cross-Site Request Forgery) / usamos quando um serviço externo não inclui automaticamente os cabeçalhos CSRF
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by('data')

    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {
        'peso': pesos,
        'labels': labels,
    }
    return JsonResponse(data)


def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})
    

def plano_alimentar(request, id):
    try:
        paciente = get_object_or_404(Pacientes, id=id) ## Verifica se esse paciente existe. Caso contrário retorna una página 404
    except Http404:
        messages.add_message(request, constants.ERROR, f'Paciente com o ID {id} não está cadastrado')
        return redirect('/dados_paciente/')  
    else:    ## somente será efetuado caso o try for bem-sucedido
        if not paciente.nutri == request.user:  ## Verifica se o paciente é do usuário (nutricionista) que está logado
            messages.add_message(request, constants.ERROR, 'Não é possível acessar os pacientes de outro usuário.')
            return redirect('/dados_paciente/')

        if request.method == "GET":
            refeicoes = Refeicao.objects.filter(paciente=paciente).order_by('horario')
            opcoes = Opcao.objects.all()
            content = {
                'paciente': paciente,
                'refeicoes': refeicoes,
                'opcoes': opcoes,
            }
            return render(request, 'plano_alimentar.html', content)
        

def refeicao(request, id_paciente):
    try:
        paciente = get_object_or_404(Pacientes, id=id_paciente) ## Verifica se esse paciente existe. Caso contrário retorna una página 404
    except Http404: ## Se retornar 404, manda uma mensagem de volta e redireciona
        messages.add_message(request, constants.ERROR, f'Paciente com o ID {id} não está cadastrado')
        return redirect('/dados_paciente/')  
    else:    ## somente será efetuado caso o try for bem-sucedido
        if not paciente.nutri == request.user:  ## Verifica se o paciente é do usuário (nutricionista) que está logado
            messages.add_message(request, constants.ERROR, 'Não é possível acessar os pacientes de outro usuário.')
            return redirect('/dados_paciente/')

        if request.method == "POST":
            titulo = request.POST.get('titulo')
            horario = request.POST.get('horario')
            carboidratos = request.POST.get('carboidratos')
            proteinas = request.POST.get('proteinas')
            gorduras = request.POST.get('gorduras')

            # TODO: verificar se todos os campos foram preenchidos e validados
            refeicao = Refeicao(paciente=paciente,
                        titulo=titulo,
                        horario=horario,
                        carboidratos=carboidratos,
                        proteinas=proteinas,
                        gorduras=gorduras)

            refeicao.save()

            messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
            return redirect(f'/plano_alimentar/{id_paciente}')
        

def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")

        opcao = Opcao(refeicao_id=id_refeicao,
                   imagem=imagem,
                   descricao=descricao)

        opcao.save()

        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')
    


## TODO: realizar os procedimentos para exportar o PDF