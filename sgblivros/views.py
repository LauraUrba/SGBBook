from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Livro, Autor
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


def livros (request):
    return render(request, 'livros.html')
    livros_cadastrados = Livro.objects.all()
    return render(request, 'sgb_livros/livros.html', {'livros': livros_cadastrados})


def salvar_livro(request):
    if request.method == 'POST':
        titulo_livro = request.POST['titulo_livro']
        autor_livro = request.POST['autor_livro']
        editora = request.POST['editora']
        return render(request, 'livros.html', context={
            'titulo_livro': titulo_livro,
            'autor_livro': autor_livro,
            'editora': editora
        })
    return HttpResponse('Método não permitido', status=405)


def index(request):
    return render(request, 'index.html')

#adicionar uma notação para proteger essa função só se tiver alogado no sistema 
@login_required
def cadastro_livro(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        titulo = request.POST['titulo']
        autor = request.POST['autor']
        ano_publicacao = request.POST['ano_publicacao']
        editora = request.POST['editora']

        if livro_id:  # Se o ID do livro for fornecido, atualize o livro existente
            try:
                livro = Livro.objects.get(id=livro_id)
                livro.titulo = titulo
                autor, created = Autor.objects.get_or_create(nome=autor)
                livro.autor = autor
                livro.ano_publicacao = ano_publicacao
                livro.editora = editora
                livro.save()
            except Livro.DoesNotExist:
                messages.error(request, 'Livro não encontrado para edição.')
        else:  # Caso contrário, crie um novo livro. Salva um livro
            autor = Autor.objects.create(nome=autor)
            Livro.objects.create(
                titulo=titulo,
                autor=autor,
                ano_publicacao=ano_publicacao,
                editora=editora
            )

        return redirect('cadastro_livro')

    livros = Livro.objects.all()
    autores = Autor.objects.all()
    return render(request, 'livros.html', {'livros': livros, 'autores': autores})



def exclui_livro(request, livro_id):
    #get_objects_or_404 tenta recuperar o objeto com o ID fornecido buscando no banco de dados e, 
    # se não encontrar, retorna um erro 404. Se encontrar o objeto, ele o retorna para 
    # que possa ser usado na função.
    livro = get_object_or_404(Livro, id=livro_id)
    livro.delete()
    return redirect('cadastro_livro')

def edita_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    livros = Livro.objects.all()  # Recupera todos os livros do banco de dados
    autores = Autor.objects.all()
    
    if request.method == 'POST':
        livro.titulo = request.POST['titulo']
        #livro.autor = request.POST['autor']
        autor = request.POST['autor']
        autor, created = Autor.objects.get_or_create(nome=autor)
        livro.autor = autor
        livro.ano_publicacao = request.POST['ano_publicacao']
        livro.editora = request.POST['editora']
        livro.save()
        return redirect('cadastro_livro')
    return render(request, 'livros.html', {'livros': livros, 'autores': autores, 'livro_editar': livro})



# AUTORES


def autores(request):
    autores = Autor.objects.all()
    return render(request, 'autor.html', {'autores': autores})

@login_required
def cadastra_autor(request):
    if request.method == 'POST':
        autor_id = request.POST.get('autor_id')
        nome = request.POST['nome']
        sobrenome = request.POST['sobrenome']
        data_nascimento = request.POST['data_nascimento']
        nacionalidade = request.POST['nacionalidade']

        if autor_id:
            try:
                autor = Autor.objects.get(id=autor_id)
                autor.nome = nome
                autor.sobrenome = sobrenome
                autor.data_nascimento = data_nascimento
                autor.nacionalidade = nacionalidade
                autor.save()
            except Autor.DoesNotExist:
                messages.error(request, 'Autor não encontrado para edição.')
        else:
            Autor.objects.create(
                nome=nome,
                sobrenome=sobrenome,
                data_nascimento=data_nascimento,
                nacionalidade=nacionalidade
            )

        return redirect('autores')  # redireciona para a lista de autores

    autores = Autor.objects.all()
    return render(request, 'autor.html', {'autores': autores})

def edita_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)

    if request.method == 'POST':
        autor.nome = request.POST['nome']
        autor.sobrenome = request.POST['sobrenome']
        autor.data_nascimento = request.POST['data_nascimento']
        autor.nacionalidade = request.POST['nacionalidade']
        autor.save()
        return redirect('autores')

    autores = Autor.objects.all()
    return render(request, 'autor.html', {'autor_editar': autor, 'autores': autores})

def exclui_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    autor.delete()
    return redirect('autores')