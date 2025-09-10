from django.shortcuts import render,  get_object_or_404 
from ..models import Interessado
from django.shortcuts import render 
from PyPDF2 import PdfReader
import io 
from accounts.models import PdfValidation, Interessado , PdfFile
from difflib import SequenceMatcher
from django.contrib.auth import get_user_model 
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json   
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML   
from django.conf import settings 
from django.core.files.storage import default_storage 
import re
from accounts.models import historico_analise_pdf

# Carregar variáveis de ambiente
# Caminho absoluto para o .env

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("🚨 ERRO: OPENAI_API_KEY não foi encontrada! Verifique o .env 🚨")
client = OpenAI(api_key=OPENAI_API_KEY)

# def extract_text_from_pdf(pdf_path):
#     """ Extrai o texto de um arquivo PDF """
#     text = ""
#     try:
#         with fitz.open(pdf_path) as doc:
#             for page in doc:
#                 text += page.get_text("text") + "\n"
#     except Exception as e:
#         return f"Erro ao processar PDF: {str(e)}"
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

def extract_text_from_pdf(pdf_path):
    """ Extrai o texto de um arquivo PDF usando PyPDF2 """
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""  # Garantir que None não quebre a concatenação
    except Exception as e:
        return f"Erro ao processar PDF: {str(e)}"
    text = re.sub(r'\s+', ' ', text).strip()
    return text


User = get_user_model()

def extract_pdf_content(pdf_file):
    # Extrai o texto completo do PDF
    reader = PdfReader(pdf_file)
    content = ""
    for page in reader.pages:
        content += page.extract_text()
    return content

def call_api_chatGPT(str_propmt): 
    # Enviar para a API do ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": str_propmt}],
            max_tokens=1500  
        )
        chatgpt_response = response.choices[0].message.content.strip()
        # print(f"Resposta da API OpenAI: {chatgpt_response}")

        # Remover delimitadores de bloco de código (```json ... ```)
        if chatgpt_response.startswith("```json"):
            chatgpt_response = chatgpt_response[7:]  
        if chatgpt_response.endswith("```"):
            chatgpt_response = chatgpt_response[:-3]  

        # Converter string JSON em dicionário
        chatgpt_data = json.loads(chatgpt_response)
        return chatgpt_data

    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Erro ao decodificar JSON: {str(e)}"}, status=500)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Erro ao chamar OpenAI: {str(e)}"}, status=500)


@csrf_exempt 
def reanalisar_dados_pdf(request):
    print("📢 Função `reanalisar_dados_pdf` foi chamada!")

    if request.method == "POST":
        try:
            if "reanalisar_tentativas" not in request.session:
                request.session["reanalisar_tentativas"] = 0

            # Captura os dados enviados pelo frontend
            dados_reanalise = json.loads(request.body.decode("utf-8"))
            campos_para_reanalise = dados_reanalise.get("campos", [])
            cache_dados = dados_reanalise.get("cache_dados", {})

            print("📥 Campos Recebidos para Reanálise:", campos_para_reanalise)
            print("📦 Cache dos Dados Recebido:", cache_dados)

            if not campos_para_reanalise:
                return JsonResponse({"error": "Nenhum campo marcado para reanálise."}, status=400)

            extracted_text = request.session.get("ultimo_texto_pdf", "")
            if not extracted_text:
                return JsonResponse({"error": "Nenhum texto disponível para análise."}, status=400)

            # Gera um novo prompt, focando nos campos específicos
            prompt = prompt_chatGPT(extracted_text, campos_para_reanalise)
            # print("✍️ Novo Prompt Gerado:\n", prompt)

            # Chama a IA para reanalisar os dados
            novos_dados = call_api_chatGPT(prompt)

            # Incrementa a contagem de tentativas na sessão
            request.session["reanalisar_tentativas"] += 1 
            request.session.modified = True

            # 🚀 **Correção para evitar retorno de array**
            resultado_reanalise = {
                "status": "sucesso",
                "tentativas_restantes": 3 - request.session["reanalisar_tentativas"],
                "campos_reanalisados": {}
            }

            for campo in campos_para_reanalise:
                valor = novos_dados.get(campo, "Valor não encontrado")

                # Se o valor retornado for um array, substituímos por "análise inconclusiva"
                if isinstance(valor, list):
                    print(f"⚠️ Campo '{campo}' retornou um array. Substituindo por 'análise inconclusiva'.")
                    valor = "análise inconclusiva"
                
                resultado_reanalise["campos_reanalisados"][campo] = valor

            # print("🔄 Resposta gerada:", resultado_reanalise)
            return JsonResponse({
                "message": "Reanálise concluída!",
                "resultado": resultado_reanalise
            })

        except json.JSONDecodeError as e:
            print("❌ Erro ao decodificar JSON:", str(e))
            return JsonResponse({"error": f"Erro ao processar JSON: {str(e)}"}, status=400)

        except Exception as e:
            print("❌ Erro inesperado:", str(e))
            return JsonResponse({"error": f"Erro interno no servidor: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método inválido"}, status=405)




