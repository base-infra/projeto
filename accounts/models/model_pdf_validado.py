from django.db import models
from accounts.models import Interessado
from django.conf import settings
from django.utils.timezone import now

class DadosPdfValidado(models.Model):
    id_pdf_validado = models.AutoField(primary_key=True)  
    interessado = models.ForeignKey(Interessado, on_delete=models.CASCADE, db_column='interessado_id')   
    localizacao = models.TextField(null=True, blank=True)
    classificacao = models.CharField(max_length=255, null=True, blank=True)
    kilometragem_inicio = models.CharField(max_length=255, null=True, blank=True)
    kilometragem_fim = models.CharField(max_length=255, null=True, blank=True)
    coordenadas_georreferenciais_e = models.CharField(max_length=50, null=True, blank=True)
    coordenadas_georreferenciais_n = models.CharField(max_length=50, null=True, blank=True)
    nome_br = models.CharField(max_length=255, null=True, blank=True)
    sentido = models.CharField(max_length=255, null=True, blank=True)
    tipo_projeto = models.CharField(max_length=255, null=True, blank=True)
    nro_prancha = models.CharField(max_length=10, null=True, blank=True)
    responsavel_tecnico = models.CharField(max_length=255, null=True, blank=True)
    proprietario_cliente = models.CharField(max_length=255, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    data_recebimento = models.DateTimeField(null=True, blank=True)
    descricao_processo = models.CharField(max_length=255, null=True, blank=True)
    tracado_dominio = models.CharField(max_length=50, null=True, blank=True)
    cotas_legiveis = models.CharField(max_length=50, null=True, blank=True)
    escala_pdf = models.CharField(max_length=50, null=True, blank=True)
    memorial_pdf = models.CharField(max_length=50, null=True, blank=True)
    largura_pista_dnit = models.CharField(max_length=50, null=True, blank=True)
    legenda_correta = models.CharField(max_length=50, null=True, blank=True)
    anotacao_nota = models.CharField(max_length=50, null=True, blank=True)
    sigla_abreviacao = models.CharField(max_length=50, null=True, blank=True)
    carimbo_correto = models.CharField(max_length=50, null=True, blank=True)
    limite_propriedade = models.CharField(max_length=50, null=True, blank=True)
    delimitacao_dominio_nao_edificante = models.CharField(max_length=50, null=True, blank=True)
    art_pdf = models.CharField(max_length=50, null=True, blank=True)
    nome_arquivo = models.CharField(max_length=100, null=True, blank=True)
    data_upload = models.DateTimeField(auto_now_add=False, null=True, blank=True) 
    assertividade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    resposta_gpt = models.JSONField()
    resposta_corrigida = models.JSONField(null=True, blank=True)
    campos_corrigidos = models.IntegerField(default=0)


    class Meta:
        db_table = 'tb_dados_pdf_validado'
