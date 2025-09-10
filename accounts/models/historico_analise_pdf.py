from django.db import models
from django.conf import settings
from accounts.models import Interessado, PdfFile, PdfValidation

class HistoricoAnalisePDF(models.Model):
    interessado = models.ForeignKey(Interessado, on_delete=models.CASCADE)
    pdf_file = models.ForeignKey(PdfFile, null=True, blank=True, on_delete=models.SET_NULL)
    pdf_validation = models.ForeignKey(PdfValidation, null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    texto_pdf = models.TextField()
    dados_localizados = models.JSONField()
    dados_corrigidos = models.JSONField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tb_historico_analise_pdf'

    def __str__(self):
        return f"Histórico de {self.interessado.nome} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"