def prompt_chatGPT(extracted_text, campos_para_reanalise=None):
    """
    Gera um novo prompt considerando os campos que precisam de reanálise.
    Se campos_para_reanalise for passado, a IA só analisará esses campos.
    """
    if campos_para_reanalise:
        print("**ATUALIZAÇÃO DE DADOS - REANÁLISE**")
        campos_str = ", ".join(campos_para_reanalise)
        prompt = f"""
            ⚠️ **ATUALIZAÇÃO DE DADOS - REANÁLISE** ⚠️
            Alguns dados extraídos anteriormente foram considerados incorretos pelo usuário.
            Refaça a análise **somente para os seguintes campos**: {campos_str}.

            **Texto original do PDF para análise:**  
            {extracted_text[:3000]}
            
            **Formato da Resposta:** json  
            Retorne **apenas** os campos reanalisados no formato correto.
        """ 
        print(f'prompt que estamos solicitando reanalise::::{prompt}')
    else:
        print("**PRIMEIRA ANALISE**")
        prompt = f"""
            Analise o seguinte texto extraído de um documento PDF e identifique as seguintes informações:

            1. **Localização ou localidade** (deve incluir BR, PR, RODOVIA ou aparecer no campo 'LOCALIDADE:').
            2. **Cliente ou proprietário** (qualquer nome associado ao cliente ou proprietário DESCONSIDERAR REROND GOULART).
            3. **Sentido da obra/rodovia** (exemplo: sentido Curitiba ou sentido Paranaguá).
            4. **KM de Início e Fim**: Procure por expressões como "trecho da obra", "km de início da obra" e extraia os valores seguindo a máscara **XX+XXX** (ex: **54+710** e **68+503**). Considere o menor valor como início e o maior como fim.
            5. **Prancha/Folha**: Identifique a quantidade de folhas no documento, buscando padrões como **"01/21"** ou **"01 de 21"** se houver a palavra PRANCHA mostrar o número (ex 01/03).

            **Formato da Resposta:** json  
            Sempre retornar nessa ordem e nome de campos: localizacao, cliente, sentido, km_inicio, km_fim, prancha.

            **Texto do PDF:**  
            {extracted_text[:3000]}  # Limitando o envio para evitar estouro de tokens
        """
    
    return prompt


def carregar_instrucoes_base():
    print('def carregar_instrucoes_base():') 
    caminho = os.path.join(settings.BASE_DIR, "accounts", "instrucoes", "prompt_instrucoes.txt")
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


def buscar_clientes_prompt():
    clientes = Interessado.objects.values_list('nome', flat=True).distinct()
    lista_clientes = "\n".join(clientes)
    
    instrucoes_clientes = f"""
    Abaixo está uma lista de nomes de clientes conhecidos do sistema. Utilize esta lista como referência para reconhecer corretamente o nome do cliente ou proprietário durante a análise do PDF:
    nome de cliente nao pode conter no campo LOCALIZAÇÃO.
    {lista_clientes}
    """
    return instrucoes_clientes

