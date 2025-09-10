# \Projeto_Engenharia\it_solutions_eng\accounts\models\pdf_model.py

from django.db import models

class PDFDocument(models.Model):
    nome = models.CharField(max_length=255)
    data_upload = models.DateTimeField(auto_now_add=True)
    localizacao = models.CharField(max_length=255, null=True, blank=True)
    km_inicio = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nome
