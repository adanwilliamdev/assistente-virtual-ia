# Avaliação e Métricas — LivroCerto

## Metodologia
O arquivo `src/avaliar.py` roda 10 perguntas de teste contra a camada de busca
(a parte determinística do assistente) e mede três métricas:

- **hit@1**: o gênero esperado veio como a 1ª recomendação?
- **hit@3**: o gênero esperado apareceu entre as 3 recomendações?
- **recusa correta**: para perguntas sem relação com nenhum livro da base, o
  assistente disse corretamente que não tinha informação suficiente, em vez de
  forçar uma recomendação?

A avaliação foca na busca (não no modo com IA generativa) porque é a parte
testável de forma objetiva e repetível — a qualidade da redação gerada por IA
é mais subjetiva e foi avaliada manualmente lendo algumas respostas de exemplo.

## Casos de teste e resultado (execução real)

| Pergunta | Gênero esperado | Retornado | Resultado |
|---|---|---|---|
| "quero algo de fantasia com magia e aventura" | Fantasia | Fantasia | top1 OK |
| "livro de terror assustador para ler a noite" | Terror | Terror | top1 OK |
| "preciso de motivacao para minha carreira e negocios" | Negócios | Desenvolvimento pessoal, Negócios | top1 não / top3 OK |
| "romance emocionante sobre adolescentes" | Romance | Romance, Romance, Drama | top1 OK |
| "quero entender a historia da humanidade" | História | Biografia, História | top1 não / top3 OK |
| "suspense psicologico com reviravoltas" | Suspense | Suspense | top1 OK |
| "ficcao cientifica com hackers e futuro distopico" | Ficção científica | Ficção científica, Ficção científica, História | top1 OK |
| "quero desenvolver habitos e produtividade" | Desenvolvimento pessoal | Desenvolvimento pessoal | top1 OK |
| "xkzq blablabla sem sentido nenhum" | — (deve recusar) | recusou | correto |
| "qual o melhor investimento para hoje" | — (deve recusar) | Negócios | **falhou** |

## Métricas agregadas
- **hit@1**: 6/8 = **75%**
- **hit@3**: 8/8 = **100%**
- **recusas corretas**: 1/2 = **50%**

## Análise
- A busca acerta bem quando a pergunta usa palavras próximas das tags do livro
  (ex: "fantasia", "aventura", "suspense psicológico").
- Os dois erros de hit@1 (negócios/desenvolvimento pessoal e história/biografia)
  acontecem porque livros de gêneros vizinhos compartilham tags como
  "motivacional" ou "reflexivo" — um problema esperado de uma busca por
  palavras-chave sem entendimento semântico profundo.
- A falha de recusa em "qual o melhor investimento para hoje" mostra um
  limite conhecido do protótipo: a pergunta menciona "investimento", que é uma
  tag do livro *Pai Rico, Pai Pobre*, então a busca encontra uma correspondência
  fraca por palavra-chave mesmo a pergunta não sendo, de fato, um pedido de
  recomendação de livro. Um próximo passo natural seria adicionar uma
  verificação de intenção (a pergunta é sobre livros?) antes da busca.

## Testes manuais do modo conversacional
Além do script automatizado, testei manualmente a aplicação (`src/app.py`)
com perguntas livres (ex: "quero um livro leve de fantasia com aventura") e
confirmei que:
- As justificativas exibidas realmente citam tags/trechos coerentes com a
  pergunta;
- A mensagem de "não tenho informação suficiente" aparece para perguntas vagas
  demais (ex: apenas "me indica algo");
- O app não trava nem gera erro mesmo sem a variável `ANTHROPIC_API_KEY`
  configurada (modo local funciona de forma independente).
