# SiteBio — Plataforma educacional de Biologia (IFRN)

Projeto final de PPI Biologia IFRN. Site em Flask com conteúdos de Biologia, quizzes, plano de estudos e área administrativa.

## Perfis e funcionalidades

- **Estudante:** conteúdos, quizzes com resultados salvos (ao enviar, vê as respostas e pode refazer do zero quando quiser), meus erros, plano de estudos com horários, feedback e dúvidas.
- **Público externo:** conteúdos, quizzes sem salvar resultados e envio de feedback.
- **Administrador:** gerenciamento de conteúdos (editor de texto visual, com imagens no meio do texto), imagens, quizzes, páginas fixas, dúvidas, feedbacks publicáveis e visualização de usuários. Cada conteúdo mostra quem o publicou, e o painel avisa sobre novidades de outros administradores.

## Estrutura

```text
SiteBio/
├── config.py                 # configurações carregadas do ambiente
├── .env.example              # modelo das variáveis locais (copie para .env)
├── .gitignore
├── run.py
├── requirements.txt
├── scripts/
│   └── adicionar_palavrao.py  # gera o hash de uma palavra para o filtro de obscenidades
├── migrations/               # configuração do Flask-Migrate (já vem no projeto; as versões são geradas com `db migrate`)
└── app/
    ├── __init__.py           # cria o app e registra os Blueprints
    ├── constantes.py
    ├── hooks.py              # login obrigatório, variáveis de template e páginas de erro
    ├── template_filters.py   # filtros Jinja (data_br, censurar, ...)
    ├── utils.py              # perfis_permitidos, exigir_csrf, recente, pagina_inicial
    ├── routes/               # um Blueprint por área do site
    │   ├── acesso.py         # login, cadastro (com confirmação do e-mail), sair, recuperar senha
    │   ├── conteudo.py       # modalidades e páginas de conteúdo
    │   ├── quiz.py           # quizzes, meus erros, plano de estudos
    │   ├── perfil.py         # editar/excluir o próprio cadastro
    │   ├── feedback.py       # feedbacks, dúvidas e contato com o admin
    │   ├── admin.py          # conteúdos, imagens e respostas
    │   ├── admin_quiz.py     # quizzes do admin
    │   └── admin_pagina.py   # edição das páginas fixas
    ├── forms/
    │   └── validators.py     # validadores compartilhados (Email, Codigo)
    ├── models/               # um arquivo por model
    ├── services/             # regras de negócio (classes em PascalCase; módulos de funções em minúsculo)
    │   ├── DBRepository.py   # persistência exclusivamente SQLAlchemy
    │   ├── filtro.py         # filtro de palavras obscenas (tem_palavrao, censurar, bloquear_se_palavrao)
    │   ├── imagem_texto.py   # imagens no meio do texto (converte a figura do editor em [imagem N] e vice-versa)
    │   └── mensagens_email.py # textos dos e-mails
    ├── static/
    └── templates/
        ├── admin/
        ├── auth/
        ├── conteudo/
        ├── quiz/
        └── shared/
```

## Como instalar e executar

Requisitos: Python 3.10+ e MySQL em execução.

1. Crie o banco no MySQL:

