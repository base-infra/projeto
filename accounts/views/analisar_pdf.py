from PyPDF2 import PdfReader
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# Carregar variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Criar o cliente OpenAI corretamente
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    """ Extrai o texto de um arquivo PDF usando PyPDF2 """
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        return f"Erro ao processar PDF: {str(e)}"
    return text

def carregar_instrucoes_base():
    with open("instrucoes/prompt_instrucoes.txt", "r", encoding="utf-8") as arquivo:
        return arquivo.read()


def gerar_prompt(texto_pdf):
    instrucoes = carregar_instrucoes_base()  # <- do arquivo ou banco
    prompt_completo = f"{instrucoes}\n\nTexto extraído do PDF:\n{texto_pdf}"
    return prompt_completo


@csrf_exempt
def upload_pdf(request):
    print('def upload_pdf(request): caminho views analisar_pdf')
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        
        # Salvar temporariamente o PDF
        file_path = default_storage.save(f"uploads/{pdf_file.name}", ContentFile(pdf_file.read()))
        full_path = default_storage.path(file_path)

        # Extrair texto do PDF
        extracted_text = extract_text_from_pdf(full_path)
        if "Erro ao processar PDF" in extracted_text:
            return JsonResponse({"error": extracted_text}, status=400)
 
        prompt = gerar_prompt(extracted_text) 
        print(prompt)
        
        try:
            # Enviar para a API do ChatGPT
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Alterado para compatibilidade com OpenAI
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            chatgpt_response = response.choices[0].message.content
            print(chatgpt_response)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao chamar OpenAI: {str(e)}"}, status=500)

        return JsonResponse({"resultado": chatgpt_response})

    return JsonResponse({"error": "Nenhum PDF enviado."}, status=400)