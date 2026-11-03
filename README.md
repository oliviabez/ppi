# SiteBio — Plataforma educacional de Biologia (IFRN)

Projeto Final de PPI Biologia IFRN — Lívia Maria, Maria Antônia e Olivia Bezerra.

Site em **Flask** com conteúdos de Biologia, quizzes, plano de estudos e área do administrador.
O visual usa o tema **Business Casual** (Start Bootstrap, licença MIT), adaptado com paleta verde.

## Perfis de usuário

| Perfil | O que faz |
|---|---|
| **Estudante** | lê os conteúdos, faz quizzes (resultado e erros ficam salvos), vê "Meus erros" e o plano de estudos, envia feedback e dúvidas, escreve para o e-mail de um administrador |
| **Público externo** | lê os conteúdos, faz quizzes (vê o que acertou e errou, nada é salvo), envia feedback |
| **Administrador** | publica e edita conteúdos, gerencia imagens, cria quizzes, responde dúvidas, vê usuários cadastrados e as porcentagens dos quizzes |

Depois do login: Administrador vai para `/admin`; Estudante e Público vão para `/modalidades`.
Para criar um administrador pelo cadastro é preciso o **código de administrador**
(padrão de desenvolvimento: `sitebio-admin`, veja "Variáveis de ambiente").

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
pip install pymysql            # necessário para o MySQL (não está no requirements.txt)
python run.py
```

Abra http://127.0.0.1:5000 — a primeira tela é o **login** 

## Banco de dados

O projeto está configurado para **MySQL**, direto em `app/__init__.py`:

```python
app.config['USAR_BANCO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Oi_olivk961@localhost/sitebio'
```

- Usuário: `root` · Senha: `Oi_olivk961` · Banco: `sitebio` (em `localhost`).
- Crie o banco antes: `CREATE DATABASE sitebio CHARACTER SET utf8mb4;`
- As tabelas são criadas sozinhas ao subir o servidor (`db.create_all()`). Tabelas novas aparecem
  sozinhas; **alterações em colunas de tabelas já existentes não são aplicadas** automaticamente.
- As variáveis `SITEBIO_USAR_BANCO` e `SITEBIO_DATABASE_URL`, citadas nos comentários do código,
  **não são lidas**: para trocar de banco, edite as duas linhas acima.
- **Modo memória (sem banco):** coloque `app.config['USAR_BANCO'] = False`. Os dados somem ao
  reiniciar e o sistema cria contas de teste (`app/services/memoria.py`):

  | Perfil | E-mail | Senha |
  |---|---|---|
  | Administrador | admin@sitebio.com | admin123 |
  | Estudante | aluno@sitebio.com | aluno123 |
  | Público externo | publico@sitebio.com | publico123 |

Para ver os usuários cadastrados no MySQL:

```sql
USE sitebio;
SELECT * FROM usuarios;
```

### Tabelas

| Tabela | Para que serve |
|---|---|
| `usuarios`, `conteudos`, `comentarios` | cadastro, conteúdos publicados, feedbacks e dúvidas |
| `quizzes`, `perguntas`, `resultados_quiz` | quizzes criados pelo admin e o resultado de cada tentativa de estudante |
| `respostas_quiz` | cada pergunta respondida por estudantes (base de "Meus erros", do plano e das porcentagens do admin) |
| `imagens_conteudo` | imagens enviadas pelo admin (em conteúdos publicados ou páginas fixas) |
| `respostas_comentario` | respostas do admin às dúvidas dos estudantes |
| `verificacoes_email` | códigos de recuperação de senha (guardados só como hash) |
| `paginas_editadas` | texto editado pelo admin nas páginas de conteúdo fixas |
| `config_site` | marcações internas (ex.: o quiz padrão já foi copiado para o banco) |

## Variáveis de ambiente

No Windows (cmd) use `set NOME=valor`; no PowerShell, `$env:NOME="valor"`. Elas valem só para
o terminal em que foram definidas, então defina **antes** de `python run.py`.

| Variável | Para que serve |
|---|---|
| `SITEBIO_SECRET_KEY` | chave da sessão. O padrão é de desenvolvimento: **troque em produção** |
| `SITEBIO_ADMIN_CODIGO` | código para se cadastrar como administrador (padrão `sitebio-admin`) |
| `SITEBIO_SMTP_HOST` | servidor de e-mail (ex.: `smtp.gmail.com`). Vazio = modo desenvolvimento |
| `SITEBIO_SMTP_PORT` | porta (padrão `587`; a `465` usa SSL) |
| `SITEBIO_SMTP_USUARIO` | e-mail que envia as mensagens |
| `SITEBIO_SMTP_SENHA` | senha do envio. No Gmail use uma **senha de app** (16 letras, sem espaços) |
| `SITEBIO_EMAIL_REMETENTE` | opcional; se vazio usa o usuário SMTP |

## E-mail

Exemplo com Gmail (conta com verificação em duas etapas e senha de app):

```
set SITEBIO_SMTP_HOST=smtp.gmail.com
set SITEBIO_SMTP_PORT=587
set SITEBIO_SMTP_USUARIO=seuemail@gmail.com
set SITEBIO_SMTP_SENHA=senhadeapp16letras
python run.py
```

**Sem `SITEBIO_SMTP_HOST`, nenhum e-mail sai de verdade:** o conteúdo é impresso no terminal
(modo desenvolvimento) e as telas mostram um aviso. Se o envio falhar, o motivo aparece no terminal
em `[SiteBio · ERRO AO ENVIAR E-MAIL]`.

O site envia e-mail em quatro situações:

- **Cadastro:** a conta é criada na hora e chega uma mensagem avisando que o cadastro foi realizado.
- **Esqueci minha senha:** código de 6 números (vale 15 minutos, 5 tentativas, 60 s entre pedidos).
- **Resposta do admin a uma dúvida:** o estudante é avisado (o e-mail tem *Reply-To* do admin).
- **Estudante escreve para um admin** (`/contato-admin`): a mensagem vai para o e-mail do admin
  escolhido (o estudante só vê os nomes dos admins), e a resposta volta para o e-mail do estudante.

## Rotas

| Rota | Quem acessa | O que é |
|---|---|---|
| `/auth`, `/cadastro` | todos | login e cadastro |
| `/esqueci-senha`, `/redefinir-senha` | todos | recuperação de senha por código |
| `/` | logado | redireciona para `/admin` ou `/modalidades` |
| `/modalidades` | logado | home: conteúdos, busca, novidades dos últimos 30 dias, desempenho (estudante) |
| `/celula` `/citologia` `/dna` `/continuidade` `/educacao-sexual` `/manutencao` | logado | conteúdos fixos |
| `/conteudo/<id>` | logado | conteúdo publicado pelo admin |
| `/quiz`, `/quiz/tema/<tema>`, `/quiz/<id>` | Estudante, Público | quizzes por conteúdo (admin é redirecionado para a área dele) |
| `/meus-erros`, `/plano-de-estudos` | Estudante | erros por quiz e plano semanal |
| `/feedback` (+ editar/excluir) | Estudante (feedback e dúvida), Público (feedback) | envios do próprio usuário, com as respostas do admin |
| `/contato-admin` | Estudante | e-mail para um administrador |
| `/perfil` (+ excluir) | logado | atualizar ou excluir o próprio cadastro |
| `/admin` | Admin | painel: números, conteúdos, páginas fixas, usuários, feedbacks |
| `/admin/conteudo/<id>/editar`, `/excluir`, `/imagens` | Admin | editar, excluir e anexar imagens a um conteúdo publicado |
| `/admin/pagina/<chave>/editar`, `/restaurar`, `/imagens` | Admin | editar o texto e as imagens das páginas fixas |
| `/admin/imagem/<id>/excluir` | Admin | remover uma imagem |
| `/admin/comentario/<id>/responder` | Admin | responder uma dúvida (avisa o estudante por e-mail) |
| `/admin/quizzes`, `/admin/quizzes/tema/<tema>`, `/novo`, `/<id>/editar`, `/<id>/excluir` | Admin | criar, editar e excluir quizzes por conteúdo |

(`/cadastro/confirmar` e `/cadastro/reenviar` ainda existem no código, mas o cadastro atual não usa.)

## Funcionalidades

### Conteúdos
- **Conteúdos fixos** (Célula, Citologia, DNA, Continuidade, Educação Sexual, Manutenção): o admin pode
  **editar o texto seção por seção** e **restaurar o original** (o texto original continua nos templates).
  O HTML digitado é limpo ao salvar (scripts, eventos e links perigosos são removidos).
- **Conteúdos publicados** pelo admin (título, tema, descrição e texto): aparecem em
  **Modalidades** como "Novidades dos últimos 30 dias" e ficam **dentro da página do tema**
  ("Mais conteúdos deste tema"). O tema Metabolismo aparece em `/continuidade` e `/manutencao`.
- **Imagens** (PNG, JPG, GIF ou WEBP, até 5 MB cada, 16 MB por envio): podem ser anexadas ao criar ou
  depois, em conteúdos publicados e nas páginas fixas. O tipo é conferido pelo conteúdo do arquivo.
  Ficam em `app/static/uploads/` com nome aleatório.

### Quizzes
- A aba **Quiz** mostra um quadrinho por conteúdo (5 temas); cada um abre os quizzes dele.
- O admin cria **vários quizzes por conteúdo** (perguntas com 4 alternativas A–D e uma correta),
  edita e exclui. O título de cada quiz precisa ser único.
- O **quiz padrão** ("Biologia Celular") é copiado para o banco uma única vez, no tema Célula, e depois
  é um quiz comum: pode ser editado e apagado (não volta).
- Ao final, estudante e público veem **o que erraram e a resposta certa**, sem porcentagem.
  O resultado só é salvo para **estudantes**.
- As **porcentagens** (média de acertos e acerto por pergunta) aparecem **só para o admin**, agregadas,
  sem nomes. A marca "(editável)" em títulos só aparece para administradores.
- No fim de cada conteúdo há o botão para os quizzes daquele conteúdo (não aparece para admin).

### Estudante
- **Meus erros:** perguntas erradas por quiz e os conteúdos com mais dúvidas (contagens, sem %).
- **Plano de estudos:** modelo semanal único (segunda a domingo) com todos os conteúdos; os até 2 temas com
  mais erros recebem **Reforço** (+20 min) e um quiz extra no domingo.
- **Feedback e dúvidas:** o admin pode responder as dúvidas, e a resposta aparece em "Minhas mensagens".

### Administrador
- Painel com números, lista de **usuários cadastrados** (estudantes, público e admins, com nome e e-mail),
  conteúdos, páginas fixas, feedbacks e dúvidas (com botão **Responder**).
- A lista de administradores é por nome e e-mail.

### Filtro de palavras obscenas
Feedbacks, dúvidas, respostas do admin e mensagens ao admin passam por um filtro
(`app/services/filtro.py`): o texto **não é publicado** ("Você não pode publicar isso") e a palavra aparece
**rasurada**. O filtro compara palavra inteira, ignora acentos, letras repetidas e trocas por números, e
**não bloqueia termos de biologia** (pênis, vagina, sexo...). Mensagens antigas também aparecem rasuradas.

A lista fica guardada como **hashes** (nenhuma palavra ofensiva escrita no código). Para incluir uma
palavra: rode `python palav.py`, digite a palavra e cole a linha gerada dentro de `HASHES` no `filtro.py`.

## Compartilhar para testes (sem hospedagem)

Com o site rodando em um terminal, abra outro e use o túnel gratuito da Cloudflare:

```
cloudflared-windows-amd64.exe tunnel --url http://localhost:5000
```

Ele mostra um link `https://....trycloudflare.com`. O link é temporário, muda ao reiniciar e só funciona
enquanto o seu computador e os dois terminais estiverem abertos. Os dados continuam no seu MySQL.

## Limitações e pontos de atenção

Também estão marcados no código com `LIMITAÇÃO`, `ATENÇÃO` e `TODO(BANCO)`.

- **Senha do banco e chave secreta no código:** a senha do MySQL está escrita em `app/__init__.py` e neste
  README. Se o código for publicado em lugar público (ex.: GitHub), remova-a antes.
- **Código de administrador e chave secreta** têm valor padrão de desenvolvimento: troque em produção.
- **`run.py` usa `debug=True`:** não use em produção; use um servidor como gunicorn ou waitress.
- **Cadastro sem confirmação de e-mail:** a conta é criada na hora, então é possível cadastrar um e-mail que
  não existe (o aviso de cadastro simplesmente não chega).
- **Login sem limite de tentativas** (força bruta) e sem bloqueio por IP.
- **Cookie de sessão:** ligar `SESSION_COOKIE_SECURE` ao publicar com HTTPS.
- **Contas de demonstração** só existem no modo memória; no modo banco não há contas de teste.
- **Quiz padrão:** como ele virou um quiz comum com um único tema, todas as suas perguntas contam no tema
  Célula ao calcular dúvidas e plano de estudos.
- **Editor de conteúdo fixo:** edição em HTML simples, sem editor visual; as edições ficam no banco.
- **Controle de usuários:** o admin só visualiza a lista (sem excluir ou editar contas).
- **Imagens enviadas** ficam na pasta `app/static/uploads/`. Em hospedagens com disco temporário elas se perdem.
- **E-mail:** sem SMTP configurado nada é enviado de verdade (só impresso no terminal).
- **PDFs** nos conteúdos ainda não existem. Sem paginação nas listas do admin e sem testes automatizados.
- **Comentários** são ligados a um tema (não a um conteúdo) e só o autor e os admins os veem.

## Estrutura do código

```
SiteBio/
├── run.py                          # inicia o servidor (porta 5000, debug ligado)
├── palav.py                        # gera o hash de uma palavra para o filtro de palavrões
├── requirements.txt                # flask, flask-wtf, wtforms, email-validator, flask-sqlalchemy
├── README.md
│
├── app/
│   ├── __init__.py                 # cria o app e configura banco, sessão, e-mail e uploads
│   ├── constantes.py               # perfis, temas, páginas fixas, tipos de feedback
│   ├── routes.py                   # TODAS as rotas, filtros de template e controle de acesso
│   │
│   ├── forms/                      # formulários (Flask-WTF / WTForms)
│   │   ├── __init__.py
│   │   ├── UsuarioForm.py          # cadastro, login, perfil, excluir conta
│   │   ├── PublicacaoForm.py       # novo conteúdo do admin
│   │   ├── ComentarioForm.py       # feedback / dúvida
│   │   ├── QuizForm.py             # perguntas do quiz padrão (usadas para copiá-lo ao banco)
│   │   └── AcessoForm.py           # esqueci senha, redefinir, responder dúvida, contato com admin
│   │
│   ├── models/                     # tabelas (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── usuario.py              # usuarios
│   │   ├── conteudo.py             # conteudos
│   │   ├── comentario.py           # comentarios
│   │   ├── quiz.py                 # quizzes, perguntas, resultados_quiz
│   │   └── extras.py               # imagens_conteudo, respostas_comentario, verificacoes_email,
│   │                               #   respostas_quiz, paginas_editadas, config_site
│   │
│   ├── services/                   # regras de negócio (funcionam em memória e no banco)
│   │   ├── __init__.py
│   │   ├── UsuarioService.py       # cadastro, login, atualizar, excluir
│   │   ├── ConteudoService.py      # conteúdos publicados
│   │   ├── FeedbackService.py      # feedbacks e dúvidas
│   │   ├── ResultadoService.py     # resultado de cada tentativa de quiz
│   │   ├── QuizService.py          # quizzes e perguntas; corrige respostas; copia o quiz padrão
│   │   ├── RespostaQuizService.py  # erros por aluno e porcentagens do admin
│   │   ├── PlanoService.py         # plano de estudos semanal
│   │   ├── RespostaService.py      # respostas do admin às dúvidas
│   │   ├── ImagemService.py        # upload, validação e remoção de imagens
│   │   ├── PaginaService.py        # edição do texto das páginas fixas
│   │   ├── EmailService.py         # envio por SMTP (ou impressão no terminal)
│   │   ├── VerificacaoService.py   # códigos de recuperação de senha
│   │   ├── filtro.py               # filtro de palavras obscenas (lista em hashes)
│   │   ├── sanitizar.py            # limpa o HTML digitado pelo admin
│   │   ├── repositorio.py          # acesso genérico: memória ou banco
│   │   └── memoria.py              # dados em memória e contas de demonstração
│   │
│   ├── templates/                  # páginas (Jinja)
│   │   ├── base.html               # layout, menu e rodapé
│   │   ├── _macros.html            # hero, galeria, revisão de erros, quiz do fim da página...
│   │   ├── erro.html
│   │   ├── auth.html  cadastro.html  cadastro_confirmar.html
│   │   ├── esqueci_senha.html  redefinir_senha.html  perfil.html
│   │   ├── modalidades.html        # home: conteúdos, busca, novidades, desempenho
│   │   ├── celula.html  citologia.html  dna.html  cont.html  ed.sex.html  manutencao.html
│   │   ├── conteudo.html           # conteúdo publicado pelo admin
│   │   ├── quiz.html  quiz_tema.html  quiz_dinamico.html
│   │   ├── meus_erros.html  plano.html
│   │   ├── feedback.html  contato_admin.html
│   │   ├── admin.html  admin_editar.html  admin_responder.html
│   │   ├── admin_pagina_editar.html  admin_pagina_imagens.html
│   │   └── admin_quizzes.html  admin_quiz_tema.html  admin_quiz_form.html
│   │
│   └── static/
│       ├── css/styles.css          # Bootstrap + tema (compilado, não edite à mão)
│       ├── js/                     # bootstrap.bundle.min.js e scripts.js (busca da home)
│       ├── assets/                 # favicon.ico e img/ (banners e ilustrações de biologia)
│       └── uploads/                # imagens enviadas pelo admin (criada automaticamente)
│
└── theme/
    ├── scss/                       # código-fonte do tema (edite aqui)
    │   ├── styles.scss  _global.scss  _variables.scss
    │   ├── variables/              # _colors.scss, _typography.scss
    │   ├── components/             # botões, formulários, navbar, overrides do Bootstrap
    │   └── sections/               # about, cards, content, cta, footer, intro, products, quiz
    ├── tools/make_images.py        # gera as ilustrações de assets/img
    ├── package.json  package-lock.json
    └── LICENSE-business-casual.txt
```

## Alterando cores e estilos

As cores ficam em `theme/scss/variables/_colors.scss` (`$primary`, `$secondary`, `$accent-dark`).
Depois de editar qualquer `.scss`, recompile o CSS:

```bash
cd theme
npm install
npm run build:css
```

As imagens podem ser regeneradas com `pip install pillow numpy && python theme/tools/make_images.py`
ou substituídas por fotos suas, mantendo os mesmos nomes de arquivo.