import openai
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import PyPDF2 
from datetime import datetime
import json 
import re
import io
import csv 
from ..models import AnaliseGPT
from ..models import Interessado
import unidecode
from ..models import DadosPdfValidado

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

def csv_para_json(csv_texto):
    f = io.StringIO(csv_texto)
    reader = csv.DictReader(f)
    return list(reader)

def carregar_instrucoes_base():
    caminho_absoluto = os.path.join(settings.BASE_DIR, "accounts", "instrucoes", "prompt_instrucoes.txt")
    with open(caminho_absoluto, "r", encoding="utf-8") as arquivo:
        return arquivo.read() 

@csrf_exempt
def chatgpt_response(request):
    print('entrou func def chatgpt_response(request):')
    # if request.method != 'POST':
    #     return JsonResponse({'error': 'Método não permitido - chatgpt_response'}, status=405)

    try:
        data = json.loads(request.body)
        print('********** request.POST.get nome_arquivo')
        nome_arquivo = data.get('nome_arquivo', '')
        print(nome_arquivo)
        print('********** request.POST.get nome_arquivo')
        user_message = data.get('message')

        messages = request.session.get('chat_history', [])

        if not any(m['role'] == 'system' for m in messages):
            messages.insert(0, {
                "role": "system",
                "content": "Você é um assistente de engenheiro civil especialista em projetos para concessionárias."
            })
        messages.append({"role": "user", "content": user_message})

        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        request.session['chat_history'] = messages

        json_resultado = None

        # Verifica primeiro por JSON explícito na resposta
        try:
            # Procura por um bloco JSON bem delimitado
            match_json = re.search(r"```(?:json)?\s*\n(.*?)```", reply, re.DOTALL | re.IGNORECASE)
            if match_json:
                json_content = match_json.group(1).strip()
                json_resultado = json.loads(json_content)
            else:
                # Se não encontrou bloco JSON, tenta o CSV
                match_csv = re.search(r"csv corrigido:?\s*```(?:csv)?\s*\n(.*?)```", reply, re.DOTALL | re.IGNORECASE)
                if match_csv:
                    csv_content = match_csv.group(1).strip()
                    csv_content = "\n".join([
                        line.strip()
                        for line in csv_content.splitlines()
                        if line.strip() and not line.strip().startswith("```")
                    ])
                    json_resultado = csv_para_json(csv_content)
                else:
                    print("⚠️ Nenhum bloco JSON ou CSV encontrado.")

        except Exception as e:
            print("❌ Erro ao processar JSON ou CSV:", e)

        print(reply)
        print(f"resposta que procuro: {json_resultado}")

        return JsonResponse({'reply': reply, 'json_resultado': json_resultado, 'nome_arquivo': nome_arquivo})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
     
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

