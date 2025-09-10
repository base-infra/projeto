from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    print("Entrou na home_view")
    print("Usuário atual:", request.user)

    if request.user.is_authenticated:
        print("Usuário autenticado, redirecionando para home.") 
        return render(request, 'accounts/home.html') 
    else:
        print("Usuário não autenticado, redirecionando para login.")
        return render(request, 'registration/login.html')