from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Interessado, DadosPdfValidado
from django.contrib.auth import get_user_model
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()

@login_required
def gerar_checklist(request, cliente_id):
    print("Entrou na gerar_checklist")
    print("Usuário atual:", request.user)
    print("ID do cliente:", cliente_id)
    dados_json = request.GET.get('dados')
    checklist_data  = json.loads(dados_json) if dados_json else {}

    dados_recebidos = {k.lower(): v for k, v in checklist_data.items()}

    print("Dados recebidos:", dados_recebidos )

    interessado = get_object_or_404(Interessado, id=cliente_id)  
    nome_arquivo = request.session.get('nome_arquivo', '')

    print('****************request.session.get(request, cliente_id)')
    print(nome_arquivo)
    print('****************request.session.get(request, cliente_id)')
    if interessado.tipo_acesso:
        tipo_classificao = "Acesso" 
        campo_ocupacao_area = None
    elif interessado.tipo_ocupacao:
        tipo_classificao = "Ocupação" 
        campo_ocupacao_area = interessado.ocupacao_area if interessado.ocupacao_area else None  
    elif interessado.tipo_publicidade:
        tipo_classificao = "Publicidade" 
        campo_ocupacao_area = None
    else:
        tipo_classificao = "Não informado" 
        campo_ocupacao_area = None 
    
    user_logado = request.user

    interessado.data_recebimento = datetime.strptime(interessado.data_recebimento, "%Y-%m-%d") 

    if request.user.is_authenticated: 
        return render(request, 'accounts/gerar_checklist.html', {'cliente_id': cliente_id,
                                                                 'interessado': interessado , 
                                                                 'tipo_classificao': tipo_classificao, 
                                                                 'campo_ocupacao_area': campo_ocupacao_area,
                                                                 'user_logado': user_logado,
                                                                 'checklist_data': dados_recebidos,
                                                                 'nome_arquivo': nome_arquivo}) 


@csrf_exempt
def gerar_checklist_criado(request, cliente_id):
    print(f"⚙️ Recebido gerar_checklist_criado para Interessado ID: {cliente_id}")

    if request.method == 'GET':
        try:
            interessado = Interessado.objects.get(id=cliente_id)
        except Interessado.DoesNotExist:
            return JsonResponse({'error': f'Interessado com id {cliente_id} não encontrado.'}, status=400)

        checklist_data = DadosPdfValidado.objects.filter(interessado=interessado).last()  
        
        if not checklist_data:
            return JsonResponse({'error': 'Nenhum checklist encontrado.'}, status=404)

        if interessado.tipo_acesso:
            tipo_classificao = "Acesso" 
            campo_ocupacao_area = None
        elif interessado.tipo_ocupacao:
            tipo_classificao = "Ocupação" 
            campo_ocupacao_area = interessado.ocupacao_area if interessado.ocupacao_area else None  
        elif interessado.tipo_publicidade:
            tipo_classificao = "Publicidade" 
            campo_ocupacao_area = None
        else:
            tipo_classificao = "Não informado" 
            campo_ocupacao_area = None  
            
        #tive que fazer isso pois o nome das variaveis estava grande e quabrava dentro do if do html    
        loc = checklist_data.localizacao
        km_ini = checklist_data.kilometragem_inicio
        km_fim = checklist_data.kilometragem_fim
        br = checklist_data.nome_br
        return render(request, 'accounts/checklist_criado_layout.html', {'checklist_data': checklist_data,
                                                                         'interessado':interessado, 
                                                                         'tipo_classificao': tipo_classificao, 
                                                                         'campo_ocupacao_area': campo_ocupacao_area,
                                                                         'loc': loc,
                                                                         'km_ini': km_ini,
                                                                         'km_fim': km_fim,
                                                                         'br': br,
                                                                         })
        
@csrf_exempt
def gerar_checklist_criado_analises(request, cliente_id, pdf_id):
    print(f"⚙️ Recebido gerar_checklist_criado_analises para Interessado ID: {cliente_id}, PDF ID: {pdf_id}")

    try:
        interessado = Interessado.objects.get(id=cliente_id)
        checklist_data = DadosPdfValidado.objects.get(id_pdf_validado=pdf_id, interessado=interessado)
    except Interessado.DoesNotExist:
        return JsonResponse({'error': f'Interessado com id {cliente_id} não encontrado.'}, status=400)
    except DadosPdfValidado.DoesNotExist:
        return JsonResponse({'error': f'PDF com id {pdf_id} não encontrado para este interessado.'}, status=404)

    if interessado.tipo_acesso:
        tipo_classificao = "Acesso"
        campo_ocupacao_area = None
    elif interessado.tipo_ocupacao:
        tipo_classificao = "Ocupação"
        campo_ocupacao_area = interessado.ocupacao_area if interessado.ocupacao_area else None
    elif interessado.tipo_publicidade:
        tipo_classificao = "Publicidade"
        campo_ocupacao_area = None
    else:
        tipo_classificao = "Não informado"
        campo_ocupacao_area = None

    loc = checklist_data.localizacao
    km_ini = checklist_data.kilometragem_inicio
    km_fim = checklist_data.kilometragem_fim
    br = checklist_data.nome_br

    return render(request, 'accounts/checklist_criado_layout.html', {
        'checklist_data': checklist_data,
        'interessado': interessado,
        'tipo_classificao': tipo_classificao,
        'campo_ocupacao_area': campo_ocupacao_area,
        'loc': loc,
        'km_ini': km_ini,
        'km_fim': km_fim,
        'br': br,
    })