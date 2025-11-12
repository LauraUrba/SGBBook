from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from sgblivros.models import Livro
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy



from .utils import send_otp
from datetime import datetime, timedelta
from django.utils import timezone 
import pyotp

import re

def cadastra_usuario(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')

    elif request.method == "POST":
        nome_usuario = request.POST.get('nome_usuario', '').strip()
        nome = request.POST.get('nome', '').strip()
        sobrenome = request.POST.get('sobrenome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()

        # Verificação de campos obrigatórios
        if not nome or not sobrenome or not nome_usuario or not email or not senha:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('cadastro')

        # Verificação de formato de e-mail
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, 'E-mail em formato inválido.')
            return redirect('cadastro')

        # Verificação de força da senha
        if len(senha) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
            return redirect('cadastro')
        if not re.search(r'[A-Z]', senha):
            messages.error(request, 'A senha deve conter pelo menos uma letra maiúscula.')
            return redirect('cadastro')
        if not re.search(r'[a-z]', senha):
            messages.error(request, 'A senha deve conter pelo menos uma letra minúscula.')
            return redirect('cadastro')
        if not re.search(r'\d', senha):
            messages.error(request, 'A senha deve conter pelo menos um número.')
            return redirect('cadastro')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
            messages.error(request, 'A senha deve conter pelo menos um símbolo (ex: !@#$%).')
            return redirect('cadastro')

        # Verificação de nome de usuário já existente
        if User.objects.filter(username=nome_usuario).exists():
            messages.error(request, 'Nome de usuário já está em uso.')
            return redirect('cadastro')

        # Criação do usuário
        usuario = User.objects.create_user(
            username=nome_usuario,
            first_name=nome,
            last_name=sobrenome,
            email=email,
            password=senha
        )
        usuario.save()

        messages.success(request, 'Usuário cadastrado com sucesso!')
        return redirect('cadastro')



def loga_usuario(request):
    error_message = None
    segundos_restantes = None

    if 'tentativas_login' not in request.session:
        request.session['tentativas_login'] = 0
    if 'bloqueio_login' not in request.session:
        request.session['bloqueio_login'] = None

    bloqueio = request.session['bloqueio_login']
    if bloqueio:
        tempo_bloqueio = timezone.datetime.fromisoformat(bloqueio)
        agora = timezone.now()

        if agora < tempo_bloqueio:
            segundos_restantes = int((tempo_bloqueio - agora).total_seconds())
            error_message = f'Tentativas excedidas. Tente novamente em {segundos_restantes} segundos.'
            return render(request, 'login.html', {
                'error_message': error_message,
                'segundos_restantes': segundos_restantes
            })
        else:
            request.session['tentativas_login'] = 0
            request.session['bloqueio_login'] = None

    if request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=username, password=senha)

        if usuario is not None:
            request.session['tentativas_login'] = 0
            request.session['bloqueio_login'] = None
            send_otp(request, usuario)
            request.session['nome_usuario'] = username
            return redirect('otp')
        else:
            request.session['tentativas_login'] += 1
            if request.session['tentativas_login'] >= 3:
                tempo_bloqueio = timezone.now() + timedelta(seconds=10)
                request.session['bloqueio_login'] = tempo_bloqueio.isoformat()
                segundos_restantes = 10
                error_message = f'Muitas tentativas falhas. Tente novamente em {segundos_restantes} segundos.'

    return render(request, 'login.html', {
        'error_message': error_message,
        'segundos_restantes': segundos_restantes
    })


def otp_view(request):
    error_message = None

    if request.method == 'POST':
        otp = request.POST.get('otp')
        username = request.session.get('nome_usuario')
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_until = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_until:
            valid_until = datetime.fromisoformat(otp_valid_until)

            if datetime.now() < valid_until:
                totp = pyotp.TOTP(otp_secret_key, interval=300)
                if totp.verify(otp):
                    usuario = User.objects.filter(username=username).first()
                    if usuario:
                        usuario.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, usuario)

                        # Limpa a sessão
                        request.session.pop('otp_secret_key', None)
                        request.session.pop('otp_valid_date', None)
                        request.session.pop('nome_usuario', None)

                        return redirect('cadastro_livro')
                    else:
                        error_message = 'Usuário não encontrado.'
                else:
                    error_message = 'Código inválido. Tente novamente.'
            else:
                error_message = 'O código expirou. Solicite um novo login.'
        else:
            error_message = 'Sessão inválida. Tente novamente.'

    return render(request, 'otp.html', {'error_message': error_message})



def logout_usuario(request):
    logout(request)
    return render (request, 'login.html')


# Redefinir a senha - enviar email com link
def ForgetPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        try:
            usuario = User.objects.get(email=email)
            
            # Gera token seguro
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            
            # Cria o link de redefinição
            reset_link = f"http://127.0.0.1:8000/auth/NewPasswordPage/{uid}/{token}/"
            
            # Envia email
            send_mail(
                'Redefinição de senha - SGLivros',
                f"Olá, {usuario.username}!\n\n"
                f"Você solicitou a redefinição de senha.\n\n"
                f"Clique no link abaixo para redefinir sua senha:\n"
                f"{reset_link}\n\n"
                f"Este link expira em 24 horas.\n\n"
                f"Se você não solicitou esta redefinição, ignore este email.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            
            messages.success(request, 'Email enviado com sucesso! Verifique sua caixa de entrada.')
            return render(request, 'EmailEnviado.html', {
                'mensagem_sucesso': 'Um link de redefinição foi enviado para seu email.'
            })
            
        except User.DoesNotExist:
            # Por segurança, não revela se o email existe ou não
            messages.info(request, 'Se este email estiver cadastrado, você receberá um link de redefinição.')
            return render(request, 'EmailEnviado.html', {
                'mensagem_sucesso': 'Se o email estiver cadastrado, você receberá as instruções.'
            })
    
    return render(request, 'forget_password.html')


def NewPasswordPage(request, uidb64, token):
    """View para redefinir senha com token de segurança"""
    try:
        # Decodifica o ID do usuário
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None
    
    # Verifica se o usuário existe e se o token/senha é válido
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == "POST":
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')
            
            if not nova_senha or not confirmar_senha:
                messages.error(request, 'Preencha todos os campos!')
                return render(request, 'NewPassword.html', {'validlink': True, 'usuario': usuario})
            
            if nova_senha == confirmar_senha:
                if len(nova_senha) < 6:
                    messages.error(request, 'A senha deve ter no mínimo 6 caracteres!')
                    return render(request, 'NewPassword.html', {'validlink': True, 'usuario': usuario})
                
                usuario.set_password(nova_senha)
                usuario.save()
                messages.success(request, 'Senha redefinida com sucesso! Faça login com sua nova senha.')
                return redirect('login')
            else:
                messages.error(request, 'As senhas não coincidem!')
                return render(request, 'NewPassword.html', {'validlink': True, 'usuario': usuario})
        
        # GET request - mostra formulário
        return render(request, 'NewPassword.html', {'validlink': True, 'usuario': usuario})
    else:
        # Token inválido ou expirado
        messages.error(request, 'Link inválido ou expirado! Solicite um novo link de redefinição.')
        return render(request, 'NewPassword.html', {'validlink': False})

# Create your views here.
