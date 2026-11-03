"""Filtro de palavras obscenas para feedbacks, comentários, respostas e mensagens.

Regras:
  * compara PALAVRA INTEIRA (palavras comuns que contêm um trecho parecido não são bloqueadas);
  * ignora acentos, maiúsculas, letras repetidas e trocas comuns de letras por números/símbolos;
  * termos de biologia/educação sexual (pênis, vagina, sexo, ânus...) NÃO estão na lista de propósito.
A lista fica em HASHES (sem palavras legíveis); veja adicionar_palavrao.py para incluir novas.
"""
import hashlib
import re
import unicodedata
from markupsafe import Markup, escape

# Lista de palavras bloqueadas, guardada como HASHES (SHA-256): nenhuma palavra ofensiva fica escrita aqui.
# Para incluir uma palavra, rode:  python adicionar_palavrao.py  e cole o hash que aparecer abaixo.
HASHES = {
    '02cdc5daeafbc4ddc3eb948c1ee8bc6c874e326e6795be8849a24f9b4d97c700',
    '05e45b12b1e099373ff76174a29c810e8dfbdff85e0e4e825f43de8342307ac2',
    '06e0bd5e046ec3828806f3087ec92260b2af1d435ce7962bb98ddbfb4496d809',
    '0da9363e07820afc7b77fea98c90b7249a23ce544f8df22a7b37620a9bda1ed0',
    '0fc8c263b45e3f4443a778bee2eb470779a9638a6e51b4146f0135219cc167e7',
    '1080c3938c9cbc9de00e26fdd37b2e04964f44165c0a2229a02d532b2b33cde3',
    '11cfb3301e3d68799522330e466fd36bda0369d939a21b2617380fa358e167c5',
    '13841bb17efbc3d1099aca5c0d4ed6b7be04d1635682e64202435c104d54c502',
    '2212d86256fc6c982578d003ecf41865795a776935004fc3ab1886e8eb6b208e',
    '2beb6b5fe3d7bdf658da84d6ce4252d853f7d4865e025f6b3970e39a3777fd4f',
    '36106b2d067dbaa5139e16c9c0fe7c11b781183dd06e9b7b52e3e5cccb73a0c7',
    '3f3b5b8b6ada8ca34471c1942ec18f6a8d6a3f2ed0da27066b3f48c9933249b6',
    '489a845537412def5431c0b0022bac0022dd00dadcb971bf375c862e5b1f0085',
    '4f1a5468748a06b2aa793ccac6e40192e7df9f63683e516e07f73f3801c2879a',
    '5361e2902d88b3527d82b5e955c855032527a9414ff19020560bcb7c3fb82233',
    '547dcda36f49a3462cf4d1657659421be90acf0b7b3b77658aa0a9c58ff1fe78',
    '5977c64ed287e9077b968f61651239e98ce5b3f242642bdb04b3fa7e5fae7d36',
    '59e11dcffe7ad54cf629a803f156104a104d0ede1d64676fdb2319b1e66382e1',
    '5f5564c4ee1522a45694c6c1fd352d2912ded94641a00c5db4ef4c0e09ad1726',
    '634d28934cddcfa41a7676a2b9c3d994c8ea1586b9afba963f9f3bc5702ac473',
    '63c2402511b8bccd948e5d995b2696a98df1ed7c4780168d95b553c2b209b5dd',
    '66a65afbf25fc4de9327e7b1d489fe0e6ad113fbba84980c89ad83c4cfaa5b04',
    '6954b2217d69a9191034b49a02099b8c2b4563013fa9e9c3c30cfb41e4024602',
    '6ada028b2d096d946ddfb32453673d6116a10d664593ca86b73b6de12e060355',
    '702543ba8598564d3834a09982b42f3343249933e59228c0a15bb0e822a0aef5',
    '72f8b57bd33e19beacf2ec595411f0ae5360e65492e7c6ef9afd7e110f1c797f',
    '75f4c0fbd5a2d162181cfe4b8cc0afe08072054b03dfe61d3c7125962e3d3db6',
    '7ec2368c9eb1a6834f4e044fb077027df7a01dc007c31dfafe2e1f9fb58c25c8',
    '7f4bfdebf1a23458b860771bd2c1715a910fd91f691c4c195d35ccb9a5e4f6cc',
    '7f785f4b1f8187cbe43c71cce02fffe946056cfe865bcde8cd7c202341ee0a61',
    '861aaa0731bdaea1fa598d1750466ef6210c4a1cc1e39d3ea4f3ee4f1bc9e5a2',
    '8f78c0e64402db4305347a459dc4006b4b01fbc4563b899cb07aacbe86b3648f',
    '9ca5cf35db33571b965a1cff067908838568a98c545281b11e0fc48386a6b9e6',
    'ab54ba640504b1c93237fa996cc053f9e41c1ccfe1c8400ee3cdab489bfde950',
    'adfb510ad53730614118a3fd795f53d5b4315e2c234efc12c79ceeb38d0f7cd6',
    'af83ae81832416b80018e9d6d8a047a8c59e1a972a5d996fc3da679378d834fd',
    'b3208633abfe25c25a71cfd26ca66c766da5846577893bc4b1a01642116b9e33',
    'ba624ddd116f18406b1f1021967557179a6249957c008f8ac2471803fe755b72',
    'bbfdd53c04dbdd6b85de296e7492f53bb0ff96054235d794290cd562fb7fa8c4',
    'be09496edb44ce894b227a16db3e76fef2ae04a8a54047a94a5b0b6f85b453d9',
    'c0f9c42d0879573e1fcf23e080a8e919b33d5d428678c27a1c5695f7fd0c7b81',
    'c28a08a1a507d5c8ce1a24a6544850290d534e8da2ba92d04025a8dd199e3cd5',
    'c3b65f8156ea049cce296df32675170967cfbdfef79809c382adbf5f66f0dd96',
    'c5174ff1d726c4ae477f55bea38d4f673d433ca18fb15e343fc2f89b5482d063',
    'c7d5ec2f5cd6dc18c8209cb070903d272718937c5abf2b90c06bbb66631a1c80',
    'ca8ccf2990b2ebc7910a80304c811e9b52622d4828666cbf4fd18b8ca3f8f713',
    'cbeb0102202435f4c80d0ce7c5fb54070a2ab0a7e98f0fc57efd4005561a20c0',
    'cc06226a2bacacbe46235fcee060b73f70a8c559771f4544e97960e660b99f08',
    'ce741fee73f964f4d36ebc1d1ead6ca7dacd444c87242703a28f998d964b0306',
    'd0e51c388328d2a8ea18646dc7a43bdb05dc7dac51e2e4b81b6d1a4305d8f4d8',
    'df048168887984b5f0856fcc1012dfb3acff4a5c0d919d8e1d295a4387ddf0eb',
    'df4a054c422ceb99f55f0cf6431f0054caa2d98dd2dd15bc0ec72a6698515e25',
    'e026b556f630e9996951555f5bc72f1f67b6e0c9780ae721a101ccb0f2957c46',
    'e51d490d2db8ad9597e82fcdd77a0dd6b4c2b9a56aca1c6fe11065c62d2b4d4a',
    'e67be79550661604d9b9c646911c80d74f6c691613224c207fa7088c20698acd',
    'e9c276352ae61ffabadc9998fdcac5ad96df04f27400968b6cd5e9cc38ca652c',
}

