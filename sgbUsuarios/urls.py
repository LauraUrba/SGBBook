from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('cadastro', views.cadastra_usuario, name='cadastro'),
    path('login/', views.loga_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Password Reset - Email Enviado
    path('ForgetPassword/', views.ForgetPassword, name='forget_password'),
    path('NewPasswordPage/<uidb64>/<token>/', views.NewPasswordPage, name='new_password'),
    path('EmailEnviado/', TemplateView.as_view(template_name='EmailEnviado.html'), name='EmailEnviado'),
    
    path('otp/', views.otp_view, name='otp'),  # Adiciona a URL para a view otp_view
    
]