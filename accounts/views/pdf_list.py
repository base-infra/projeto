from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404 
from accounts.models import PdfFile, Interessado, DadosPdfValidado
from django.db.models import Q 

def list_pdf_validado_ajax(request, interessado_id):
    print("📌 Função `list_pdf_validado_ajax` chamada para o interessado:", interessado_id)
    interessado = get_object_or_404(Interessado, id=interessado_id)
    pdfs_validado = DadosPdfValidado.objects.filter(interessado=interessado).order_by("-id_pdf_validado")

    page = request.GET.get("page", 1)
    paginator = Paginator(pdfs_validado, 5)

    try:
        pdfs_page = paginator.page(page)
    except:
        pdfs_page = paginator.page(1)

    # Retorna apenas o fragmento da tabela
    return render(request, "partials/lista_pdfs_validado.html", {"pdfs": pdfs_page})
    


def recuperar_checklist(request, interessado_id, pdfvalidado_id):
    print("📌 Função `recuperar_checklist` chamada para o interessado e id do pdf especifico:", interessado_id, pdfvalidado_id)

    interessado = get_object_or_404(Interessado, id=interessado_id)

    pdf_recuperado = get_object_or_404(
        DadosPdfValidado,
        interessado=interessado,
        id_pdf_validado=pdfvalidado_id
    )

    if interessado.tipo_acesso:
        tipo_classificacao = "Acesso" 
        campo_ocupacao_area = None
    elif interessado.tipo_ocupacao:
        tipo_classificacao = "Ocupação" 
        campo_ocupacao_area = interessado.ocupacao_area if interessado.ocupacao_area else None  
    elif interessado.tipo_publicidade:
        tipo_classificacao = "Publicidade" 
        campo_ocupacao_area = None
    else:
        tipo_classificacao = "Não informado" 
        campo_ocupacao_area = None 
    print(tipo_classificacao)
    print(campo_ocupacao_area)
    return render(request, 'accounts/recuperar_checklist.html', {'checklist_data': pdf_recuperado, 
                                                                 'tipo_classificacao': tipo_classificacao,
                                                                 'campo_ocupacao_area': campo_ocupacao_area})

def list_pdf_cliente(request, interessado_id):
    print("📌 Função `list_pdf_cliente` chamada para o interessado:", interessado_id)

    interessado = get_object_or_404(Interessado, id=interessado_id)

    # Filtrar PDFs validados desse interessado
    pdfs = DadosPdfValidado.objects.filter(interessado=interessado).order_by("-data_upload")

    page = request.GET.get("page", 1)
    items_per_page = 5

    paginator = Paginator(pdfs, items_per_page)

    try:
        pdfs_page = paginator.page(page)
    except:
        pdfs_page = paginator.page(1)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print(f"✅ Enviando página {page} com {len(pdfs_page)} itens")
        return render(request, "partials/lista_pdfs_ajax.html", {"pdfs": pdfs_page})
        
# def list_pdf_cliente(request, interessado_id):
#     print("📌 Função `list_pdf_cliente` chamada para o interessado:", interessado_id)

#     interessado = get_object_or_404(Interessado, id=interessado_id)

#     # Filtrar apenas PDFs não aprovados
#     pdfs = PdfFile.objects.filter(interessado=interessado, status_pdf=False).order_by("-uploaded_at")

#     # 🔹 PAGINAÇÃO 🔹
#     page = request.GET.get("page", 1)  # Página atual (padrão = 1)
#     items_per_page = 5  # Quantidade de PDFs por página

#     paginator = Paginator(pdfs, items_per_page)

#     try:
#         pdfs_page = paginator.page(page)
#     except:
#         pdfs_page = paginator.page(1)  # Se a página for inválida, carregar a primeira

#     # 🔹 Se for uma requisição AJAX, retorna apenas a tabela sem recarregar a página inteira
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         print(f"✅ Enviando página {page} com {len(pdfs_page)} itens")  # DEBUG
#         return render(request, "partials/lista_pdfs_ajax.html", {"pdfs": pdfs_page})
 

def listar_checklists(request):
    print("📌 Função `listar_checklists` de todos os clientes:")

    pdfs = DadosPdfValidado.objects.all().order_by("-data_upload")
    print(f"🔍 PDFs encontrados: {pdfs.count()}")

    for pdf in pdfs[:5]:  # Mostra os 5 primeiros como exemplo
        print(f"📄 PDF: {pdf.nome_arquivo} - Interessado: {pdf.interessado.nome} - Data: {pdf.data_upload}")

    page = request.GET.get("page", 1)
    items_per_page = 20
    paginator = Paginator(pdfs, items_per_page)

    try:
        pdfs_page = paginator.page(page)
    except:
        pdfs_page = paginator.page(1)

    return render(request, "accounts/listar_checklists.html", {
        "pdfs": pdfs_page,
        "page_obj": pdfs_page
    })


# def listar_checklists(request):
#     print("📌 Função `listar_checklists` de todos os clientes:")

#     # Buscar todos os PDFs não aprovados de todos os clientes
#     pdfs = PdfFile.objects.all().order_by("-uploaded_at")
 

#     # print(f"🔍 PDFs encontrados: {pdfs.count()}")
#     # for pdf in pdfs:
#     #     print(f"📄 PDF: {pdf.nome_pdf} - Cliente: {pdf.interessado.nome}")


#     # Paginação
#     page = request.GET.get("page", 1)
#     items_per_page = 20
#     paginator = Paginator(pdfs, items_per_page)

#     try:
#         pdfs_page = paginator.page(page)
#     except:
#         pdfs_page = paginator.page(1) 

#     return render(request, "accounts/listar_checklists.html", {
#         "pdfs": pdfs_page,
#         "page_obj": pdfs_page   
#     })


def listar_query_checklists(request): 
    print("📌 Função `listar_query_checklists` com DadosPdfValidado:")
    query = request.GET.get('q')

    if query:
        cliente = DadosPdfValidado.objects.filter(
            Q(id_pdf_validado__icontains=query) |
            Q(nome_arquivo__icontains=query) |
            Q(interessado__nome__icontains=query) |
            Q(interessado__nro_processo__icontains=query)
        ).order_by("-data_upload")
    else:
        cliente = DadosPdfValidado.objects.all().order_by("-data_upload")
    
    paginator = Paginator(cliente, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'pdfs': page_obj,
        'page_obj': page_obj,
        'query': query,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print(f"✅ Requisição AJAX detectada")
        return render(request, "partials/lista_pdfs_ajax_especifico.html", context)
    
    return render(request, 'accounts/listar_checklists.html', context)
# def listar_query_checklists(request): 
#     print("📌 Função `listar_query_checklists` de um cliente específico:")
#     query = request.GET.get('q')

#     if query:
#         cliente = PdfFile.objects.filter(
#             Q(id__icontains=query) |
#             Q(nome_pdf__icontains=query) |
#             Q(interessado__nome__icontains=query) |
#             Q(interessado__nro_processo__icontains=query)
#         )
#     else:
#         cliente = PdfFile.objects.all()
    
#     paginator = Paginator(cliente, 20)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'pdfs': page_obj,
#         'page_obj': page_obj,
#         'query': query,
#     }

#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         print(f"✅ Requisição AJAX detectada")
#         return render(request, "partials/lista_pdfs_ajax_especifico.html", context)
    
#     return render(request, 'accounts/listar_checklists.html', {
#     'pdfs': page_obj,
#     'page_obj': page_obj,
#     'query': query,
#     }) 
