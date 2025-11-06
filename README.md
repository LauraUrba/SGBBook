# 2FA - AUTENTIÇÃO

# Autenticação com OTP e Recuperação de Senha no Django

Este projeto implementa autenticação em duas etapas (2FA) com código OTP gerado por PyOTP e enviado por email, além de recuperação de senha via link.

---

## Funcionalidades implementadas

- **Login com email e senha personalizado**
- **Geração de código OTP com PyOTP**
- **Envio do código por email usando `console.EmailBackend`**
- **Verificação do código digitado pelo usuário**
- **Reenvio de código OTP**
- **Recuperação de senha com `PasswordResetView`**

---

## Caminhos seguidos

1. **Criação do modelo `CustomUser`** com campo `email` como login e `otp_secret` para gerar códigos.
2. **Configuração do `AUTH_USER_MODEL`** no `settings.py`.
3. **Configuração do backend de email para testes:**

   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

4. **Views para login, envio e verificação de código OTP** usando métodos `generate_otp()` e `verify_otp()`.
5. **Templates personalizados para login, verificação e dashboard.**
6. **Recuperação de senha com `PasswordResetView`**, exibindo o conteúdo do email no terminal.

---

## Testes

- O código OTP e os emails de recuperação aparecem no terminal.
- O código expira automaticamente após 5 minutos.
- O fluxo completo pode ser testado localmente sem envio real de emails.

---

Se quiser, posso te ajudar a expandir esse README com instruções de instalação ou exemplos de uso. É só pedir!



*-----------------*

#  REDEFINÇÃO DE SENHA

## Visão Geral

Este módulo implementa, **de forma manual (sem uso das views prontas do Django)**, o processo completo de **redefinição de senha via e-mail**.
O sistema foi desenvolvido dentro do app `sgb_usuarios`, utilizando templates próprios e envio de e-mail através do **console** (modo de desenvolvimento).

---

## Funcionalidades Implementadas

* Página para solicitação de redefinição de senha.
* Envio de link de redefinição via e-mail (mostrado no terminal).
* Verificação de validade do link (token e UID).
* Formulário para definir uma nova senha.
* Mensagens de sucesso e erro personalizadas para o usuário.
* Tratamento de segurança para não expor se um e-mail está cadastrado ou não.

---

## Views Principais

### `ForgetPassword(request)`

View responsável por solicitar a redefinição de senha:

* O usuário informa o e-mail.
* Caso o e-mail exista, é gerado um token seguro com `default_token_generator`.
* O link é enviado para o e-mail do usuário (impresso no terminal no modo de desenvolvimento).
* Uma mensagem de sucesso é exibida, independentemente de o e-mail existir (por segurança).

### `NewPasswordPage(request, uidb64, token)`

View que recebe o link do e-mail e permite ao usuário definir uma nova senha:

* Decodifica o `uidb64` para identificar o usuário.
* Verifica se o token ainda é válido.
* Permite redefinir a senha com validação de tamanho e confirmação.
* Exibe mensagem apropriada para links expirados ou inválidos.

---

## Configuração de E-mail (modo desenvolvimento)

As configurações estão em `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@sgblivros.com'
EMAIL_HOST_USER = 'SGB_Admin@dominio.com'
```

💡 **Observação:**
O e-mail não é realmente enviado, mas exibido no terminal do servidor Django.
Em produção, pode ser alterado para SMTP real (por exemplo, Gmail).

---

## Funcionamento do Fluxo

1. Usuário acessa **“Esqueci minha senha”** (`forget_password.html`).
2. Informa seu e-mail e envia o formulário.
3. O sistema gera um token seguro e imprime o link de redefinição no terminal.
4. O usuário acessa o link (`NewPasswordPage/<uidb64>/<token>/`).
5. Define uma nova senha válida (mínimo 6 caracteres e confirmação).
6. O sistema salva a nova senha e redireciona o usuário ao login.

---

## Tecnologias Utilizadas

