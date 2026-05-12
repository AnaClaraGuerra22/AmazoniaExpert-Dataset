# Prompt de Geração Sintética (Q&A)

Este *prompt* foi utilizado para orientar os modelos de linguagem na extração de conhecimento e formulação do conjunto de avaliação especializado na sustentabilidade do bioma amazônico.

## Instrução Base
Estou criando um LLM que será especializado em Amazônia Sustentável. Para testar se ele não alucina, preciso selecionar pares de perguntas e respostas de cada artigo que mandei para ele (Em inglês). Me ajude a fazer isso, mandei 38 artigos para ele.

## Regras de Geração
Regras para a criação dos pares de perguntas e respostas:

1. **Densidade:** Formular pelo menos 1 par de pergunta e resposta a cada 3 páginas do artigo.
2. **Idioma:** O conteúdo deve ser gerado estritamente em inglês.
3. **Autossuficiência:** Não citar o documento fonte nas perguntas (ex: não usar termos como *"according to the article"*).
4. **Dificuldade:** Classificar esses pares em níveis de dificuldade.
5. **Tipologia da Questão:** Classificar esses pares em **'direto'** ou **'indireto'**:
   * **Direto:** A resposta está explicitamente pronta em um trecho do artigo[cite: 9].
   * **Indireto:** A resposta exige a consolidação de um conjunto de partes do artigo, não estando pronta em um único local e demandando interpretação de contexto[cite: 9].
6. **Proporção:** Gerar pelo menos 2 pares 'direto' e 2 pares 'indireto' em cada artigo processado.

## Estrutura de Saída (Formato Esperado)
Estrutura que você irá mandar:

"Pair" x 
"Question" x:
...........?
"Answer" x:
........................
"Difficulty:"
...........
"Classification:"
"Direct" ou "Indirect"

"Pair" x+1
"Question" x+1:
...........?
"Answer" x+1:
........................
"Difficulty:"
...........
"Classification:"
"Direct" ou "Indirect"