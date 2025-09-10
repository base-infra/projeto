from django.shortcuts import render, redirect
from accounts.forms.cadastro_form import CadastroForm
from accounts.models import Interessado , PdfFile
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model  
from django.http import JsonResponse
from django.db.models import Q
User = get_user_model()

def cadastro_view(request):
    print("entrou def cadastro_view(request):")
    """
    Exibe o formulário de cadastro e salva os dados no banco.
    Redireciona para a listagem de interessados após salvar.
    """
    
    if request.method == 'POST':
        form = CadastroForm(request.POST) 
        if form.is_valid():
            cliente  = form.save(commit=False)  
            # interessado.usuario_id = request.user
            cliente.usuario = User.objects.get(pk=request.user.pk)
            cliente.save() 
            clientes = Interessado.objects.all()
            paginator = Paginator(clientes, 10)  # 10 registros por página
            page_number = request.GET.get('page', 1)  # Define página padrão como 1
            page_obj = paginator.get_page(page_number)
            clientes.usuario_id = request.user
            return redirect('listar_clientes')
        else:
            print(form.errors)
    else:
        form = CadastroForm()

    return render(request, 'accounts/cadastro_form.html', {'form': form, 'user': request.user})

def listar_clientes(request): 
    """
    Lista todos os Clientes salvos no banco de dados e renderiza a página de listagem.
    """
    cliente = Interessado.objects.all()
    # Adiciona paginação
    paginator = Paginator(cliente, 10)  # 10 registros por página
    page_number = request.GET.get('page', 1)  # Define página padrão como 1
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/clientes.html', {'page_obj': page_obj}) 
 
def editar_clientes(request, id):
    """
    Exibe o formulário de edição ou cadastro para um registro específico e salva as alterações.
    """
    print('aqui def editar_clientes(request, id):')
    if id:  # Caso seja edição
        cliente = get_object_or_404(Interessado, id=id)
    else:  # Caso seja cadastro
        cliente = None

    if request.method == 'POST':
        form = CadastroForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')  # Use o nome da URL associada a 'accounts/clientes.html'
    else:
        form = CadastroForm(instance=cliente)

    return render(request, 'accounts/cadastro_form.html', {
        'form': form, 
        'editar': bool(cliente),
    })

def excluir_interessado(request, id):
    """
    Exclui um registro específico do banco de dados.
    """

    print('aqui def editar_clientes(request, id):')
    interessado = get_object_or_404(Interessado, id=id)
    if request.method == 'POST':
        interessado.delete()
        cliente = Interessado.objects.all()
            # Adiciona paginação
        paginator = Paginator(cliente, 10)  # 10 registros por página
        page_number = request.GET.get('page', 1)  # Define página padrão como 1
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'accounts/clientes.html', {'page_obj': page_obj}) 

    return render(request, 'accounts/confirmar_exclusao.html', {'interessado': interessado})

def overview_cliente(request, id): 
    print("aquiiiiii def overview_cliente(request, id):")
    cliente = get_object_or_404(Interessado, id=id)  # Busca um único cliente
    if cliente.tipo_acesso:
        tipo_classificao = "Acesso" 
        campo_ocupacao_area = None
    elif cliente.tipo_ocupacao:
        tipo_classificao = "Ocupação" 
        campo_ocupacao_area = cliente.ocupacao_area if cliente.ocupacao_area else None  # Define como None se estiver vazio
    elif cliente.tipo_publicidade:
        tipo_classificao = "Publicidade" 
        campo_ocupacao_area = None
    else:
        tipo_classificao = "Não informado" 
        campo_ocupacao_area = None 

    print(f"Filtrando PDFs para o cliente {cliente} com status_pdf=False")
    pdfs = PdfFile.objects.filter(interessado=cliente, status_pdf=False).order_by("-uploaded_at")

    if pdfs.exists():
        print(f"PDFs encontrados: {pdfs.count()}")
        print(f"Primeiro PDF ID: {pdfs.first().id}")  # Pegando o primeiro elemento
    else:
        print("Nenhum PDF encontrado")


        # 🚀 **Tratando requisições POST**
    if request.method == "POST":
        try:
            # Aqui você pode adicionar lógica para processar dados do POST
            data = request.POST  # Captura os dados enviados no request
            print(f"📩 Dados recebidos via POST: {data}")

            # Exemplo de resposta JSON (pode ser alterado conforme necessidade)
            return JsonResponse({"message": "Requisição POST processada com sucesso!", "status": "success"})
        
        except Exception as e:
            print(f"❌ Erro ao processar requisição POST: {e}")
            return JsonResponse({"error": str(e), "status": "error"}, status=400)

    # 🚀 **Tratando requisições GET**
    return render(request, 'accounts/cliente_overview.html', {
        'cliente': cliente,
        'campo_tipo_classificao': tipo_classificao,
        'campo_ocupacao_area': campo_ocupacao_area,
        'pdfs': pdfs
    }) 

def listar_clientes(request): 
    """
    Lista os Clientes com suporte a pesquisa por ID, nome ou número do processo.
    """
    query = request.GET.get('q')  # Valor digitado na barra de pesquisa
    if query:
        cliente = Interessado.objects.filter(
            Q(id__icontains=query) |
            Q(nome__icontains=query) |
            Q(nro_processo__icontains=query)
        )
    else:
        cliente = Interessado.objects.all()
    
    paginator = Paginator(cliente, 10)  # 10 registros por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/clientes.html', {
        'page_obj': page_obj,
        'query': query,  # opcional: útil se quiser manter o valor no input
    })