def validar_dados_clientes_prompt(interessado_id, texto_pdf):
    print('funcao def validar_dados_clientes_prompt(interessado_id, texto_pdf):')
    def extrair_kms(kilometragem):
        padrao = r"(\d{1,3}\+\d{3})"
        encontrados = re.findall(padrao, kilometragem)
        if len(encontrados) >= 2:
            kms_numericos = [int(k.replace('+', '')) for k in encontrados]
            menor = min(kms_numericos)
            maior = max(kms_numericos)
            menor_formatado = f"{str(menor)[:-3]}+{str(menor)[-3:]}"
            maior_formatado = f"{str(maior)[:-3]}+{str(maior)[-3:]}"
            return f"{menor_formatado} a {maior_formatado}"
        return kilometragem

    try:
        interessado = Interessado.objects.get(id=interessado_id)
    except Interessado.DoesNotExist:
        return "❌ Interessado não encontrado."

    kilometragem_tratada = extrair_kms(interessado.kilometragem or "")

    dados_cliente = {
        "nome_br": interessado.nome_br or "Não informado",
        "kilometragem": kilometragem_tratada or "Não informado",
        "sentido": interessado.sentido or "Não informado",
        "municipio": interessado.municipio or "Não informado"
    }

    instrucoes_iniciais = f"""
    Você deve analisar o texto extraído de um documento PDF para:

    1️⃣ Tentar localizar diretamente os seguintes dados:
    - Nome da rodovia ou localidade
    - Município
    - Sentido da obra
    - Quilometragem (início e fim)

    2️⃣ Caso não consiga localizar com precisão, use como referência os dados oficiais do cliente abaixo:
    - Nome (nome_br): {dados_cliente['nome_br']}
    - Município: {dados_cliente['municipio']}
    - Sentido: {dados_cliente['sentido']}
    - Quilometragem esperada: {dados_cliente['kilometragem']}
    """
    # print(instrucoes_iniciais)
    return instrucoes_iniciais


def gerar_prompt(id, texto_pdf):
    print('def gerar_prompt(texto_pdf):')
    
    instrucoes_gerais = carregar_instrucoes_base()  # <- do arquivo ou banco
    instrucoes_listagem_clientes_BD = buscar_clientes_prompt() # <- lista de clientes atualizada para o chat saber
    instrucoes_dados_clientes_base_BD = validar_dados_clientes_prompt(id, texto_pdf) # <- comparar os campos do cadastro com os campos da analise

    prompt_completo = f"{instrucoes_dados_clientes_base_BD}{instrucoes_listagem_clientes_BD}{instrucoes_gerais}\n\nTexto extraído do PDF:\n{texto_pdf}"
    # print(prompt_completo)
    return prompt_completo


def upload_pdf(request, id):
    print('📌 Função `upload_pdf(request, id)` chamada.')
    interessado = get_object_or_404(Interessado, id=id)

    if request.method == "POST" and request.FILES.get("pdf"):
        print('📌 Recebendo arquivo PDF.')
        pdf_file = request.FILES["pdf"]

        # Salvar temporariamente o PDF
        file_path = default_storage.save(f"uploads/{pdf_file.name}", ContentFile(pdf_file.read()))
        full_path = default_storage.path(file_path)

        pdf_name = pdf_file.name
        print(f"📂 Nome do PDF: {pdf_name}")

        descricao_pdf = request.POST.get("descricao_pdf", "").strip()
        if not descricao_pdf:
            return JsonResponse({"error": "Descrição do PDF é obrigatória."}, status=400)

        try:
            # 📄 Extrair texto do PDF
            extracted_text = extract_text_from_pdf(full_path)
            if "Erro ao processar PDF" in extracted_text:
                return JsonResponse({"error": extracted_text}, status=400)

            # 🧠 Gerar prompt com instruções base + texto do PDF
            prompt_completo = gerar_prompt(interessado.id,extracted_text)
            print("📝 Prompt gerado:")
            # print(prompt_completo)

            # 🧠 Chamada direta à OpenAI (ChatGPT)
            chatgpt_data = call_api_chatGPT(prompt_completo)

            # Força conversão de `None` para `""`
            chatgpt_data = {k: v if v is not None else "" for k, v in chatgpt_data.items()}

            # Adicionar o nome do PDF dentro do JSON retornado
            chatgpt_data["pdf_name"] = pdf_name
            chatgpt_data["descricao_pdf"] = descricao_pdf

            print("✅ Resposta da OpenAI:")
            # print(chatgpt_data)

            return JsonResponse(chatgpt_data)

        except Exception as e:
            print(f"❌ Erro ao processar o PDF: {e}")
            return JsonResponse({"error": "Erro interno ao processar o arquivo."}, status=500)

        finally:
            # 🗑️ Excluir o PDF temporário
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                print(f"🗑️ Arquivo deletado: {file_path}")

    return JsonResponse({"error": "Nenhum arquivo enviado."}, status=400)


