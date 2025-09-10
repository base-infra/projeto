from django.db import models
from accounts.models import Interessado, DadosPdfValidado

class AnaliseGPT(models.Model):
    id = models.AutoField(primary_key=True)
    nome_arquivo = models.CharField(max_length=255)
    interessado = models.ForeignKey(Interessado, on_delete=models.CASCADE) 
    # id_pdf_validado = models.ForeignKey(DadosPdfValidado, on_delete=models.CASCADE, null=True, blank=True)
    assertividade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    resposta_gpt = models.JSONField()
    resposta_corrigida = models.JSONField(null=True, blank=True)
    campos_corrigidos = models.IntegerField(default=0)
    data_analise = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Análise {self.id} - {self.nome_arquivo}'

    class Meta:
        db_table = 'tb_analise_gpt'
