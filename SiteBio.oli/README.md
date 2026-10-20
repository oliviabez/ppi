# SiteBio — Plataforma educacional de Biologia (IFRN)

Projeto Final de PPI Biologia IFRN — Lívia Maria, Maria Antônia e Olivia Bezerra.

O visual usa o tema **Business Casual** (Start Bootstrap, licença MIT), adaptado com paleta verde,
imagens de biologia e novos componentes. O backend Flask (rotas, forms, models e services) é o mesmo do projeto original.

## Como rodar

```bash
pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000

> `email-validator` foi adicionado ao `requirements.txt`: o `UsuarioForm` usa o validador `Email()`, que exige esse pacote.

## Rotas

| Rota | Template | Layout do modelo usado |
|---|---|---|
| `/` | `index.html` | intro + cta (busca e cartões) + product-items + cta (perfis) |
| `/celula` | `celula.html` | about-heading (banner + caixa) + blocos `bg-faded` |
| `/citologia` | `citologia.html` | idem |
| `/dna` | `dna.html` | idem |
| `/continuidade` | `cont.html` | idem |
| `/educacao-sexual` | `ed.sex.html` | idem |
| `/manutencao` | `manutencao.html` | idem |
| `/quiz` (GET/POST) | `quiz.html` | about-heading + bloco `bg-faded` com `QuizForm` |
| `/auth` (GET/POST) | `auth.html` | about-heading + `LoginForm` e `UsuarioForm` |
| `/admin` (GET/POST) | `admin.html` | about-heading + `PublicacaoForm` |

Templates compartilhados: `base.html` (cabeçalho, navbar, rodapé) e `_macros.html` (`hero`, `errors`, `cta_quiz`).

## Estrutura

```
app/
  static/
    css/styles.css          # Bootstrap + tema (compilado, não edite à mão)
    js/                     # bootstrap.bundle.min.js e scripts.js (busca da home)
    assets/img/             # imagens de biologia e favicon
  templates/
theme/
  scss/                     # código-fonte do tema (edite aqui)
  tools/make_images.py      # gera as ilustrações de assets/img
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
