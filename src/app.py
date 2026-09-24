"""
LivroCerto — Assistente Virtual de Recomendação de Livros.

Aplicação de linha de comando (Passo 4 do desafio). Funciona de duas formas:

1. Modo local (padrão, sempre disponível): busca por palavras-chave na base de
   conhecimento e monta a resposta com um template. Não depende de nenhuma chave
   de API.
2. Modo com IA generativa (opcional): se a variável de ambiente
   ANTHROPIC_API_KEY estiver configurada e a biblioteca 'anthropic' instalada,
   as respostas são reescritas em linguagem mais natural pelo Claude — mas
   sempre com base apenas nos livros que a busca local já filtrou, para evitar
   que o modelo invente recomendações fora da base.

Para executar:
    python src/app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import knowledge_base as kb
import llm_client
from prompts import MENSAGEM_SEM_INFORMACAO

PONTUACAO_MINIMA = 3  # abaixo disso, consideramos que não há um bom match


def formatar_resposta_local(resultados: list[dict]) -> str:
    """Monta uma resposta legível a partir dos resultados da busca, sem usar IA generativa."""
    linhas = ["Encontrei estas opções na minha base de conhecimento:\n"]
    for posicao, item in enumerate(resultados, start=1):
        livro = item["livro"]
        termos = ", ".join(sorted(item["termos_usados"])) or "correspondência geral"
        linhas.append(
            f"{posicao}. {livro['titulo']} — {livro['autor']} ({livro['genero']})\n"
            f"   {livro['sinopse']}\n"
            f"   Tempo de leitura: {livro['tempo_leitura']} | Nível: {livro['nivel']} | "
            f"Avaliação: {livro['avaliacao']}/5\n"
            f"   Por que combina: relacionado a \"{termos}\"\n"
        )
    return "\n".join(linhas)


def responder(pergunta: str, livros: list[dict]) -> str:
    """Gera a resposta do assistente para uma pergunta da pessoa usuária."""
    resultados = kb.buscar(pergunta, livros, top_k=3)

    if not resultados or resultados[0]["pontuacao"] < PONTUACAO_MINIMA:
        # Regra explícita do desafio: dizer quando não há informação suficiente,
        # em vez de forçar uma recomendação de baixa qualidade.
        return MENSAGEM_SEM_INFORMACAO

    if llm_client.modo_ia_disponivel():
        try:
            return llm_client.gerar_resposta_natural(pergunta, resultados)
        except Exception as erro:
            # Se a chamada à IA falhar por qualquer motivo (rede, cota, etc.),
            # o assistente não quebra: cai para a resposta local.
            print(f"[aviso] modo IA generativa falhou ({erro}); usando resposta local.\n")

    return formatar_resposta_local(resultados)


def main():
    livros = kb.carregar_livros()
    modo = "com IA generativa (Claude)" if llm_client.modo_ia_disponivel() else "local (busca por palavras-chave)"

    print("=" * 60)
    print("LivroCerto — Assistente Virtual de Recomendação de Livros")
    print(f"Modo ativo: {modo}")
    print("=" * 60)
    print(
        "Me conte que tipo de livro você procura (gênero, clima, tempo disponível "
        "para ler, etc). Digite 'sair' para encerrar.\n"
    )

    while True:
        pergunta = input("Você: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("LivroCerto: Até a próxima leitura! 📚")
            break

        resposta = responder(pergunta, livros)
        print(f"\nLivroCerto: {resposta}\n")


if __name__ == "__main__":
    main()
