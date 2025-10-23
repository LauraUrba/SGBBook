"""
URL configuration for sgb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('index/', include('sgb_livros.urls')),
    path('livros/', include('sgblivros.urls')),
    path('auth/', include('sgbUsuarios.urls')),  # Adiciona as URLs do aplicativo sgb_usuarios
    path('accounts/', include('allauth.urls')),
    #path('SenhaReset/', include('sgb_usuarios.urls')), #senha/email e otp
    #path('codigo/', include('sgb_usuarios.urls')),

]
