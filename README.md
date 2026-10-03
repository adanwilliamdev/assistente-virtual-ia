# LivroCerto — Assistente Virtual de Recomendação de Livros

Projeto criado para o Lab **"Construa Seu Assistente Virtual Com Inteligência
Artificial"**. Um assistente conversacional simples que ajuda uma pessoa
indecisa a escolher o próximo livro para ler, com base em uma base de
conhecimento própria e sem inventar recomendações fora dela.

## Estrutura do projeto
```
assistente-virtual-ia/
  README.md
  requirements.txt
  data/
    livros.json          # base de conhecimento (Passo 2)
  docs/
    documentacao.md       # Passo 1 — objetivo, público e comportamento
    prompts.md             # Passo 3 — explicação dos prompts
    avaliacao.md            # Passo 5 — metodologia e métricas
    pitch.md                  # Passo 6 — pitch do projeto
  web/
    index.html            # frontend (chat + catálogo)
  src/
    server.py               # servidor web + API JSON (sem dependências)
    knowledge_base.py     # carregamento e busca na base (Passo 2)
    prompts.py             # prompts usados pelo agente (Passo 3)
    llm_client.py            # integração opcional com Claude
    app.py                     # aplicação de linha de comando (Passo 4)
    avaliar.py                  # script de avaliação com métricas (Passo 5)
```

## Interface web (recomendado)
```bash
python src/server.py        # abra http://127.0.0.1:8000
```
Tem chat com cartões de livros, sugestões rápidas, botão "Quero algo parecido",
aba de catálogo com filtros por gênero/nível, tema claro/escuro e layout
responsivo. Variáveis opcionais: `PORT`, `HOST`, `LIVROCERTO_MODELO`.

## Como executar no terminal

Requer Python 3.10+ (usa `list[dict]` e `tuple[...]` na assinatura de funções).

```bash
cd assistente-virtual-ia
python src/app.py
```

Exemplo de conversa:
```
Você: quero um livro leve de fantasia com aventura
LivroCerto: Encontrei estas opções na minha base de conhecimento:

1. O Hobbit — J.R.R. Tolkien (Fantasia)
   Bilbo Bolseiro, um hobbit pacato, é arrastado para uma jornada inesperada...
   Por que combina: relacionado a "aventura, fantasia, leve"
...
```

Para encerrar, digite `sair`.

## Modo opcional com IA generativa
Por padrão, o assistente responde usando busca por palavras-chave + templates
(funciona 100% offline, sem chave de API). Para habilitar respostas mais
naturais geradas por um modelo Claude:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua_chave_aqui"
python src/app.py
```

Mesmo nesse modo, o modelo só recebe os livros que a busca local já filtrou —
ele nunca vê a base inteira e é instruído a não recomendar nada fora dela
(veja `docs/prompts.md`).

## O que melhorou nesta versão
- Busca ignora acentos e plural, entende sinônimos ("assustador" → terror) e
  considera nível ("iniciante") e tamanho ("curto") do pedido.
- Recusa pedidos fora de escopo (ex.: investimentos) e trata saudações.
- Refinamentos curtos usam o contexto das últimas mensagens.
- Modelo Claude configurável por `LIVROCERTO_MODELO` (padrão `claude-sonnet-5-5`).
- Avaliação (`python src/avaliar.py`): hit@1 75% → 82%, recusas corretas 50% → 100%,
  com 3 casos de teste novos mais difíceis.

## Como avaliar
```bash
python src/avaliar.py
```
Roda 10 perguntas de teste e imprime métricas de acerto (hit@1, hit@3) e de
recusa correta quando não há informação suficiente. Os resultados de uma
execução real estão documentados em `docs/avaliacao.md`.

## Os 6 passos do desafio, e onde encontrar cada um
| Passo | Onde está |
|---|---|
| 1. Documentação | `docs/documentacao.md` |
| 2. Base de conhecimento | `data/livros.json` + `src/knowledge_base.py` |
| 3. Prompts | `src/prompts.py` + `docs/prompts.md` |
| 4. Aplicação funcional | `src/app.py` |
| 5. Avaliação e métricas | `src/avaliar.py` + `docs/avaliacao.md` |
| 6. Pitch | `docs/pitch.md` |
