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

        # Verificação de senha com no mínimo 8 caracteres
        if len(senha) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
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
    """View de login com suporte a 2FA"""
    error_message = None

    if request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=username, password=senha)

        if usuario is not None:
            # Envia código OTP para o email do usuário
            send_otp(request, usuario)


            # Salva nome de usuário na sessão
            request.session['nome_usuario'] = username

            # Redireciona para a página de verificação do OTP
            return redirect('otp')
        else:
            error_message = 'Usuário ou senha incorretos.'

    # Renderiza o formulário de login (GET ou erro)
    return render(request, 'login.html', {'error_message': error_message})


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
