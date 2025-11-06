from django.urls import path, include
from . import views

urlpatterns = [
    #path('index/', views.index, name='index'),
    
    path('livros/', views.livros, name='livros'),
    #path('salva_livros/', views.salvar_livro, name='salva_livros'),
    path('', views.cadastro_livro, name='cadastro_livro'),
    path('excluir/<int:livro_id>', views.exclui_livro, name='exclui_livro'),
    path('editar/<int:livro_id>', views.edita_livro, name='edita_livro'),

    # AUTORES
    path('autores/', views.autores, name='autores'),  # Página principal de autores
    path('cadastra_autor/', views.cadastra_autor, name='cadastra_autor'),
    path('excluir_autor/<int:autor_id>/', views.exclui_autor, name='exclui_autor'),
    path('editar_autor/<int:autor_id>/', views.edita_autor, name='edita_autor'),
]
