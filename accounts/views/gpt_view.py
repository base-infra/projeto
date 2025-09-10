from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from accounts.models import PdfValidation, PdfFile
from ..models import Interessado
from django.shortcuts import render, get_object_or_404
from accounts.models import historico_analise_pdf
 
def mostrar_popup_dados(request):
    print('def mostrar_popup_dados(request):')
    """ View para exibir a modal com os dados do cliente e os extraídos da IA """
    print(request.method)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            cliente_id = data.get("cliente_id")  # Obtém o ID do cliente enviado pelo AJAX
            dados_chatgpt = data.get("dados_chatgpt", {})
            print('passou')
            if not cliente_id:
                return JsonResponse({"error": "ID do cliente não informado."}, status=400)

            cliente = get_object_or_404(Interessado, id=cliente_id)
            print(cliente.id)

            if request.FILES.get("pdf"):
                pdf_file = request.FILES["pdf"]
                pdf_name = pdf_file.name
                dados_chatgpt["pdf_name"] = pdf_name
            # Passar os dados para o template da modal
            return render(request, "accounts/popup_dados_gpt.html", {
                "cliente": cliente,
                "dados_chatgpt": dados_chatgpt
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao processar os dados enviados."}, status=400)

    return JsonResponse({"error": "Método inválido."}, status=405)


 
@csrf_exempt
def salvar_dados_pdf(request):
    if request.method == "POST":
        try:
            # Capturar os dados do POST
            data = json.loads(request.body.decode("utf-8"))
            print("📥 Dados recebidos para salvar: def salvar_dados_pdf(request):", data)

            descricao_pdf = data.get('descricao_pdf')  # <- aqui
            print("🔍 Descrição recebida:", descricao_pdf)

            # Verificar se o ID do interessado (cliente) está presente
            interessado_id = data.get("interessado_id")
            if not interessado_id:
                print("❌ Erro: ID do cliente não fornecido.")
                return JsonResponse({"error": "ID do cliente não fornecido."}, status=400)

            # Buscar o cliente no banco de dados
            try:
                interessado = get_object_or_404(Interessado, id=interessado_id)
            except Exception as e:
                print(f"❌ Erro ao buscar o cliente: {str(e)}")
                return JsonResponse({"error": f"Erro ao identificar o cliente. Atualize a página e tente novamente. func def salvar_dados_pdf(request)"}, status=400)

            # Criar e salvar o novo registro em `PdfValidation`
            pdf_validation = PdfValidation.objects.create(
                interessado=interessado,
                localizacao=data.get("localizacao", ""),
                etapa=data.get("etapa", ""),
                projeto=data.get("projeto", ""),
                proprietario_cliente=data.get("proprietario_cliente", ""),
                responsavel_tecnico=data.get("responsavel_tecnico", ""),
                prancha=data.get("prancha", ""),
                ocupacao=data.get("ocupacao", ""),
                escala=data.get("escala", ""),
                usuario=request.user  # Associa o usuário autenticado
            )

 
            pdf_file = PdfFile(
                interessado_id=interessado.id,
                usuario_id=request.user.id,
                pdf_validation_id=pdf_validation.id,
                nome_pdf=data.get("pdf_name", ""),
                versao=1,
                status_pdf=False,
                descricao_pdf_upload=descricao_pdf
            )
            pdf_file.save()
            print(f"✅ PDF Validation salvo com ID {pdf_validation.id}")
 
            # Resetar a contagem de reanálise
            if "reanalisar_tentativas" in request.session:
                del request.session["reanalisar_tentativas"]
                print("🔄 Contador de reanálise resetado.")

            return JsonResponse({
                "message": "Dados salvos com sucesso!",
                "status": "success",
                "pdf_validation_id": pdf_validation.id
            })

        except json.JSONDecodeError as e:
            print(f"❌ Erro ao processar JSON: {e}")
            return JsonResponse({"error": f"Erro ao processar JSON: {str(e)}"}, status=400)

        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return JsonResponse({"error": f"Erro interno no servidor: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método inválido"}, status=405)
