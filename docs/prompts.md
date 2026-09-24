# Prompts do Agente — LivroCerto

Os prompts reais usados pelo código estão em `src/prompts.py` (para ficarem
versionados junto com a aplicação). Este documento explica as decisões por
trás deles.

## System Prompt
Define a identidade do assistente e, principalmente, as **regras anti-alucinação**:
usar somente os livros recebidos no contexto, admitir quando não há bom match,
justificar recomendações e não opinar fora do escopo de livros.

A regra mais importante é a primeira:
> "Use APENAS os livros fornecidos na lista de contexto abaixo. Nunca invente
> títulos, autores, sinopses ou avaliações que não estejam na lista."

Isso é reforçado de duas formas, não só no texto do prompt:
- A busca local (`knowledge_base.py`) já filtra os livros **antes** de qualquer
  chamada de IA — o modelo generativo nunca vê a base inteira, só os 3 livros
  mais relevantes para aquele pedido.
- Se a busca não encontra nada relevante, a IA generativa nem chega a ser
  chamada: a resposta de "sem informação suficiente" é decidida pelo código.

## Template da mensagem do usuário
Combina a pergunta original da pessoa com o contexto dos livros já filtrados
pela busca, deixando explícito no próprio texto que a IA deve usar "SOMENTE
estes" livros. Repetir a restrição no prompt do usuário (além do system prompt)
é uma técnica simples para reduzir a chance de alucinação.

## Por que separar busca (determinística) de geração (IA)?
Essa arquitetura (geralmente chamada de RAG — *Retrieval-Augmented Generation*)
foi escolhida porque:
- A busca é fácil de testar e avaliar com métricas objetivas (ver
  `docs/avaliacao.md`);
- A parte generativa só entra para deixar a redação mais natural, sem poder
  mudar *quais* livros são recomendados;
- O assistente continua funcional mesmo sem chave de API configurada, o que
  facilita testar e revisar o protótipo.

## Mensagem de "não sei"
Ficou centralizada em `MENSAGEM_SEM_INFORMACAO` para que o tom (educado, pede
detalhes específicos: gênero, clima, tempo de leitura) seja consistente e
fácil de revisar, em vez de estar espalhada pelo código.
