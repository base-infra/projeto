# accounts/forms/cadastro_form.py
from django import forms
from accounts import models
from accounts.models.model_cadastro import Interessado

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

MEMORIAL_CHOICES = [
    ('sim', 'Sim'),  # valor real, nome legível
    ('nao', 'Não'),    # valor real, nome legível
    ('n/a', 'n/a'),    # valor real, nome legível
]

ART_CHOICES = [
    ('sim', 'Sim'),  # valor real, nome legível
    ('nao', 'Não'),    # valor real, nome legível 
    ('n/a', 'n/a'),    # valor real, nome legível
]

OCUPACAO_PROJETO = [
    ('acesso', 'Acesso'),  # valor real, nome legível
    ('ocupacao', 'Ocupação'),    # valor real, nome legível
    ('publicidade', 'Publicidade'),    # valor real, nome legível
]

FASE_PROJETO_CHOICES = [
    ('1', '1'),  # valor real, nome legível
    ('2', '2'),    # valor real, nome legível
    ('3', '3'),    # valor real, nome legível
]

NOME_CONCESSIONARIA = [
       ('ECO101', 'ECO101'),
        ('EPR_LP', 'EPR LP')
]

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Interessado
        fields = '__all__'
    data_recebimento = forms.DateField(
        required=True,  # Torna o campo obrigatório
        widget=forms.DateInput(attrs={'type': 'date'})  # Usa um seletor de data HTML5
    )
    
    # vdm = forms.ChoiceField(choices=VDM_CHOICES, widget=forms.Select(attrs={'id': 'vdm-select'})) 
    memorial = forms.ChoiceField(choices=MEMORIAL_CHOICES, widget=forms.Select(attrs={'id': 'memorial-select'}))    
    art = forms.ChoiceField(choices=ART_CHOICES, widget=forms.Select(attrs={'id': 'art-select'}))
    tipo_projeto = forms.ChoiceField(choices=OCUPACAO_PROJETO, widget=forms.Select(attrs={'id': 'ocupacao-select'}))
    fase_projeto = forms.ChoiceField(choices=FASE_PROJETO_CHOICES, widget=forms.Select(attrs={'id': 'fase-projeto-select'}))
    nome_concessionaria = forms.ChoiceField(choices=NOME_CONCESSIONARIA, widget=forms.Select(attrs={'id': 'nome-concessionaria-select'}))
    
    tipo_ocupacao = forms.ChoiceField(
        choices=TIPO_OCUPACAO,  # Remove a opção "vazio" daqui, pois já a colocamos no HTML
        required=False,
        widget=forms.Select(attrs={'id': 'tipo-ocupacao-select'})
    )

    tipo_publicidade = forms.ChoiceField(
        choices=TIPO_PUBLICIDADE,
        required=False,
        widget=forms.Select(attrs={'id': 'tipo-publicidade-select'})
    )

    tipo_acesso = forms.ChoiceField(
        choices=TIPO_ACESSO,
        required=False,
        widget=forms.Select(attrs={'id': 'tipo-acesso-select'})
    )

    ocupacao_area = forms.CharField(
        max_length=255,
        required=False,  # Não obrigatório por padrão
        widget=forms.TextInput(attrs={'id': 'ocupacao-area-input', 'style': 'display: none;'}),  # Oculto inicialmente
    )

    nome_concessionaria = forms.ChoiceField(
        choices=NOME_CONCESSIONARIA,
        required=False,
        widget=forms.Select(attrs={'id': 'nome-concessionaria'})
    )

    # data_recebimento = forms.DateTimeField(required=False)
    data_devolucao = forms.CharField(max_length=20, required=False) 
    data_hora_cadastro = forms.DateTimeField(required=False) 