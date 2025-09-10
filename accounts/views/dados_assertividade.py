from django.shortcuts import render, get_object_or_404
from ..models import DadosPdfValidado, Interessado

def visualizar_assertividade(request, cliente_id, pdf_id):
    interessado = get_object_or_404(Interessado, id=cliente_id)
    pdf = get_object_or_404(DadosPdfValidado, id_pdf_validado=pdf_id, interessado=interessado)
    print(pdf.resposta_corrigida)
    print(pdf.resposta_gpt)
    print(pdf.campos_corrigidos)
    contexto = {
        'interessado': interessado,
        'pdf': pdf,
        'resposta_corrigida': pdf.resposta_corrigida,
        'resposta_gpt': pdf.resposta_gpt,
        'campos_corrigidos': pdf.campos_corrigidos
    }

    return render(request, 'accounts/assertividade_detalhes.html', contexto)
