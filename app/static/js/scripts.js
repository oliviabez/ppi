/*!
* SiteBio - scripts do tema
* Baseado em Start Bootstrap - Business Casual (MIT) https://startbootstrap.com/theme/business-casual
*/

// Busca de conteúdos na página inicial (filtra os cartões sem recarregar a página)
window.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('busca-conteudos');
    const cards = document.querySelectorAll('[data-busca]');
    if (!input || !cards.length) return;

    const aviso = document.getElementById('busca-sem-resultado');
    const normalizar = (texto) =>
        texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const filtrar = () => {
        const termo = normalizar(input.value.trim());
        let visiveis = 0;
        cards.forEach((card) => {
            const coincide = !termo || normalizar(card.dataset.busca).includes(termo);
            card.classList.toggle('d-none', !coincide);
            if (coincide) visiveis++;
        });
        if (aviso) aviso.style.display = visiveis ? 'none' : 'block';
    };

    input.addEventListener('input', filtrar);

    const form = document.getElementById('form-busca');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            filtrar();
            document.getElementById('conteudos').scrollIntoView({ behavior: 'smooth' });
        });
    }

    document.querySelectorAll('[data-termo]').forEach((chip) => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.termo;
            filtrar();
            input.focus();
        });
    });
});
