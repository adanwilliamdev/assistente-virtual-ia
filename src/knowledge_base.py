"""
Base de conhecimento do LivroCerto.

Busca simples e sem dependências externas, baseada em sobreposição de palavras
entre o pedido da pessoa e os campos de cada livro. Melhorias desta versão:

- normalização sem acentos ("ficção" == "ficcao") e plural simples ("livros" == "livro");
- pequeno dicionário de sinônimos ("assustador" -> "terror");
- bônus quando o pedido menciona nível ("iniciante") ou tamanho ("curto") compatíveis;
- só retorna livros com relevância de conteúdo mínima, para o assistente poder
  admitir que não sabe em vez de forçar uma recomendação ruim.
"""

import json
import re
import unicodedata
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "livros.json"

# Abaixo disso (pontuação só de conteúdo), consideramos que não há bom match.
PONTUACAO_MINIMA = 3

STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "um", "uma", "uns", "umas",
    "e", "ou", "que", "com", "para", "por", "em", "no", "na", "nos", "nas", "se",
    "eu", "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
    "mais", "muito", "muita", "algo", "alguma", "algum", "quero", "queria",
    "gostaria", "voce", "livro", "livros", "sobre", "estou", "isso", "esse", "essa",
    "este", "esta", "ler", "leitura", "assistente", "recomende", "recomenda",
    "recomendacao", "indicacao", "pode", "preciso", "busco", "procuro", "tipo",
}

SINONIMOS = {
    "assustador": "terror", "assustadora": "terror", "medo": "terror",
    "arrepiante": "terror", "distopico": "distopia", "distopica": "distopia",
    "cientifico": "cientifica", "futurista": "futuro", "produtivo": "produtividade",
}

# Assuntos que o assistente não cobre (só vale se a pessoa não pedir um "livro").
FORA_DE_ESCOPO = {
    "investimento", "investir", "bolsa", "remedio", "medico", "doenca", "sintoma",
    "advogado", "juridico", "imposto", "dieta", "diagnostico",
}

PALAVRAS_NIVEL = {
    "iniciante": {"iniciante", "facil", "simples", "comecar", "comecando"},
    "avancado": {"avancado", "complexo", "dificil"},
}
PALAVRAS_TAMANHO = {
    "curto": {"curto", "curtos", "rapido", "rapida", "breve"},
    "longo": {"longo", "longos", "extenso", "grande"},
}


def carregar_livros(caminho: Path = CAMINHO_PADRAO) -> list[dict]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e sem pontuação."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texto)


def _radical(palavra: str) -> str:
    if len(palavra) > 4 and palavra.endswith("es"):
        return palavra[:-2]
    if len(palavra) > 3 and palavra.endswith("s"):
        return palavra[:-1]
    return palavra


def tokenizar(texto: str) -> list[str]:
    """Lista de radicais relevantes (sem stopwords, com sinônimos aplicados)."""
    saida = []
    for p in normalizar(texto).split():
        if p in STOPWORDS or len(p) <= 2:
            continue
        saida.append(_radical(SINONIMOS.get(p, p)))
    return saida


def _tamanho_do_livro(livro: dict) -> str:
    return normalizar(livro.get("tempo_leitura", "")).split(" ")[0]


def pontuar_livro(tokens: set[str], livro: dict, palavras: set[str] | None = None) -> dict:
    """
    Pontua um livro. Tags/gênero valem 3, sinopse e público-alvo valem 1.
    Nível e tamanho compatíveis com o pedido dão +2 (bônus, não contam para o mínimo).
    """
    t_tags = set(tokenizar(" ".join(livro.get("tags", []))))
    t_genero = set(tokenizar(livro.get("genero", "")))
    t_texto = set(tokenizar(livro.get("sinopse", "") + " " + livro.get("publico_alvo", "")))

    m_tags, m_genero, m_texto = tokens & t_tags, tokens & t_genero, tokens & t_texto
    conteudo = 3 * len(m_tags) + 3 * len(m_genero) + len(m_texto - m_tags - m_genero)

    bonus = 0
    palavras = palavras or set()
    for nivel, termos in PALAVRAS_NIVEL.items():
        if palavras & termos and normalizar(livro.get("nivel", "")) == nivel:
            bonus += 2
    for tamanho, termos in PALAVRAS_TAMANHO.items():
        if palavras & termos and _tamanho_do_livro(livro) == tamanho:
            bonus += 2

    motivos = [t for t in livro.get("tags", []) if set(tokenizar(t)) & tokens]
    if m_genero:
        motivos.insert(0, livro["genero"])
    return {"conteudo": conteudo, "bonus": bonus, "motivos": motivos}


def buscar(pergunta: str, livros: list[dict], top_k: int = 3, excluir_ids: set | None = None) -> list[dict]:
    """
    Retorna até top_k resultados {'livro','pontuacao','termos_usados','motivos'},
    do mais para o menos relevante. Livros abaixo de PONTUACAO_MINIMA não entram.
    """
    tokens = set(tokenizar(pergunta))
    if not tokens:
        return []
    palavras = set(normalizar(pergunta).split())
    excluir_ids = excluir_ids or set()

    resultados = []
    for livro in livros:
        if livro["id"] in excluir_ids:
            continue
        p = pontuar_livro(tokens, livro, palavras)
        if p["conteudo"] >= PONTUACAO_MINIMA:
            resultados.append({
                "livro": livro,
                "pontuacao": p["conteudo"] + p["bonus"],
                "termos_usados": set(p["motivos"]),
                "motivos": p["motivos"],
            })
    # desempate pela avaliação média
    resultados.sort(key=lambda r: (r["pontuacao"], r["livro"].get("avaliacao", 0)), reverse=True)
    return resultados[:top_k]


def listar(livros: list[dict], genero: str = "", nivel: str = "") -> list[dict]:
    """Catálogo filtrado, ordenado pela avaliação."""
    saida = [l for l in livros
             if (not genero or l["genero"] == genero) and (not nivel or l["nivel"] == nivel)]
    return sorted(saida, key=lambda l: l.get("avaliacao", 0), reverse=True)
