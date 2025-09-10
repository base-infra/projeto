from django.contrib import admin
from django.urls import path, include 
from accounts.views.home_views import *  
from accounts.views import *
from django.conf.urls.static import static 
from django.conf import settings   
from django.shortcuts import redirect    
from django.contrib import admin 
from django.contrib.auth import views as auth_views 
from accounts.views import home_view   
from accounts.views.pdf_upload import upload_pdf, pdf_checklist, download_checklist, reanalisar_dados_pdf, resetar_tentativas,salvar_pdf_validation
from accounts.views.clientes_view import listar_clientes, editar_clientes, cadastro_view, excluir_interessado, overview_cliente
from accounts.views.pdf_list import list_pdf_cliente , listar_checklists, listar_query_checklists, recuperar_checklist,list_pdf_validado_ajax
from accounts.views.gpt_view import mostrar_popup_dados, salvar_dados_pdf
from accounts.views.checklist_criado_view import checklist_criado
from accounts.views.gpt_message import chatgpt_response, clear_chat, analisar_pdf
from accounts.views.gerar_checklist_GPT import gerar_checklist, gerar_checklist_criado,gerar_checklist_criado_analises
from accounts.views.salvar_checklist_GPT import salvar_checklist
from accounts.views.dados_assertividade import visualizar_assertividade
from accounts.views.exportar_checklist import exportar_checklist
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

class CustomLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))  # Redireciona para a página de login


urlpatterns = [ 
    
    path('admin/', admin.site.urls), 
    path('', lambda request: redirect('home', permanent=True)), 
    path('home/', home_view, name='home'),    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('clientes/', listar_clientes, name='listar_clientes') ,
    path('editar/<int:id>/', editar_clientes, name='editar_clientes'),
    path('cadastro/', cadastro_view, name='cadastro_view'), 
    path('excluir/<int:id>/', excluir_interessado, name='excluir_interessado'), 
    path('overview_cliente/<int:id>/', overview_cliente, name='overview_cliente') , 
    path('upload_pdf/<int:id>/', upload_pdf, name='upload_pdf') , 
    path('pdf_checklist/<int:id>/<int:pdf_validation_id>/', pdf_checklist, name='pdf_checklist'),
    path('download_checklist/<int:id>', download_checklist, name='download_checklist'), 
    path('pdfs/<int:interessado_id>/', list_pdf_cliente, name='list_pdf_cliente'),  
    path("mostrar-popup-dados/", mostrar_popup_dados, name="mostrar_popup_dados"),
    path("salvar-dados-pdf/", salvar_dados_pdf, name="salvar_dados_pdf"),
    path("reanalisar-dados-pdf/", reanalisar_dados_pdf, name="reanalisar_dados_pdf"),
    path("resetar-tentativas/", resetar_tentativas, name="resetar_tentativas"),
    path("checklist-criado/<int:id>/", checklist_criado, name="checklist_criado"),
    path("listar-checklists", listar_checklists, name="listar-checklists"), 
    path('checklists/', listar_query_checklists, name='listar_query_checklists'),  
    path('api/chatgpt/', chatgpt_response, name='chatgpt_response'), 
    path('api/chatgpt/analisar-pdf/', analisar_pdf, name='analisar_pdf'),
    path('api/chatgpt/clear/', clear_chat, name='clear_chat'),
    path('gerar-checklist/<int:cliente_id>/', gerar_checklist, name='gerar_checklist'), 
    path('salvar-checklist/<int:cliente_id>/', salvar_checklist, name='salvar_checklist'), 
    # path('gerar-checklist-criado/<int:cliente_id>/', gerar_checklist_criado, name='gerar_checklist'),  
    path('gerar-checklist-criado-analises/<int:cliente_id>/<int:pdf_id>/', gerar_checklist_criado_analises, name='gerar_checklist_criado_analises'),
    path('pdfs-recuperado/<int:interessado_id>/<int:pdfvalidado_id>/', recuperar_checklist, name='recuperar_checklist'),  
    path('pdfs-validado-ajax/<int:interessado_id>/', list_pdf_validado_ajax, name='list_pdf_validado_ajax'),
    path('dados-assertividade/<int:cliente_id>/<int:pdf_id>/', visualizar_assertividade, name='dados_assertividade'),
    path("checklist/<int:interessado_id>/<int:pdf_id>/exportar/", exportar_checklist, name="exportar_checklist"),




    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