def salvar_pdf_validation(request):
    """
    Salva os dados extraídos do PDF na tabela PdfValidation.
    Retorna o objeto PdfValidation salvo. 
    Salva os dados validados do PDF no banco de dados e encerra a contagem de tentativas.
    """
    if request.method == "POST":
        try:
            # Capturar os dados do POST
            data = json.loads(request.body.decode("utf-8"))
            print("📥 Dados recebidos para salvar: def salvar_pdf_validation(request)", data)

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
                return JsonResponse({"error": f"Erro ao identificar o cliente. Atualize a página e tente novamente. func salvar_pdf_validation"}, status=400)

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

            print(f"✅ PDF Validation salvo com ID {pdf_validation.id}")

            # historico_analise_pdf.objects.create(
            #     interessado=interessado,
            #     usuario=request.user if request.user.is_authenticated else None,
            #     # texto_pdf=extracted_text[:3000],
            #     # dados_localizados=chatgpt_data,
            #     observacoes="Análise automática realizada via upload_pdf."
            # )

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

@csrf_exempt
def resetar_tentativas(request):
    """
    Reseta a contagem de tentativas de reanálise na sessão do usuário.
    """
    if request.method == "POST":
        request.session["reanalisar_tentativas"] = 0
        request.session.modified = True
        return JsonResponse({"message": "Contador de tentativas resetado."})

    return JsonResponse({"error": "Método inválido"}, status=405)


def calcular_similaridade(a, b):
        if not a or not b:  # Se algum valor for None ou vazio
            return 0
        # Pré-processar as strings: remover quebras de linha, espaços extras, e padronizar maiúsculas
        a = ' '.join(a.upper().split())
        b = ' '.join(b.upper().split())
        return SequenceMatcher(None, a, b).ratio()

