"""
Avaliação do LivroCerto (Passo 5 do desafio).

Roda um conjunto fixo de perguntas de teste contra a base de conhecimento e mede:

- hit@1: a resposta certa (gênero esperado) veio em 1º lugar?
- hit@3: a resposta certa apareceu entre as 3 primeiras?
- taxa de "recusa correta": para perguntas sem gênero esperado (fora de escopo /
  sem sentido), o assistente corretamente disse que não tinha informação suficiente?

Esse script não usa o modo com IA generativa — ele avalia a camada de busca, que é
a parte determinística e testável do assistente.

Para executar:
    python src/avaliar.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as core
import knowledge_base as kb

CASOS_DE_TESTE = [
    {"pergunta": "quero algo de fantasia com magia e aventura", "genero_esperado": "Fantasia"},
    {"pergunta": "livro de terror assustador para ler a noite", "genero_esperado": "Terror"},
    {"pergunta": "preciso de motivacao para minha carreira e negocios", "genero_esperado": "Negocios"},
    {"pergunta": "romance emocionante sobre adolescentes", "genero_esperado": "Romance"},
    {"pergunta": "quero entender a historia da humanidade", "genero_esperado": "Historia"},
    {"pergunta": "suspense psicologico com reviravoltas", "genero_esperado": "Suspense"},
    {"pergunta": "ficcao cientifica com hackers e futuro distopico", "genero_esperado": "Ficcao cientifica"},
    {"pergunta": "quero desenvolver habitos e produtividade", "genero_esperado": "Desenvolvimento pessoal"},
    {"pergunta": "algo de ficção científica com hackers", "genero_esperado": "Ficcao cientifica"},
    {"pergunta": "um clássico romântico leve", "genero_esperado": "Romance"},
    {"pergunta": "algo assustador para ler de madrugada", "genero_esperado": "Terror"},
    {"pergunta": "xkzq blablabla sem sentido nenhum", "genero_esperado": None},
    {"pergunta": "qual o melhor investimento para hoje", "genero_esperado": None},
]


def avaliar():
    livros = kb.carregar_livros()

    total_com_genero = 0
    acertos_top1 = 0
    acertos_top3 = 0

    total_sem_genero = 0
    recusas_corretas = 0

    print("Resultado detalhado por caso de teste:\n")
    for caso in CASOS_DE_TESTE:
        resposta = core.responder_estruturado(caso["pergunta"], livros, usar_ia=False)
        houve_match_relevante = resposta["tipo"] == "recomendacao"
        generos_retornados = [l["genero"] for l in resposta["livros"]]

        if caso["genero_esperado"] is None:
            total_sem_genero += 1
            recusou = not houve_match_relevante
            recusas_corretas += int(recusou)
            status = "OK (recusou corretamente)" if recusou else "FALHOU (deveria ter recusado)"
            print(f"- \"{caso['pergunta']}\" -> {status}")
        else:
            total_com_genero += 1
            top1 = houve_match_relevante and generos_retornados[0] == caso["genero_esperado"]
            top3 = houve_match_relevante and caso["genero_esperado"] in generos_retornados
            acertos_top1 += int(top1)
            acertos_top3 += int(top3)
            status = f"top1={'OK' if top1 else 'nao'} | top3={'OK' if top3 else 'nao'}"
            print(f"- \"{caso['pergunta']}\" (esperado: {caso['genero_esperado']}) -> retornou {generos_retornados} [{status}]")

    print("\nMétricas agregadas:")
    if total_com_genero:
        print(f"  hit@1: {acertos_top1}/{total_com_genero} ({100 * acertos_top1 / total_com_genero:.0f}%)")
        print(f"  hit@3: {acertos_top3}/{total_com_genero} ({100 * acertos_top3 / total_com_genero:.0f}%)")
    if total_sem_genero:
        print(
            f"  recusas corretas (evitar resposta inventada): "
            f"{recusas_corretas}/{total_sem_genero} ({100 * recusas_corretas / total_sem_genero:.0f}%)"
        )


if __name__ == "__main__":
    avaliar()
