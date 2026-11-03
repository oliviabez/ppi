"""Gera o hash de uma palavra para colocar em HASHES (app/services/filtro.py).
Uso:  python adicionar_palavrao.py   (digite a palavra; o hash é mostrado)
A palavra digitada NÃO é gravada em lugar nenhum."""
import hashlib
import re
import unicodedata

LEET = str.maketrans({'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a', '$': 's'})


def normalizar(palavra):
    p = unicodedata.normalize('NFD', palavra.lower())
    p = ''.join(c for c in p if unicodedata.category(c) != 'Mn').translate(LEET)
    return re.sub(r'(.)\1+', r'\1', p)


palavra = input('Palavra: ').strip()
print(f"    '{hashlib.sha256(normalizar(palavra).encode()).hexdigest()}',")