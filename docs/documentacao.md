# Documentação do Agente — LivroCerto

## O que ele faz
O **LivroCerto** é um assistente virtual que ajuda uma pessoa indecisa a escolher
o próximo livro para ler. A pessoa descreve o que procura em linguagem natural
(gênero, clima, tempo disponível, nível de leitura) e o assistente sugere até
3 livros da sua base de conhecimento, explicando por que cada um combina com o
pedido.

## Para quem ele serve
Leitores que:
- Não sabem o que ler a seguir e querem sugestões rápidas;
- Preferem descrever um "clima" (ex: "algo leve e emocionante") em vez de já
  saber o título exato;
- Querem entender *por que* um livro foi recomendado, não só receber uma lista.

## Como ele deve se comportar
1. **Nunca inventa livros.** Toda recomendação vem da base de conhecimento em
   `data/livros.json`. Isso vale tanto no modo local (busca por palavras-chave)
   quanto no modo opcional com IA generativa, que recebe instrução explícita
   (no `SYSTEM_PROMPT`) para não extrapolar a lista fornecida.
2. **Admite quando não sabe.** Se a busca não encontra um livro com relevância
   mínima para o pedido, o assistente diz isso claramente e pede mais detalhes,
   em vez de forçar uma recomendação de baixa qualidade.
3. **Justifica cada recomendação**, citando o gênero, as tags ou trechos da
   sinopse que motivaram a escolha — isso ajuda a pessoa a confiar (ou não) na
   sugestão e a refinar o pedido se quiser.
4. **Fica no seu escopo.** O assistente só recomenda livros; não dá conselhos
   médicos, financeiros ou jurídicos, mesmo que os livros da base toquem nesses
   temas (ex: um livro sobre investimentos).
5. **Funciona mesmo sem IA generativa configurada**, usando busca por
   palavras-chave e respostas em template — a "camada de IA" (Claude) é uma
   melhoria opcional de linguagem natural, não uma dependência obrigatória.

## Fora de escopo (por design)
- Comprar ou indicar onde comprar os livros;
- Resumir o final dos livros (spoilers);
- Dar opiniões pessoais sobre qualidade literária além do que está na base.