```sql
CREATE DATABASE sitebio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Copie `.env.example` para `.env` e ajuste `SITEBIO_DATABASE_URL` com usuário e senha do seu MySQL. Exemplo:

```text
SITEBIO_DATABASE_URL=mysql+pymysql://root:SUA_SENHA@localhost/sitebio
```

5. Crie as tabelas (veja a seção *Banco de dados e migrations*). A pasta `migrations/` já vem no projeto, então **não** rode `db init`:

```bash
python -m flask --app run.py db migrate -m "Criacao inicial"
python -m flask --app run.py db upgrade
```

6. Inicie o sistema:

```bash
python run.py
```

Abra http://127.0.0.1:5000.

**Importante:** o SiteBio usa exclusivamente MySQL. Não existe usuário de teste criado automaticamente. Para criar o primeiro administrador, defina `SITEBIO_ADMIN_CODIGO` no `.env` e veja *Contas de administrador* abaixo.

## Configuração (.env)

| Variável | Finalidade |
|---|---|
| `SITEBIO_SECRET_KEY` | chave secreta das sessões; use um valor aleatório forte |
| `SITEBIO_ADMIN_CODIGO` | código de administrador (cadastro, login e alteração do cadastro); sem valor padrão no código |
| `SITEBIO_DATABASE_URL` | URL de conexão com MySQL |
| `SITEBIO_COOKIE_SECURE` | use `1` somente quando o site estiver publicado com HTTPS |
| `SITEBIO_SMTP_HOST` | servidor SMTP; vazio mantém envio em modo de desenvolvimento |
| `SITEBIO_SMTP_PORT` | porta SMTP (padrão 587) |
| `SITEBIO_SMTP_USUARIO` | conta remetente |
| `SITEBIO_SMTP_SENHA` | senha de app/SMTP |
| `SITEBIO_EMAIL_REMETENTE` | remetente opcional; por padrão usa o usuário SMTP |

Nunca envie o arquivo `.env` para GitHub ou compartilhe sua senha do banco. Se uma senha real já foi incluída em um ZIP ou repositório, altere-a no MySQL.

## Banco de dados e migrations

As tabelas são criadas **somente** pelo Flask-Migrate (o app não chama `db.create_all()`). A pasta `migrations/` já vem configurada, mas sem nenhuma versão dentro; a primeira versão é gerada na sua máquina:

```bat
python -m flask --app run.py db migrate -m "Criacao inicial"
python -m flask --app run.py db upgrade
```

Sempre que alterar um model:

```bat
python -m flask --app run.py db migrate -m "descreva a alteração"
python -m flask --app run.py db upgrade
```

**Banco que já tem as tabelas** (criado antes pelo `create_all`): depois do `db migrate`, rode `python -m flask --app run.py db stamp head` em vez do `upgrade`, para não tentar recriar tabelas que já existem.

**Colunas novas nesta versão** (entram na primeira migration, ou no próximo `db migrate` se o banco já existe): `conteudos.autor_id` e `conteudos.autor_nome`, `comentarios.permite_publicar` e `comentarios.publicado`, e em `verificacoes_email` as colunas `nome`, `senha_hash` e `perfil` (guardam o cadastro pendente até o e-mail ser confirmado).

Faça backup antes de aplicar migrations em um banco com dados importantes.

## E-mail

O e-mail é usado para **confirmar o cadastro** (código de 6 números: só depois de digitá-lo a conta é criada, o que garante que o e-mail existe), recuperar a senha e avisar sobre respostas. Sem `SITEBIO_SMTP_HOST`, o envio real fica desativado e as mensagens (incluindo o código) são registradas no terminal; nesse modo **não há verificação real** de que o e-mail existe. Para Gmail, configure SMTP com uma senha de app:

```text
SITEBIO_SMTP_HOST=smtp.gmail.com
SITEBIO_SMTP_PORT=587
SITEBIO_SMTP_USUARIO=seuemail@gmail.com
SITEBIO_SMTP_SENHA=sua_senha_de_app
```

## Observações de segurança e produção

- `SECRET_KEY` tem valor de desenvolvimento no código de configuração; substitua-o no `.env`. O `SITEBIO_ADMIN_CODIGO` não tem valor padrão: só existe no `.env`.
- O servidor de desenvolvimento usa `debug=True`; não use essa opção em produção.
- Configure HTTPS e `SITEBIO_COOKIE_SECURE=1` quando publicar.
- O login (inclusive o código de administrador) ainda não tem limitação de tentativas.
- Não há paginação nas listas administrativas nem testes automatizados.
- O administrador visualiza os usuários, mas ainda não edita/exclui contas.
- Os uploads ficam em `app/static/uploads/`; mantenha backup se a hospedagem tiver disco temporário.

## Sobre a organização

- **Rotas:** divididas em Blueprints por área (`app/routes/`). Os endereços (URLs) continuam os mesmos; só os nomes internos dos endpoints ganharam o prefixo do Blueprint (ex.: `url_for('acesso.auth')`, `url_for('admin.admin')`).
- **Regras de negócio:** ficam nos `services/` (validação do cadastro, leitura/validação dos formulários de quiz e de páginas, textos de e-mail). As rotas cuidam só de receber a requisição e devolver a resposta.
- **Services:** os métodos são `@staticmethod`/`@classmethod`; use `UsuarioService.buscar_por_id(...)` direto, sem instanciar e sem criar apelidos (`servico = ...`).
- **Filtro de palavrão:** as rotas que recebem texto livre (feedback, resposta do admin, contato) usam a mesma função, `filtro.bloquear_se_palavrao(...)`, em vez de repetir o bloco.
- **Páginas fixas:** a lista fica em `PAGINAS_FIXAS` e `MENU_CONTEUDOS` (`app/constantes.py`), mais `BLOCOS`/`SEMANA` em `PlanoService` e, para uma página nova, a rota e o template. Os nomes das páginas devem ser iguais em todos esses lugares.
- **Cadastro em dois passos:** `/cadastro` valida os dados e envia o código; `/cadastro/confirmar` cria a conta. Os dados pendentes ficam em `verificacoes_email` (senha já em hash).
- **Convenção de nomes em `services/`:** arquivos com uma classe em PascalCase (`QuizService.py`, `DBRepository.py`); módulos de funções em minúsculo (`filtro.py`, `sanitizar.py`, `mensagens_email.py`).
- **Logs:** o modo de desenvolvimento do e-mail (sem SMTP) e os erros de envio usam o `logging` do Flask.

## Contas de administrador

Existe **um código de administrador único**, guardado só no `.env` (não está escrito em nenhum arquivo do projeto):

```text
SITEBIO_ADMIN_CODIGO=admin-sua-frase-secreta
```

Sugestão: comece o código com `admin` (ex.: `admin-bio-2026`). Sem esse valor, contas de administrador não podem ser criadas e os administradores existentes não conseguem entrar.

- **Cadastro:** ao escolher o perfil *Administrador*, a pessoa informa o código.
- **Login:** administradores preenchem também o código (o campo é opcional para os demais usuários). Qualquer erro mostra a mesma mensagem, sem revelar qual dado falhou.
- **Meu cadastro:** o administrador precisa digitar o código para salvar qualquer alteração.
- Para trocar o código, edite o `.env` e reinicie o servidor; vale para todos os administradores.

## Editor de texto visual e imagens no meio do texto

- O administrador escreve direto na caixa de texto, sem código: Enter cria um novo parágrafo. Nas páginas fixas há botões de negrito, itálico, lista e link; as partes (título + texto) podem ser movidas ou inseridas logo abaixo de outra.
- Para colocar uma imagem **no meio do texto**: clique no lugar desejado e use **Inserir imagem**, escolhendo a miniatura. A imagem aparece de verdade na caixa de edição; para tirá-la, clique no ×. Imagens não colocadas no texto aparecem **centralizadas** no final.
- Por baixo dos panos, a figura é gravada como `[imagem N]` (N = posição da imagem na lista), então o site público e o banco continuam iguais. Ao remover uma imagem, ela some do texto e as seguintes são renumeradas automaticamente.
- O envio e a remoção de imagens acontecem sem recarregar a página, então o texto digitado não se perde (código em `static/js/editor-visual.js`).

## Feedbacks publicáveis

Ao enviar um feedback ou comentário, o usuário pode marcar *Permito que o SiteBio publique esta mensagem*. Só nesse caso o administrador vê o botão **Publicar no site**; a mensagem aparece em *O que a comunidade diz* (página de modalidades) com apenas o primeiro nome do autor. Se o autor editar o texto ou retirar a autorização, a mensagem sai do ar até ser aprovada de novo.

## Plano de estudos

O estudante escolhe o **tempo por dia** (30 min a 3 h) e a **hora de início**; o plano mostra o horário de cada etapa, o total de cada dia e da semana. Dias com tema de dúvida (*Reforço*) ganham +15 min, e o domingo inclui quiz extra desses temas e até 3 conteúdos publicados recentes.
