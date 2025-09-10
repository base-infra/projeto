from django.shortcuts import render, get_object_or_404 
from accounts.models import PdfFile, PdfValidation, Interessado  
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()
def checklist_criado(request, id):
    print("entrando na funcao def checklist_criado(request, id): ") 

    try:
        pdf = PdfFile.objects.get(id=id)
    except PdfFile.DoesNotExist:
        return HttpResponse("PDF não encontrado", status=404)

    pdf = get_object_or_404(PdfFile, id=id) 
    interessado = pdf.interessado  
    validacao = PdfValidation.objects.filter(pdffile=pdf).order_by("-uploaded_at").first() 

    usuario_responsavel = None
    if validacao and validacao.usuario_id:
        try:
            usuario_responsavel = User.objects.get(id=validacao.usuario_id).username
        except User.DoesNotExist:
            usuario_responsavel = "Usuário não encontrado"

    try:
        pdf = PdfFile.objects.get(id=id)
    except PdfFile.DoesNotExist:
        return HttpResponse("PDF não encontrado", status=404)


    if interessado.tipo_acesso:
        tipo_classificao = "Acesso"
        tipo_projeto = interessado.tipo_acesso
    elif interessado.tipo_ocupacao:
        tipo_classificao = "Ocupação"
        tipo_projeto = interessado.tipo_ocupacao
    elif interessado.tipo_publicidade:
        tipo_classificao = "Publicidade"
        tipo_projeto=interessado.tipo_publicidade
    else:
        tipo_classificao = "Não informado"
        tipo_projeto = "Não informado"

    print("para trace dos pdf")
    print(f"📌 Carregando checklist para o CLIENTE - tb_interessado: {interessado.id}")
    print(f"📌 Carregando checklist para PDF's dos clientes tb_pdf_files: {id}")
    print(f"📌 Carregando checklist para VALIDAÇÃO DO PDF's do clientes pdf_validation: {validacao.id}")
    
    return render(request, "accounts/checklist_criado_layout.html", {
        "interessado": interessado,
        "pdf": pdf,
        "validacao": validacao,
        "usuario_responsavel": usuario_responsavel,
        'tipo_classificao' : tipo_classificao,
        'tipo_projeto' : tipo_projeto,
    })


