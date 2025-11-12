import pyotp
from datetime import datetime, timedelta

def send_otp(request, usuario):
    # Gera o segredo apenas se ainda não estiver na sessão
    if not request.session.get('otp_secret_key'):
        request.session['otp_secret_key'] = pyotp.random_base32()

    # Usa o segredo armazenado para gerar o código
    totp = pyotp.TOTP(request.session['otp_secret_key'], interval=300)
    otp = totp.now()

    # Define validade do código
    valid_date = datetime.now() + timedelta(minutes=5)
    request.session['otp_valid_date'] = valid_date.isoformat()

    # Aqui você enviaria o OTP por email ou SMS
    print(f"Sua senha de uso único é: {otp}") # Para desenvolvimento
