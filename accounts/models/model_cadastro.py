# accounts/models/model_cadastro.py
from django.db import models
from django.utils import timezone  # Apenas necessário se você for usar timezone.now
from django.conf import settings


MEMORIAL_CHOICES = [
    ('sim', 'Sim'),  # valor real, nome legível
    ('nao', 'Não'),    # valor real, nome legível
]

ART_CHOICES = [
    ('sim', 'Sim'),  # valor real, nome legível
    ('nao', 'Não'),    # valor real, nome legível
]

OCUPACAO_CHOICES = [
    ('acesso', 'Acesso'),  # valor real, nome legível
    ('ocupacao', 'Ocupação'),    # valor real, nome legível
    ('publicidade', 'Publicidade'),    # valor real, nome legível
]

FASE_PROJETO_CHOICES = [
    ('1', '1'),  # valor real, nome legível
    ('2', '2'),    # valor real, nome legível
    ('3', '3'),    # valor real, nome legível
]

TIPO_ACESSO = [
        ('vmd_menor_igual_10', 'VMD <=10'),
        ('vmd_maior_10', 'VMD > 10'),
        ('10_maior_vmd_menor_200', '10 > VMD < 20'),
        ('vmd_maior_igual_200', 'VMD >= 200')
]

TIPO_OCUPACAO = [
        ('todas', 'Todas'),
        ('porte_0_100m', 'Porte de 0-100m'),
        ('porte_101_1000m', 'Porte de 101-1000m'),
        ('porte_1001_10000m', 'Porte de 1001-10000m'),
        ('porte_acima_1000', 'Porte acima de 10000m')
]

TIPO_PUBLICIDADE = [
        ('todas', 'Todas'),
        ('simples', 'Simples'), 
        ('energizado', 'Energizado'), 
        ('portico_semi_portico', 'Portico e Semi portico'), 
]

NOME_CONCESSIONARIA = [
       ('ECO101', 'ECO101'),
        ('EPR_LP', 'EPR LP')
]

class Interessado(models.Model):
    nome = models.CharField(max_length=255) 
    kilometragem = models.CharField(max_length=255)
    nome_br = models.CharField(max_length=255)
    sentido = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255) 
    cidade = models.CharField(max_length=255, null=True, blank=True) 
    estado = models.CharField(max_length=255,null=True, blank=True)
    tipo = models.CharField(max_length=255,null=True, blank=True)
    numero_folha = models.CharField(max_length=255,null=True, blank=True) 
    responsavel_tecnico = models.CharField(
        max_length=255, 
        default='Rerond Goulart Carvalho',  # Valor padrão
        blank=True  
    )
    descricao_processo = models.TextField(null=True, blank=True) 
    memorial = models.CharField(max_length=20, choices=MEMORIAL_CHOICES) # Usando as opções de escolha
    art = models.CharField(max_length=20, choices=ART_CHOICES) # Usando as opções de escolha 
    ocupacao = models.CharField(max_length=20, choices=OCUPACAO_CHOICES,null=True, blank=True) # Usando as opções de escolha 
    fase_projeto = models.CharField(max_length=20, choices=FASE_PROJETO_CHOICES) # Usando as opções de escolha 
    tipo_ocupacao = models.CharField(max_length=80, choices=TIPO_OCUPACAO,null=True, blank=True) # Usando as opções de escolha 
    tipo_publicidade = models.CharField(max_length=80, choices=TIPO_PUBLICIDADE,null=True, blank=True) # Usando as opções de escolha 
    tipo_acesso = models.CharField(max_length=80, choices=TIPO_ACESSO,null=True, blank=True) # Usando as opções de escolha 
    nro_processo = models.CharField(max_length=255)
    ocupacao_area = models.CharField(max_length=255, null=True, blank=True)  # Novo campo para armazenar a área 
    data_recebimento = models.DateField(null=False, blank=True)  
    data_devolucao = models.CharField(max_length=20, null=True, blank=True)
    data_hora_cadastro = models.DateTimeField(auto_now_add=True) 
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, max_length=255, null=True, blank=True)
    nome_concessionaria = models.CharField(max_length=50, choices=NOME_CONCESSIONARIA,null=True, blank=True)

    class Meta:
        db_table = 'tb_interessado'
    
    def __str__(self):
        return self.nome
    
    def classificacao_projeto(self):
        """
        Retorna o primeiro campo preenchido como classificação do projeto.
        """
        if self.tipo_publicidade:
            return f"Tipo de Publicidade" 
        if self.tipo_acesso:
            return f"Tipo de Acesso"
        if self.tipo_ocupacao:
            return f"Tipo de Ocupação"
        return "Sem classificação"