_LEET = str.maketrans({'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a', '$': 's'})
_TOKEN = re.compile(r"[\w@$]+", re.UNICODE)


def _normalizar(palavra):
    p = unicodedata.normalize('NFD', palavra.lower())
    p = ''.join(c for c in p if unicodedata.category(c) != 'Mn')
    p = p.translate(_LEET)
    return re.sub(r'(.)\1+', r'\1', p)          # letras repetidas viram uma só


def _impropria(palavra):
    return len(palavra) >= 2 and hashlib.sha256(_normalizar(palavra).encode()).hexdigest() in HASHES


def encontrar(texto):
    """Lista das palavras impróprias encontradas (como o autor escreveu)."""
    return [m.group(0) for m in _TOKEN.finditer(texto or '') if _impropria(m.group(0))]


def tem_palavrao(texto):
    return bool(encontrar(texto))


def censurar(texto):
    """HTML seguro com cada palavra imprópria RASURADA (<del>). Serve também de filtro de template."""
    texto = texto or ''
    saida, ultimo = [], 0
    for m in _TOKEN.finditer(texto):
        if _impropria(m.group(0)):
            saida.append(escape(texto[ultimo:m.start()]))
            saida.append(Markup('<del class="palavrao" title="palavra imprópria">') + escape(m.group(0)) + Markup('</del>'))
            ultimo = m.end()
    saida.append(escape(texto[ultimo:]))
    return Markup('').join(saida)


MENSAGEM_BLOQUEIO = 'Você não pode publicar isso: remova as palavras rasuradas abaixo e tente de novo.'