@csrf_exempt
def analisar_pdf(request):
    print("Iniciando análise de PDF...") 
    interessado_id = int(request.POST.get('interessado_id'))
    interessado = Interessado.objects.get(id=interessado_id)

    campos_ordenados = [
        "LOCALIZACAO",
        "KM_INICIO",
        "KM_FIM",
        "NOME_BR",
        "COORDENADAS_GEORREFERENCIAIS_E",
        "COORDENADAS_GEORREFERENCIAIS_N",
        "TRACADO_FAIXA_DOMINIO",
        "COTAS_TEXTOS_LEGIVEIS",
        "VERIFICACAO_ESCALA",
        "MEMORIAL",
        "LARGURA_PISTA_DNIT",
        "LEGENDAS",
        "ANOTACAO_NOTA",
        "SIGLA_ABREVIACAO",
        "LOC_KM_PREFIXO",
        "CARIMBO_CORRETO",
        "LIMITE_PROPRIEDADE",
        "DELIMITACAO_DOMINIO_NAO_EDIFICANTE",
        "ART_PDF",
        "QTD_FOLHAS"
    ]
    mapeamento_chaves = {
        "LOCALIZA": "LOCALIZACAO",
        "KM INICIO": "KM_INICIO",
        "KM FIM": "KM_FIM",
        "SIGLA_ABREV": "SIGLA_ABREVIACAO",
        "MEMORIAL_DESCRITIVO": "MEMORIAL"
    }
    if request.method == 'POST' and request.FILES.get('pdf'):
        try:
            json_resultado = None  
            print("Arquivo PDF recebido, iniciando leitura...")
            pdf_file = request.FILES['pdf']
            reader = PyPDF2.PdfReader(pdf_file)
            texto = " ".join(p.extract_text() or "" for p in reader.pages)

            nome_arquivo = pdf_file.name
            request.session['nome_arquivo'] = nome_arquivo
            print('*************************** request.session[nome_arquivo] ')
            
            print(nome_arquivo)
            print('*************************** request.session[nome_arquivo] ')

            # 🧠 Verificar se já existe um registro com esse nome_arquivo + interessado
            registro_existente = DadosPdfValidado.objects.filter(
                nome_arquivo=nome_arquivo,
                interessado=interessado
            ).order_by('-data_upload').first()
 
            if registro_existente and (registro_existente.campos_corrigidos > 0 
                                  or(registro_existente.resposta_corrigida 
                                  and not registro_existente.resposta_gpt)):

                print("📄 Registro anterior com correções encontrado. Mesclando respostas...")

                resposta_gpt = registro_existente.resposta_gpt or {}
                resposta_corrigida = registro_existente.resposta_corrigida or {}

                # Normaliza chaves com mapeamento
                resposta_gpt = {
                    mapeamento_chaves.get(k, k): v
                    for k, v in resposta_gpt.items()
                }
                resposta_corrigida = {
                    mapeamento_chaves.get(k, k): v
                    for k, v in resposta_corrigida.items()
                }

                resposta_final = resposta_corrigida.copy()
                for campo, valor in resposta_gpt.items():
                    if campo not in resposta_corrigida:
                        resposta_final[campo] = valor

                json_resultado = {
                    campo: resposta_final.get(campo, "")
                    for campo in campos_ordenados
                }

                return JsonResponse({
                    'reply': json.dumps(json_resultado, ensure_ascii=False),
                    'json_resultado': json_resultado,
                    'nome_arquivo': nome_arquivo,
                    'origem': 'resposta_corrigida_mesclada'
                })
 

            print('====================')
            print(f"[{datetime.now()}] analisar_pdf - Raw reply antes retirada duplicidade:\n{len(texto)}")
            print('====================')

            texto = re.sub(r'\s+', ' ', texto)  # Limpa espaços múltiplos
            texto = re.sub(r'(\b\w+\b)(\s+\1\b)+', r'\1', texto)  # Remove palavras duplicadas consecutivas

            print('====================')
            print(f"[{datetime.now()}] analisar_pdf - Raw reply depois retirada duplicidade:\n{len(texto)}")
            print('====================')
 
            # ---------------------
            # VERIFICAÇÃO DO NOME CLIENTE CADASTRADO COM O NOME NO PDF
            # ---------------------
            # nome_cliente = unidecode.unidecode(interessado.nome).lower() 
            # texto_pdf = unidecode.unidecode(texto).lower()

            # if nome_cliente not in texto_pdf:
            #     return JsonResponse({
            #         'error': f"O nome do interessado '{interessado.nome}' não foi encontrado no conteúdo do PDF.",
            #         'nome_cliente': interessado.nome,
            #     }, status=400)

            prompt = carregar_instrucoes_base()
 
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            # messages = []
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content":prompt},
                    {"role": "user", "content": f"Analise o seguinte conteúdo do PDF: {texto}"},
                    {"role": "system", "content": "Você é um assistente de engenheiro civil especialista em projetos para concessionárias."}
                ]
            )

                    # {"role": "user", "content": f"Analise o seguinte conteúdo do PDF: {texto[:3500]}"},
            reply = response.choices[0].message.content
            print(f"[{datetime.now()}] analisar_pdf - Raw reply:\n{reply!r}") 

            AnaliseGPT.objects.create(
                nome_arquivo=nome_arquivo,
                resposta_gpt=reply,
                interessado=interessado
                # id_pdf_validado omitido nesse ponto eu ainda nao tenho criado um pdf validado
            )


            
            return JsonResponse({'reply': reply,'json_resultado': json_resultado, 'nome_arquivo': nome_arquivo,'origem': 'nova_analise'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Arquivo PDF inválido ou não enviado'}, status=400)

@csrf_exempt
def clear_chat(request):
    request.session['chat_history'] = []
    return JsonResponse({'status': 'chat history cleared'})
 