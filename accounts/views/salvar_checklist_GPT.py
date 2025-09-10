from ..models import DadosPdfValidado, Interessado, AnaliseGPT
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import render, get_object_or_404
from django.utils import timezone  
from django.db.models import Q
import re

@csrf_exempt
def salvar_checklist(request, cliente_id):
    print(f"⚙️ Recebido salvar_checklist para Interessado ID: {cliente_id}") 
    
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            interessado = Interessado.objects.get(id=cliente_id)
        except Interessado.DoesNotExist:
            return JsonResponse({'error': f'Interessado com id {cliente_id} não encontrado.'}, status=400)

        print("📄 Dados recebidos para salvar:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # Normalizar as chaves do checklist_data para minúsculo
        checklist_original = data.get('checklist_data', {})
        checklist = {k.lower(): v for k, v in checklist_original.items()}

        nome_arquivo = data.get('nome_arquivo', '')

        # # Procurar o último registo compatível na tabela tb_analise_gpt 
        resposta_corrigida = {k.upper(): str(v).strip() for k, v in checklist.items()}
        resposta_gpt_dict = {}
        campos_diferentes = 0
        assertividade = 0

        ultima_analise = AnaliseGPT.objects.filter(
            interessado=interessado,
            nome_arquivo=nome_arquivo
        ).order_by('-data_analise').first()

        if ultima_analise:
            if ultima_analise.resposta_corrigida:
                resposta_anterior = {k.upper(): str(v).strip() for k, v in ultima_analise.resposta_corrigida.items()}
                if resposta_corrigida == resposta_anterior:
                    assertividade = 100.0
                    campos_diferentes = 0
                    print("✅ Resposta corrigida idêntica à anterior. Assertividade: 100%")
            elif ultima_analise.resposta_gpt:
                if isinstance(ultima_analise.resposta_gpt, str):
                    linhas = ultima_analise.resposta_gpt.splitlines()
                    chave_atual = None
                    for linha in linhas:
                        linha = linha.strip()
                        if not linha:
                            continue
                        match_chave = re.match(r'"?(\d+\.?\s*[A-Z_\s]+)"?:?', linha, re.IGNORECASE)
                        if match_chave:
                            chave_atual = re.sub(r'^\d+\.?\s*', '', match_chave.group(1)).strip().upper()
                            continue
                        if chave_atual and '"valor"' in linha:
                            match_valor = re.search(r'"valor"\s*:\s*"([^"]+)"', linha)
                            if match_valor:
                                resposta_gpt_dict[chave_atual] = match_valor.group(1).strip()
                elif isinstance(ultima_analise.resposta_gpt, dict):
                    resposta_gpt_dict = {k.upper(): str(v).strip() for k, v in ultima_analise.resposta_gpt.items()}

                campos_diferentes = sum(
                    1 for campo in resposta_corrigida
                    if campo in resposta_gpt_dict and resposta_gpt_dict[campo] != resposta_corrigida[campo]
                )
                total_campos = len(resposta_corrigida)
                assertividade = round((total_campos - campos_diferentes) / total_campos * 100, 2) if total_campos else 0

            ultima_analise.resposta_corrigida = resposta_corrigida
            ultima_analise.campos_corrigidos = campos_diferentes
            ultima_analise.assertividade = assertividade
            ultima_analise.save()

            print(f"✅ Análise atualizada com {campos_diferentes} campos corrigidos.")
            print(f"📊 Assertividade registrada: {assertividade}%")
        else:
            print("⚠️ Nenhuma análise GPT anterior encontrada para este cliente e arquivo.")

        DadosPdfValidado.objects.create(
            interessado=interessado,
            localizacao=checklist.get('localizacao'),
            classificacao=data.get('classificacao'),
            kilometragem_inicio=checklist.get('km_inicio'),
            kilometragem_fim=checklist.get('km_fim'),
            coordenadas_georreferenciais_e=checklist.get('coordenadas_georreferenciais_e'),
            coordenadas_georreferenciais_n=checklist.get('coordenadas_georreferenciais_n'),
            nome_br=data.get('br'),
            sentido=data.get('sentido'),
            tipo_projeto=data.get('tipo'),
            nro_prancha=checklist.get('qtd_folhas'),
            responsavel_tecnico=data.get('responsavel_tecnico'),
            proprietario_cliente=data.get('interessado'),
            usuario=request.user if request.user.is_authenticated else None,
            data_recebimento=data.get('data_recebimento'),
            descricao_processo=data.get('descricao_processo'),
            tracado_dominio=checklist.get('tracado_faixa_dominio'),
            cotas_legiveis=checklist.get('cotas_textos_legiveis'),
            escala_pdf=checklist.get('verificacao_escala'),
            memorial_pdf=checklist.get('memorial'),
            largura_pista_dnit=checklist.get('largura_pista_dnit'),
            legenda_correta=checklist.get('legendas'),
            anotacao_nota=checklist.get('anotacao_nota'),
            sigla_abreviacao=checklist.get('sigla_abreviacao'),
            carimbo_correto=checklist.get('carimbo_correto'),
            limite_propriedade=checklist.get('limite_propriedade'),
            delimitacao_dominio_nao_edificante=checklist.get('delimitacao_dominio_nao_edificante'),
            art_pdf=checklist.get('art_pdf'),
            nome_arquivo=nome_arquivo,
            data_upload=timezone.now(),
            assertividade=assertividade,
            resposta_corrigida=resposta_corrigida,
            campos_corrigidos=campos_diferentes,
            resposta_gpt=resposta_gpt_dict,
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Método não permitido - salvar_checklist'}, status=405)