* **Django** (views, tokens e mensagens)
* **Templates HTML** personalizados
* **Mensagens de feedback (`django.contrib.messages`)**
* **Envio de e-mail com `send_mail()`**
* **Codificação de segurança:** `urlsafe_base64_encode`, `default_token_generator`

---

## Possíveis Melhorias Futuras

* Implementar envio real de e-mails via SMTP.
* Adicionar expiração real de token em banco de dados.
* Criar formulário de redefinição com `forms.py`.
* Customizar design com CSS e Bootstrap.

---

## Exemplo de E-mail Gerado no Console

```
Olá, usuario123!

Você solicitou a redefinição de senha.

Clique no link abaixo para redefinir sua senha:
http://127.0.0.1:8000/auth/NewPasswordPage/MQ/token-aqui/

Este link expira em 24 horas.

Se você não solicitou esta redefinição, ignore este e-mail.
```



*-----------------------------*

#  SEGURANÇA DE SENHA


Esta funcionalidade adiciona **verificação de segurança mínima para senhas** nos formulários de **login** e **cadastro de usuários** do sistema.
O objetivo é garantir que todos os usuários tenham senhas com pelo menos **8 caracteres**, reduzindo riscos de acesso não autorizado e fortalecendo a proteção das contas.

---

## Funcionalidades Implementadas

* Bloqueia o cadastro de senhas com menos de 8 caracteres.
* Exibe mensagens de erro e sucesso usando o sistema de mensagens do Django (`django.contrib.messages`).
* Valida também formato de e-mail e campos obrigatórios.
* Impede o uso de nomes de usuário duplicados.
* Apresenta alertas visuais de erro diretamente nas páginas de login e cadastro.


---

 **Destaques de segurança:**

* A senha precisa ter **no mínimo 8 caracteres**.
* Nenhum campo pode ficar em branco.
* E-mails são validados com **expressão regular (`regex`)**.
* Nomes de usuários duplicados são bloqueados.

---


## Regras de Segurança da Senha

1. Mínimo de **8 caracteres**.
2. Recomenda-se que contenha letras, números e caracteres especiais.
3. Nenhuma senha é salva em texto puro — o Django faz o **hash** automaticamente com `set_password()`.

---

## Funcionamento do Fluxo

1. O usuário acessa a página de **cadastro** e preenche todos os campos.
2. Se a senha tiver menos de 8 caracteres, o sistema exibe um alerta e bloqueia o cadastro.
3. Ao cadastrar-se corretamente, o sistema salva o novo usuário e mostra mensagem de sucesso.
4. Durante o **login**, o usuário insere suas credenciais e, se corretas, é direcionado para o **2FA (verificação por código OTP)**.

---

## Tecnologias Utilizadas

* **Django Framework**
* **Sistema de Mensagens (`django.contrib.messages`)**
* **Regex** para validação de e-mail
* **PyOTP** para autenticação em dois fatores (2FA)
* **HTML + Bootstrap** para feedback visual

---

## Possíveis Melhorias Futuras

* Implementar políticas de senha mais fortes (ex: obrigar letras maiúsculas e símbolos).
* Adicionar verificação de força de senha em tempo real com JavaScript.
* Usar `UserCreationForm` personalizado do Django para validação integrada.
* Adicionar bloqueio temporário após múltiplas tentativas de login incorretas.

# Tela de Cadastrar Autores

# Autenticação com OTP e Recuperação de Senha no Django

##Funcionalidades

   * Cadastro de autores com nome, sobrenome, data de nascimento e nacionalidade
   * Edição e exclusão de autores
   * Listagem de autores cadastrados
   * Interface responsiva com Bootstrap 5
   * Proteção de rotas com login obrigatório

   ## 🧠 Estrutura do Projeto

### 🔧 Backend (Django)

- **Modelos**:  
  ```python
  class Autor(models.Model):
      nome = models.CharField(max_length=150)
      sobrenome = models.CharField(max_length=500)
      data_nascimento = models.DateField(blank=True, null=True)
      nacionalidade = models.CharField(max_length=80, blank=True, null=True)
``
