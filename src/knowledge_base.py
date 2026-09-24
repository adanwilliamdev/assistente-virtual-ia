"""
Base de conhecimento do LivroCerto.

Implementa uma busca simples, sem dependências externas, baseada em sobreposição
de palavras-chave entre o pedido da pessoa usuária e os campos de cada livro
(gênero, tags e sinopse). É um protótipo intencionalmente simples: não usa
embeddings nem modelos de linguagem para a busca, o que torna o comportamento
fácil de entender, testar e explicar na avaliação (Passo 5).
"""

import json
import re
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "livros.json"

# Lista pequena de stopwords em português, suficiente para um protótipo.
STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "um", "uma", "uns", "umas",
    "e", "ou", "que", "com", "para", "por", "em", "no", "na", "nos", "nas", "se",
    "eu", "eu", "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
    "mais", "muito", "muita", "algo", "alguma", "algum", "quero", "queria",
    "gostaria", "voce", "você", "livro", "livros", "sobre", "estou", "isso",
    "esse", "essa", "este", "esta", "ler", "leitura", "assistente", "recomende",
    "recomenda", "recomendacao", "recomendação", "indicacao", "indicação", "pode",
}


def carregar_livros(caminho: Path = CAMINHO_PADRAO) -> list[dict]:
    """Carrega a base de conhecimento a partir do arquivo JSON."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def tokenizar(texto: str) -> list[str]:
    """Normaliza um texto em uma lista de palavras relevantes (minúsculas, sem stopwords)."""
    texto = texto.lower()
    texto = re.sub(r"[^\w\sà-ú]", " ", texto)
    palavras = texto.split()
    return [p for p in palavras if p not in STOPWORDS and len(p) > 2]


def _tokens_do_livro(livro: dict) -> dict:
    """Pré-tokeniza os campos de um livro usados na busca."""
    return {
        "tags": set(tokenizar(" ".join(livro.get("tags", [])))),
        "genero": set(tokenizar(livro.get("genero", ""))),
        "sinopse": set(tokenizar(livro.get("sinopse", ""))),
    }


def pontuar_livro(tokens_pergunta: set[str], livro: dict) -> tuple[float, set[str]]:
    """
    Calcula a pontuação de relevância de um livro para os tokens da pergunta.

    Correspondências em 'tags' e 'genero' valem mais (peso 3) do que correspondências
    apenas na 'sinopse' (peso 1), porque tags e gênero descrevem a essência do livro
    de forma mais direta.
    """
    tokens_livro = _tokens_do_livro(livro)

    match_tags = tokens_pergunta & tokens_livro["tags"]
    match_genero = tokens_pergunta & tokens_livro["genero"]
    match_sinopse = tokens_pergunta & tokens_livro["sinopse"]

    pontuacao = len(match_tags) * 3 + len(match_genero) * 3 + len(match_sinopse) * 1
    termos_usados = match_tags | match_genero | match_sinopse
    return pontuacao, termos_usados


def buscar(pergunta: str, livros: list[dict], top_k: int = 3) -> list[dict]:
    """
    Busca os livros mais relevantes para a pergunta da pessoa usuária.

    Retorna uma lista (possivelmente vazia) de dicionários com as chaves:
    'livro', 'pontuacao' e 'termos_usados', ordenada da maior para a menor pontuação.
    Só livros com pontuacao > 0 entram no resultado.
    """
    tokens_pergunta = set(tokenizar(pergunta))
    if not tokens_pergunta:
        return []

    resultados = []
    for livro in livros:
        pontuacao, termos_usados = pontuar_livro(tokens_pergunta, livro)
        if pontuacao > 0:
            resultados.append({
                "livro": livro,
                "pontuacao": pontuacao,
                "termos_usados": termos_usados,
            })

    resultados.sort(key=lambda item: item["pontuacao"], reverse=True)
    return resultados[:top_k]
