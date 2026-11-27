/*!
 * SiteBio - editor de texto visual do administrador.
 * Escreve-se direto na caixa (sem código). As imagens aparecem de verdade no texto e, ao salvar,
 * viram a marcação [imagem N] que o site já usa. Envio e remoção de imagens acontecem sem recarregar a página.
 */
(function () {
    'use strict';

    var estado = { imagens: [], ultimo: null, faixa: null };

    // ── lista de imagens (mesma ordem do servidor: a posição da imagem é o N de [imagem N]) ──
    function lerImagens() {
        var el = document.getElementById('dados-imagens');
        try { estado.imagens = el ? JSON.parse(el.textContent) : []; } catch (e) { estado.imagens = []; }
    }
    function numeroDa(id) {
        for (var k = 0; k < estado.imagens.length; k++) {
            if (String(estado.imagens[k].id) === String(id)) return k + 1;
        }
        return 0;
    }
    function imagemPorId(id) {
        for (var k = 0; k < estado.imagens.length; k++) {
            if (String(estado.imagens[k].id) === String(id)) return estado.imagens[k];
        }
        return null;
    }

    // ── figura (a imagem dentro da caixa de edição) ──
    function criarFigura(img) {
        var f = document.createElement('figure');
        f.className = 'figura-editor';
        f.setAttribute('contenteditable', 'false');
        f.setAttribute('data-img', img.id);
        var i = document.createElement('img');
        i.src = img.url; i.alt = img.legenda || 'Imagem'; i.draggable = false;
        f.appendChild(i);
        if (img.legenda) {
            var c = document.createElement('figcaption');
            c.textContent = img.legenda;
            f.appendChild(c);
        }
        var b = document.createElement('button');
        b.type = 'button'; b.className = 'figura-tirar'; b.title = 'Tirar a imagem do texto'; b.innerHTML = '&times;';
        f.appendChild(b);
        return f;
    }

    function paragrafoVazio() {
        var p = document.createElement('p');
        p.innerHTML = '<br>';
        return p;
    }
    function vazio(ed) {
        return ed.textContent.trim() === '' && !ed.querySelector('figure, img, table');
    }
    function preparar(ed) {
        if (vazio(ed)) { ed.innerHTML = '<p><br></p>'; return; }
        if (ed.lastElementChild && ed.lastElementChild.matches('figure.figura-editor')) ed.appendChild(paragrafoVazio());
    }

    // ── do editor para o que o servidor guarda ──
    function serializarHtml(ed) {
        var c = ed.cloneNode(true);
        Array.prototype.slice.call(c.querySelectorAll('figure.figura-editor')).forEach(function (f) {
            var n = numeroDa(f.getAttribute('data-img'));
            if (n) {
                var p = document.createElement('p');
                p.textContent = '[imagem ' + n + ']';
                f.parentNode.replaceChild(p, f);
            } else {
                f.parentNode.removeChild(f);
            }
        });
        Array.prototype.slice.call(c.querySelectorAll('p')).forEach(function (p) {
            if (!p.textContent.trim() && !p.querySelector('img')) p.parentNode.removeChild(p);
        });
        return c.innerHTML.trim();
    }

    function textoDoBloco(el) {
        var saida = '';
        (function andar(n) {
            Array.prototype.forEach.call(n.childNodes, function (x) {
                if (x.nodeType === 3) saida += x.nodeValue;
                else if (x.nodeName === 'BR') saida += '\n';
                else if (x.nodeType === 1) andar(x);
            });
        })(el);
        return saida.replace(/\u00a0/g, ' ');
    }
    function serializarTexto(ed) {
        var blocos = [], solto = '';
        function fechar() { if (solto.trim()) blocos.push(solto.trim()); solto = ''; }
        Array.prototype.forEach.call(ed.childNodes, function (n) {
            if (n.nodeType === 3) { solto += n.nodeValue.replace(/\u00a0/g, ' '); return; }
            if (n.nodeType !== 1) return;
            if (n.matches('figure.figura-editor')) {
                fechar();
                var k = numeroDa(n.getAttribute('data-img'));
                if (k) blocos.push('[imagem ' + k + ']');
                return;
            }
            if (n.nodeName === 'BR') { solto += '\n'; return; }
            fechar();
            var t = textoDoBloco(n).trim();
            if (t) blocos.push(t);
        });
        fechar();
        return blocos.join('\n\n');
    }
    function sincronizar(form) {
        Array.prototype.forEach.call(form.querySelectorAll('.editor-bloco'), function (bloco) {
            var ed = bloco.querySelector('.editor-texto');
            var campo = bloco.querySelector('textarea');
            if (vazio(ed)) { campo.value = ''; return; }
            campo.value = bloco.getAttribute('data-modo') === 'texto' ? serializarTexto(ed) : serializarHtml(ed);
        });
    }

    // ── janela de escolha da imagem ──
    function montarSeletor() {
        var dlg = document.getElementById('dlg-imagens');
        if (!dlg) return;
        var grade = dlg.querySelector('.grade-imagens');
        grade.innerHTML = '';
        estado.imagens.forEach(function (img) {
            var b = document.createElement('button');
            b.type = 'button'; b.className = 'escolha-imagem'; b.setAttribute('data-img', img.id);
            var i = document.createElement('img');
            i.src = img.url; i.alt = img.legenda || 'Imagem';
            b.appendChild(i);
            if (img.legenda) {
                var s = document.createElement('span');
                s.textContent = img.legenda;
                b.appendChild(s);
            }
            grade.appendChild(b);
        });
        dlg.querySelector('.sem-imagens').hidden = estado.imagens.length > 0;
    }
    function abrirSeletor(ed) {
        var dlg = document.getElementById('dlg-imagens');
        if (!dlg) return;
        estado.ultimo = ed;
        montarSeletor();
        if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    }
    function fecharSeletor() {
        var dlg = document.getElementById('dlg-imagens');
        if (!dlg) return;
        if (dlg.close) dlg.close(); else dlg.removeAttribute('open');
    }

    // A figura entra logo abaixo do parágrafo onde o cursor estava.
    function inserirImagem(id) {
        var img = imagemPorId(id);
        var ed = estado.ultimo || document.querySelector('.editor-texto');
        if (!img || !ed) return;
        var no = (estado.faixa && ed.contains(estado.faixa.startContainer)) ? estado.faixa.startContainer : null;
        while (no && no.parentNode !== ed) no = no.parentNode;
        var fig = criarFigura(img);
        if (no && no.nodeName === 'P' && !no.textContent.trim() && !no.querySelector('img')) {
            ed.insertBefore(fig, no);                       // parágrafo vazio: a figura ocupa o lugar dele
        } else {
            ed.insertBefore(fig, no ? no.nextSibling : null);
        }
        if (!fig.nextElementSibling) ed.appendChild(paragrafoVazio());
        fecharSeletor();
        if (fig.scrollIntoView) fig.scrollIntoView({ block: 'nearest' });
    }

    // ── imagens enviadas/removidas sem recarregar ──
    function campoCsrf(form) {
        return Array.prototype.slice.call(form.querySelectorAll('input[type=hidden]'));
    }
    function cartaoImagem(img, hiddens) {
        var col = document.createElement('div');
        col.className = 'col-md-4 text-center card-imagem';
        col.setAttribute('data-img', img.id);
        var i = document.createElement('img');
        i.className = 'img-fluid rounded mb-2'; i.src = img.url; i.alt = img.legenda || 'Imagem';
        col.appendChild(i);
        if (img.legenda) {
            var d = document.createElement('div'); d.className = 'small';
            var em = document.createElement('em'); em.textContent = img.legenda;
            d.appendChild(em); col.appendChild(d);
        }
        var f = document.createElement('form');
        f.method = 'POST'; f.action = img.excluir_url; f.className = 'form-remover-imagem';
        hiddens.forEach(function (h) { f.appendChild(h.cloneNode(true)); });
        var b = document.createElement('button');
        b.type = 'submit'; b.className = 'btn btn-sm btn-outline-danger mt-1'; b.textContent = 'Remover';
        f.appendChild(b);
        col.appendChild(f);
        return col;
    }
    function atualizarAvisoVazio() {
        var aviso = document.querySelector('.sem-imagens-aviso');
        if (aviso) aviso.hidden = estado.imagens.length > 0;
    }
    function adicionarImagem(img, form) {
        estado.imagens.push({ id: img.id, url: img.url, legenda: img.legenda });
        var lista = document.querySelector('.lista-imagens');
        if (lista) lista.appendChild(cartaoImagem(img, campoCsrf(form)));
        atualizarAvisoVazio();
        montarSeletor();
    }
    function removerImagem(id, cartao) {
        estado.imagens = estado.imagens.filter(function (x) { return String(x.id) !== String(id); });
        Array.prototype.forEach.call(document.querySelectorAll('figure.figura-editor'), function (f) {
            if (String(f.getAttribute('data-img')) === String(id)) {
                var ed = f.closest('.editor-texto');
                f.parentNode.removeChild(f);
                if (ed) preparar(ed);
            }
        });
        if (cartao) cartao.parentNode.removeChild(cartao);
        atualizarAvisoVazio();
        montarSeletor();
    }
    function avisar(form, texto, erro) {
        var el = form.querySelector('.aviso-imagens');
        if (!el) return;
        el.textContent = texto;
        el.className = 'aviso-imagens ms-2 small ' + (erro ? 'text-danger' : 'text-success');
    }
    function pedir(url, dados) {
        return fetch(url, {
            method: 'POST', body: dados, credentials: 'same-origin',
            headers: { 'X-Requested-With': 'fetch', 'Accept': 'application/json' }
        }).then(function (r) { return r.json(); });
    }
    function enviarImagens(form) {
        var botao = form.querySelector('button[type=submit]');
        if (botao) botao.disabled = true;
        avisar(form, 'Enviando…', false);
        pedir(form.action, new FormData(form)).then(function (res) {
            (res.imagens || []).forEach(function (img) { adicionarImagem(img, form); });
            var erros = res.erros || [];
            if (erros.length) avisar(form, erros.join(' '), true);
            else avisar(form, (res.imagens || []).length + ' imagem(ns) adicionada(s). Use "Inserir imagem" no texto.', false);
            if ((res.imagens || []).length) form.reset();
            if (botao) botao.disabled = false;
        }).catch(function () { form.submit(); });      // se algo falhar, envia do jeito normal
    }

    // ── eventos ──
    document.addEventListener('selectionchange', function () {
        var sel = window.getSelection();
        if (!sel || !sel.rangeCount || !sel.anchorNode) return;
        var n = sel.anchorNode.nodeType === 1 ? sel.anchorNode : sel.anchorNode.parentNode;
        var ed = n && n.closest ? n.closest('.editor-texto') : null;
        if (ed) { estado.ultimo = ed; estado.faixa = sel.getRangeAt(0).cloneRange(); }
    });

    // Os botões não podem roubar o foco/seleção do texto.
    document.addEventListener('mousedown', function (e) {
        if (e.target.closest && e.target.closest('.editor-barra button')) e.preventDefault();
    });

    document.addEventListener('click', function (e) {
        var alvo = e.target;
        if (!alvo.closest) return;

        var tirar = alvo.closest('.figura-tirar');
        if (tirar) {
            var f = tirar.closest('figure'), ed = f.closest('.editor-texto');
            f.parentNode.removeChild(f);
            if (ed) preparar(ed);
            return;
        }
        var escolha = alvo.closest('.escolha-imagem');
        if (escolha) { inserirImagem(escolha.getAttribute('data-img')); return; }
        if (alvo.closest('[data-acao="fechar-imagens"]')) { fecharSeletor(); return; }

        var btn = alvo.closest('.editor-barra button');
        if (!btn) return;
        var bloco = btn.closest('.editor-bloco'), editor = bloco.querySelector('.editor-texto');
        if (btn.getAttribute('data-acao') === 'imagem') {
            if (!(estado.faixa && editor.contains(estado.faixa.startContainer))) estado.faixa = null;
            abrirSeletor(editor);
            return;
        }
        var cmd = btn.getAttribute('data-cmd');
        if (!cmd) return;
        editor.focus();
        if (cmd === 'createLink') {
            var url = prompt('Endereço do link (comece com https://):', 'https://');
            if (url && /^(https?:\/\/|mailto:)/i.test(url.trim())) document.execCommand('createLink', false, url.trim());
        } else {
            document.execCommand(cmd, false, null);
        }
    });

    // Colar sempre como texto simples (não traz fontes e cores de outros sites).
    document.addEventListener('paste', function (e) {
        if (!e.target.closest || !e.target.closest('.editor-texto')) return;
        e.preventDefault();
        var t = (e.clipboardData || window.clipboardData).getData('text/plain');
        document.execCommand('insertText', false, t);
    });

    // No modo "texto simples" não há negrito/itálico: bloqueia os atalhos para não parecer que vai salvar.
    document.addEventListener('keydown', function (e) {
        var ed = e.target.closest ? e.target.closest('.editor-bloco[data-modo="texto"] .editor-texto') : null;
        if (ed && (e.ctrlKey || e.metaKey) && /^[biu]$/i.test(e.key)) e.preventDefault();
    });

    document.addEventListener('submit', function (e) {
        var f = e.target;
        if (f.classList.contains('editor-form')) { sincronizar(f); return; }
        if (f.classList.contains('form-remover-imagem')) {
            if (e.defaultPrevented) return;                  // o usuário cancelou no "Remover esta imagem?"
            e.preventDefault();
            var cartao = f.closest('.card-imagem');
            pedir(f.action, new FormData(f)).then(function (res) {
                if (res && res.ok) removerImagem(cartao.getAttribute('data-img'), cartao);
                else f.submit();
            }).catch(function () { f.submit(); });
            return;
        }
        if (f.classList.contains('form-enviar-imagens')) {
            e.preventDefault();
            enviarImagens(f);
        }
    });

    window.addEventListener('DOMContentLoaded', function () {
        try { document.execCommand('defaultParagraphSeparator', false, 'p'); } catch (e) {}
        lerImagens();
        Array.prototype.forEach.call(document.querySelectorAll('.editor-texto'), preparar);
        montarSeletor();
    });
})();
