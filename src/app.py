"""
LivroCerto — Assistente Virtual de Recomendação de Livros.

Núcleo do assistente + aplicação de linha de comando (Passo 4 do desafio).
A interface web está em src/server.py (python src/server.py).

Modo local (padrão): busca por palavras-chave + templates, sem chave de API.
Modo IA (opcional): com ANTHROPIC_API_KEY, o Claude reescreve a resposta, mas só
vê os livros que a busca local já filtrou.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import knowledge_base as kb
import llm_client
from prompts import MENSAGEM_FORA_ESCOPO, MENSAGEM_SAUDACAO, MENSAGEM_SEM_INFORMACAO

PONTUACAO_MINIMA = kb.PONTUACAO_MINIMA  # mantido para compatibilidade com avaliar.py
SAUDACOES = {"oi", "ola", "bom", "boa", "dia", "tarde", "noite", "e", "ai", "opa", "hey", "ajuda", "help"}
PALAVRAS_DE_LIVRO = {"livro", "livros", "ler", "leitura", "romance", "autor"}


def _resposta(tipo: str, texto: str, modo: str = "local", livros: list | None = None) -> dict:
    return {"tipo": tipo, "texto": texto, "modo": modo, "livros": livros or []}


def _serializar(item: dict) -> dict:
    return {**item["livro"], "motivos": item["motivos"], "pontuacao": item["pontuacao"]}


def formatar_resposta_local(livros: list[dict]) -> str:
    """Resposta em texto puro (usada no terminal e como fallback sem IA)."""
    linhas = ["Encontrei estas opções na minha base de conhecimento:\n"]
    for i, l in enumerate(livros, start=1):
        motivos = ", ".join(l["motivos"]) or "correspondência geral"
        linhas.append(
            f"{i}. {l['titulo']} — {l['autor']} ({l['genero']})\n"
            f"   {l['sinopse']}\n"
            f"   Tempo de leitura: {l['tempo_leitura']} | Nível: {l['nivel']} | "
            f"Avaliação: {l['avaliacao']}/5\n"
            f"   Por que combina: {motivos}\n"
        )
    return "\n".join(linhas)


def responder_estruturado(pergunta: str, livros: list[dict], historico: list[str] | None = None,
                          excluir_id: int | None = None, usar_ia: bool = True) -> dict:
    """Decide o tipo de resposta: saudacao | fora_escopo | sem_info | recomendacao."""
    palavras = set(kb.normalizar(pergunta).split())
    if palavras and palavras <= SAUDACOES:
        return _resposta("saudacao", MENSAGEM_SAUDACAO)

    if set(kb.tokenizar(pergunta)) & kb.FORA_DE_ESCOPO and not palavras & PALAVRAS_DE_LIVRO:
        return _resposta("fora_escopo", MENSAGEM_FORA_ESCOPO)

    excluir = {excluir_id} if excluir_id else None
    resultados = kb.buscar(pergunta, livros, top_k=3, excluir_ids=excluir)
    if not resultados and historico:
        # Pedido curto de refinamento ("e mais curto?"): junta com as últimas mensagens.
        resultados = kb.buscar(" ".join(historico[-2:] + [pergunta]), livros, 3, excluir)
    if not resultados:
        return _resposta("sem_info", MENSAGEM_SEM_INFORMACAO)

    texto, modo = None, "local"
    if usar_ia and llm_client.modo_ia_disponivel():
        try:
            texto, modo = llm_client.gerar_resposta_natural(pergunta, resultados), "ia"
        except Exception as erro:
            print(f"[aviso] modo IA falhou ({erro}); usando resposta local.", file=sys.stderr)
    if texto is None:
        n = len(resultados)
        texto = f"Encontrei {n} opç{'ão' if n == 1 else 'ões'} na minha base que combina{'' if n == 1 else 'm'} com o seu pedido:"
    return _resposta("recomendacao", texto, modo, [_serializar(r) for r in resultados])


def responder(pergunta: str, livros: list[dict]) -> str:
    """Versão em texto puro para o terminal."""
    r = responder_estruturado(pergunta, livros)
    if r["tipo"] == "recomendacao" and r["modo"] == "local":
        return formatar_resposta_local(r["livros"])
    return r["texto"]


def main():
    livros = kb.carregar_livros()
    modo = "com IA generativa (Claude)" if llm_client.modo_ia_disponivel() else "local (busca por palavras-chave)"
    print("=" * 60)
    print("LivroCerto — Assistente Virtual de Recomendação de Livros")
    print(f"Modo ativo: {modo}")
    print("=" * 60)
    print("Me conte que tipo de livro você procura. Digite 'sair' para encerrar.\n")
    while True:
        pergunta = input("Você: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("LivroCerto: Até a próxima leitura! 📚")
            break
        print(f"\nLivroCerto: {responder(pergunta, livros)}\n")


if __name__ == "__main__":
    main()
