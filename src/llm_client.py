"""
Integração opcional com um modelo de linguagem (Anthropic Claude) para deixar as
respostas do LivroCerto mais naturais.

Esse módulo é OPCIONAL: o assistente funciona perfeitamente sem ele, usando apenas
a busca por palavras-chave e respostas em template (veja app.py e knowledge_base.py).
Se a biblioteca 'anthropic' não estiver instalada ou a variável de ambiente
ANTHROPIC_API_KEY não estiver configurada, o app usa automaticamente o modo local.

Isso é intencional: um bom assistente com IA deve funcionar (e deixar claro seus
limites) mesmo quando a parte "generativa" não está disponível.
"""

import os

from prompts import SYSTEM_PROMPT, USER_MESSAGE_TEMPLATE

try:
    import anthropic
except ImportError:
    anthropic = None

# Modelo padrão usado quando o modo com IA generativa está habilitado.
# Pode ser trocado por outro modelo Claude ao qual sua chave de API tenha acesso.
MODELO_PADRAO = os.environ.get("LIVROCERTO_MODELO", "claude-sonnet-5-5")


def modo_ia_disponivel() -> bool:
    """Verifica se dá para usar o modo com IA generativa (biblioteca + chave de API)."""
    return anthropic is not None and bool(os.environ.get("ANTHROPIC_API_KEY"))


def _formatar_contexto(resultados_busca: list[dict]) -> str:
    """Formata os livros recuperados pela busca em texto para enviar ao modelo."""
    blocos = []
    for item in resultados_busca:
        livro = item["livro"]
        blocos.append(
            f"- Título: {livro['titulo']}\n"
            f"  Autor: {livro['autor']}\n"
            f"  Gênero: {livro['genero']}\n"
            f"  Tags: {', '.join(livro['tags'])}\n"
            f"  Sinopse: {livro['sinopse']}\n"
            f"  Tempo de leitura: {livro['tempo_leitura']} | Nível: {livro['nivel']}"
        )
    return "\n\n".join(blocos)


def gerar_resposta_natural(pergunta: str, resultados_busca: list[dict]) -> str:
    """
    Gera uma resposta em linguagem natural usando o Claude, com base SOMENTE nos
    livros já filtrados pela busca local (resultados_busca). O modelo é instruído
    (via SYSTEM_PROMPT) a nunca inventar livros fora dessa lista.

    Levanta RuntimeError se o modo IA não estiver disponível — quem chama essa
    função deve checar modo_ia_disponivel() antes, ou tratar a exceção.
    """
    if not modo_ia_disponivel():
        raise RuntimeError(
            "Modo IA generativa indisponível: instale 'anthropic' e configure "
            "ANTHROPIC_API_KEY para habilitá-lo."
        )

    contexto = _formatar_contexto(resultados_busca)
    mensagem_usuario = USER_MESSAGE_TEMPLATE.format(
        pergunta=pergunta, contexto_livros=contexto
    )

    cliente = anthropic.Anthropic()
    resposta = cliente.messages.create(
        model=MODELO_PADRAO,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": mensagem_usuario}],
    )

    partes_texto = [bloco.text for bloco in resposta.content if bloco.type == "text"]
    return "\n".join(partes_texto).strip()
