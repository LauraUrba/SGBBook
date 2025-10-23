from django.db import models

# Create your models here.
# trabalhamos com classes aqui 
class Livro(models.Model): #models.model indica que a classe Livro é um modelo do Django é padrão
    titulo = models.CharField(max_length=200) #CharField é um campo de texto com tamanho máximo definido
    autor = models.CharField(max_length=150)
    ano_publicacao = models.PositiveIntegerField()
    editora = models.CharField(max_length=100, blank=True, null=True) #blank e null permitem que o campo seja opcional

    def __str__(self):
        return self.titulo
# Create your models here.
