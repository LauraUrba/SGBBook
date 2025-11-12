from django.db import models

# Create your models here.
# trabalhamos com classes aqui 
# define o banco de dados - modela o banco de dados 

#chave estrangeira 
class Autor (models.Model):
    nome = models.CharField (max_length=150)
    sobrenome = models.CharField (max_length=500)
    data_nascimento = models.DateField (blank=True, null=True)
    nacionalidade = models.CharField (max_length=80, blank=True, null=True)

    '''
    def __str__(self):
        return f"{self.nome} {self.sobrenome}"
        '''

#chave primaria
class Livro(models.Model): #models.model indica que a classe Livro é um modelo do Django é padrão
    titulo = models.CharField(max_length=200) #CharField é um campo de texto com tamanho máximo definido
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='livros') #ForeignKey cria uma relação muitos-para-um com o modelo Autor
    ano_publicacao = models.PositiveIntegerField()
    editora = models.CharField(max_length=100, blank=True, null=True) #blank e null permitem que o campo seja opcional

    '''
    def __str__(self):
        return self.titulo
        '''
# Create your models here.

