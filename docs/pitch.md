# Pitch — LivroCerto

## O problema
Muita gente quer ler mais, mas trava na hora de escolher o próximo livro.
Listas genéricas de "melhores livros" não consideram o clima ou o momento da
pessoa, e recomendações de amigos nem sempre combinam com o gosto de cada um.

## A solução
O **LivroCerto** é um assistente virtual simples: a pessoa descreve, com suas
próprias palavras, o que procura ("algo leve e emocionante", "suspense com
reviravoltas", "quero entender mais sobre história"), e o assistente responde
com até 3 recomendações da sua base de conhecimento, sempre explicando o
porquê de cada escolha.

## Como funciona (em 30 segundos)
1. A pergunta da pessoa é comparada com o gênero, as tags e a sinopse de cada
   livro da base de conhecimento;
2. Os livros mais relevantes são selecionados;
3. Se não houver um bom match, o assistente admite isso e pede mais detalhes
   em vez de "chutar";
4. Opcionalmente, um modelo de linguagem (Claude) reescreve a resposta de
   forma mais natural — sempre restrito aos livros já filtrados, para nunca
   inventar títulos que não existem na base.

## Por que isso importa
- Mostra, na prática, o princípio central de assistentes de IA responsáveis:
  **responder com base em uma fonte de verdade, e admitir os próprios limites**;
- É facilmente extensível: basta adicionar mais livros a `data/livros.json`
  para o assistente cobrir mais gêneros e temas;
- A separação entre busca (determinística, testável) e geração (opcional,
  natural) é um padrão de arquitetura real usado em produtos de IA sérios
  (RAG — Retrieval-Augmented Generation).

## Próximos passos
- Melhorar a busca com verificação de intenção (a pergunta é mesmo sobre
  livros?), reduzindo falsos positivos como perguntas sobre investimentos;
- Ampliar a base de conhecimento com mais títulos e gêneros;
- Adicionar uma interface web simples além da linha de comando.
