from django.db import models
from accounts.models.model_cadastro import Interessado  # Ajuste o caminho se necessário
from django.conf import settings 

class PdfValidation(models.Model):
    """
    Modelo para armazenar os dados validados de um PDF.
    """
    interessado = models.ForeignKey(
        Interessado,  # Caminho correto do modelo relacionado
        on_delete=models.CASCADE,
        related_name='pdf_uploads'  # Define o related_name
    )
    localizacao = models.TextField(null=True, blank=True)
    etapa = models.CharField(max_length=255, null=True, blank=True)
    projeto = models.CharField(max_length=255, null=True, blank=True)
    proprietario_cliente = models.CharField(max_length=255, null=True, blank=True)  # Certifique-se de que o nome do campo está correto
    responsavel_tecnico = models.CharField(max_length=255, null=True, blank=True)
    prancha = models.CharField(max_length=10, null=True, blank=True)  # Ex: '01/03'
    data_hora_cadastro = models.DateTimeField(auto_now_add=True)
    ocupacao = models.CharField(max_length=255)
    escala = models.CharField(max_length=255)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, max_length=255, null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tb_pdf_validation'  # Definir explicitamente o nome da tabela

def __str__(self): 
        return f"{self.projeto} - {self.etapa}"


class PdfFile(models.Model):
    print("chegou aqui class PdfFile(models.Model):")
    interessado = models.ForeignKey(Interessado, on_delete=models.CASCADE, related_name="pdfs")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pdf_validation = models.ForeignKey(PdfValidation, on_delete=models.CASCADE)
    nome_pdf = models.CharField(max_length=255) 
    versao = models.IntegerField(default=1)
    status_pdf = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    descricao_pdf_upload = models.CharField(max_length=255)

    class Meta:
        db_table = 'tb_pdf_files'  # Definir explicitamente o nome da tabela

    def __str__(self):
        return f"{self.nome_pdf} - Versão {self.versao}"