def pdf_checklist(request, id, pdf_validation_id):
    # Busca o registro do interessado pelo ID
    print('chegou def pdf_checklist(request, interessado_id):') 
    print(f'pdf_validation_id. {pdf_validation_id}') 
    interessado = get_object_or_404(Interessado, id=id)

    # Busca a última validação de PDF para esse interessado
    # pdf_validation = PdfValidation.objects.filter(interessado=interessado).order_by('-data_hora_cadastro').first()
    pdf_validation = get_object_or_404(PdfValidation, id=pdf_validation_id)
    
    # Pega os dados do cliente (tb_interessado)
    cliente_dados = {
        'nome': interessado.nome,  
        'kilometragem': interessado.kilometragem,  
        'nome_br': interessado.nome_br,
        'municipio': interessado.municipio,
        'responsavel_tecnico': interessado.responsavel_tecnico,
        'descricao_processo': interessado.descricao_processo,
        'memorial': interessado.memorial,
        'art': interessado.art,
        'fase_projeto': interessado.fase_projeto
    }
    print(f'cliente_dados {cliente_dados}')

    # Pega os dados do PDF
    pdf_dados = {
        'localizacao': pdf_validation.localizacao,
        'etapa': pdf_validation.etapa,
        'projeto': pdf_validation.projeto,
        'projeto': pdf_validation.projeto,
        'proprietario_cliente': pdf_validation.proprietario_cliente,
        'responsavel_tecnico': pdf_validation.responsavel_tecnico,
        'prancha': pdf_validation.prancha,
    }

    print("print pdf_dadospdf_dadospdf_dados")
    print(pdf_dados) 

    # Função para calcular similaridade


    # Comparar os campos por aproximação
    similaridade_responsavel_tecnico = calcular_similaridade(
        interessado.responsavel_tecnico, pdf_validation.responsavel_tecnico
    )

    # Definir o limite de similaridade
    LIMITE_SIMILARIDADE = 0.8  # 80% de similaridade é considerado suficiente

    # Resultado da comparação
    responsavel_tecnico_status = (
        "Correto" if similaridade_responsavel_tecnico >= LIMITE_SIMILARIDADE
        else f"Divergente (Similaridade: {similaridade_responsavel_tecnico:.2f})"
    )

    checklist_data = {
        'responsavel_tecnico': responsavel_tecnico_status, 
    }
    print('checklist_datachecklist_datachecklist_data')
    print(checklist_data)

    usuario_responsavel = None
    if interessado.usuario:  # Verifica se o campo usuario está preenchido
        usuario_responsavel = User.objects.get(id=interessado.usuario_id).username
    # print(usuario_responsavel)

    # Caso não exista validação, mostre uma mensagem de erro ou vazio
    if not pdf_validation:
        return render(request, 'accounts/pdf_checklist.html', {'interessado': interessado, 'message': 'Nenhuma validação encontrada.'})

    #     # Verifica se os campos estão preenchidos para cada item
    checklist_data = {
        'localizacao': 'OK' if pdf_validation.localizacao else 'Não preenchido',
        'etapa': 'OK' if pdf_validation.etapa else 'Não preenchido',
        'projeto': 'OK' if pdf_validation.projeto else 'Não preenchido',
        'proprietario_cliente': 'OK' if pdf_validation.proprietario_cliente else 'Não preenchido',
        'responsavel_tecnico': 'OK' if pdf_validation.responsavel_tecnico else 'Não preenchido',
        'prancha': 'OK' if pdf_validation.prancha else 'Não preenchido',
    }

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
     

    # Renderizar os dados no template 
    return render(request, 'accounts/pdf_checklist.html', {
            'interessado': interessado,
            'checklist_data': checklist_data,
            'tipo_projeto' : tipo_projeto,
            'tipo_classificao' : tipo_classificao,
            'usuario_responsavel': usuario_responsavel,
            'prancha':pdf_validation.prancha
        })


def download_checklist(request, id):
    print(f"📥 Gerando PDF do checklist para interessado ID: {id}")

    interessado = get_object_or_404(Interessado, id=id)
    pdfs = PdfFile.objects.filter(interessado=id).order_by("-uploaded_at")
    pdf = pdfs.first()
    validacoes = PdfValidation.objects.filter(interessado=id)

    template = get_template("accounts/checklist_criado_layout.html")
    context = {
        "interessado": interessado,
        "pdfs": pdfs,
        "pdf": pdf,
        "validacoes": validacoes
    }

    html_string = template.render(context)
    print("✅ HTML gerado com sucesso!")

    pdf_file = io.BytesIO()
    try:
        HTML(string=html_string).write_pdf(pdf_file)
        print("✅ PDF gerado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao gerar o PDF: {e}")

    pdf_file.seek(0)

    try:
        with open("checklist_test.pdf", "wb") as f:
            f.write(pdf_file.getvalue())
        print("✅ PDF salvo no servidor como 'checklist_test.pdf'")
    except Exception as e:
        print(f"❌ Erro ao salvar o PDF: {e}")

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="checklist.pdf"'
    return response
