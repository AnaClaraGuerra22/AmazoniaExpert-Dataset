<div align="center">
  
# SPAmazon-QA

### Benchmarking de LLMs na Amazônia Sustentável com RAG

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)](https://www.trychroma.com/)
[![Modelo](https://img.shields.io/badge/Embeddings-all--mpnet--base--v2-green)](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20130488-blue.svg)](https://doi.org/10.5281/zenodo.20130488)
</div>

---

## Visão Geral

O **SPAmazon-QA** é um repositório estruturado de dados projetado para mitigar alucinações e auditar a precisão factual de Grandes Modelos de Linguagem (LLMs) no domínio da **Amazônia Sustentável**. 

Nascido da necessidade de suprir a escassez de recursos de avaliação focados na região amazônica, o projeto consolida o conhecimento científico dos relatórios oficiais do **Science Panel for the Amazon (SPA)** em dois pilares fundamentais:

1. **Corpus Especializado (Infraestrutura para RAG):** Uma base de dados tratada contendo 6.899 fragmentos de texto (*chunks*) enriquecidos com metadados estruturais, pronta para alimentar arquiteturas de Geração Aumentada por Recuperação (*Retrieval-Augmented Generation*).
2. **Conjunto Curado (Benchmark de Avaliação):** Um referencial rigoroso composto por 130 pares de perguntas e respostas (QA) de diferentes níveis de dificuldade, extraídos diretamente do material do SPA e validados por curadoria humana para testar modelos de IA.

O objetivo central do repositório é fornecer à comunidade científica e desenvolvedores as ferramentas necessárias para criar e testar sistemas de Inteligência Artificial com **rastreabilidade total** e **rigor acadêmico**, garantindo que as informações geradas sobre o bioma sejam ancoradas em fontes de autoridade incontestável.


### Objetivos

| Objetivo | Descrição |
|---|---|
| 🧠 Reduzir alucinações | Respostas ancoradas em corpus científico verificado |
| 🔍 Rastreabilidade | Cada resposta vinculada à fonte original |
| 📊 Avaliação semântica | Métricas quantitativas e qualitativas |
| 🏆 Conjunto Curado | Repositório estruturado com 130 pares QA |

---

## Pipeline Metodológico

<p align="center">
  <img src="assets/conjunto_curado_infografico.jpg" alt="Fluxo Metodológico" width="800"/>
</p>

O pipeline é composto por **6 etapas sequenciais**, desde a curadoria do corpus até a criação do conjunto curado:

1. **Seleção e Curadoria** — 38 documentos científicos, 1.337 páginas do SPA
2. **Extração com Unstructured** — preservação de tabelas, layouts e múltiplas colunas
3. **Limpeza e Chunking** — regex + segmentação semântica em blocos de 500–1.000 caracteres → 6.899 chunks
4. **Enriquecimento com Metadados** — capítulo, seção, página e ID único por chunk
5. **Indexação Vetorial** — embeddings `all-mpnet-base-v2` indexados no ChromaDB
6. **Criação do Conjunto Curado** — 130 pares QA gerados e validados por humanos

---

## Arquitetura RAG (Parâmetros de Inferência)

O pipeline de Recuperação e Geração é configurado para priorizar a precisão científica e o determinismo na busca pelo contexto:

* **Estratégia de Busca:** Recuperação semântica baseada em similaridade do cosseno.
* **Top-K:** `k=5` (os cinco fragmentos mais relevantes são recuperados para formar o contexto).
* **Modelo de Embedding:** `sentence-transformers/all-mpnet-base-v2` (otimizado para textos longos e acadêmicos).
* **Prompting:** Instruções estritas (*Zero-Shot*) bloqueando preâmbulos discursivos e forçando o modelo a ancorar sua resposta exclusivamente no contexto recuperado.
---

## Estrutura do Repositório

```
SPAmazon-QA/
│
├── PAR QA/
│   ├── conjunto_curado.json            # Dataset final de avaliação (130 pares QA)
│   ├── gerar_json.py                   # Script de geração do benchmark
│   └── titulos.txt                     # Metadados auxiliares
│
├── PROMPTS/
│   ├── prompt_geracao_qa.md            # Instruções para geração sintética de Q&A
│   ├── prompt_inferencia.md            # Template para inferência local (GGUF)
│   ├── prompt_inferencia_manual.md     # Template para inferência via interface Web
│   └── prompt_juiz.md                  # Instruções para o Juiz LLM
│
├── RAG/
│   ├── PDFs/                           # Relatórios originais do SPA (PDF)
│   ├── Dados_Limpos/                   # Corpus extraído, tratado e enriquecido (JSON)
│   ├── Dados_Tratados_CC/              # Corpus dos Cross Chapters (JSON)
│   ├── VECTOR_DB/                      # Banco vetorial gerado automaticamente
│   ├── MODELO/                         # Modelos GGUF locais (não versionados)
│   │
│   ├── app.py                          # Interface / execução principal
│   ├── main.py                         # Processa o corpus
│   ├── mainCross.py                    # Execução cross-model
│   ├── vetorizacao.py                  # Banco vetorial gerado automaticamente
│   ├── teste_busca.py                  # Testes de recuperação
│   └── auditoria.py                    # Auditoria das respostas
│
├── assets/
│   ├── fluxograma_datasetdivido.png            # Fluxograma metodológico
│
└── SBBD DSW 2026 - Dataset QA Amazonia.pdf     # Artigo submetido 
│
│
└── README.md
```

---

## Conjunto Curado - Benchmark de Avaliação

**Localização:** `PAR QA/conjunto_curado.json`

### Estrutura de cada entrada

```json
[
  {
    "id_questao": 1,
    "metadados_pergunta": {
      "capitulo_alvo": "Chapter X",
      "dificuldade": "Easy | Medium | Hard",
      "tipo": "Direct | Indirect",
      "modelo_gerador_qa": "Modelo utilizado para geração do QA",
      "indice_subjetividade_textblob": 0.0
    },
    "conjunto_curado": {
      "pergunta": "Pergunta de referência",
      "resposta_esperada": "Resposta científica esperada"
    },
    "avaliacoes_modelos": [
      {
        "modelo_avaliado": "Nome do modelo 1",
        "resposta_gerada": "Resposta produzida pelo modelo",
        "juiz_llm": {
          "nota_likert": 0,
          "justificativa_tecnica": "Análise técnica da resposta"
        }
      }

      {
        "modelo_avaliado": "Nome do modelo 2",
        "resposta_gerada": "Resposta produzida pelo modelo",
        "juiz_llm": {
          "nota_likert": 0,
          "justificativa_tecnica": "Análise técnica da resposta"
        }
      }
      .....

    ]
  }
  {
    "id_questao": 2,
    ......
  }

]

```

### Modelos avaliados

`GPT-4` · `Claude 3.5` · `Gemini 2.5` · `Llama 3` · `ClimateChat`

---



## Modelos Utilizados

Os modelos utilizados no projeto são carregados localmente no formato GGUF via `llama.cpp`.

Devido ao tamanho dos arquivos, os modelos **não são versionados no GitHub**.

### Estrutura esperada

```text
RAG/
├── MODELO/
│   ├── ClimateChat.i1-Q4_K_M.gguf
│   └── Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
```

### Download dos modelos

| Modelo | Link |
|---|---|
| ClimateChat (GGUF) | https://huggingface.co/mradermacher/ClimateChat-i1-GGUF/blob/main/ClimateChat.i1-Q4_K_M.gguf |
| Meta-Llama-3-8B-Instruct (GGUF) | https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/blob/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf |

Após o download, mova os arquivos `.gguf` para:

```text
RAG/MODELO/
```

Os modelos são distribuídos por terceiros via Hugging Face e mantêm suas respectivas licenças originais.
O projeto SPAmazon-QA não redistribui pesos proprietários ou arquivos GGUF.


## Como Usar

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/SPAmazon-QA.git
cd SPAmazon-QA
```

---

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### Dependência adicional para CPU (GGUF / llama.cpp)

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

---

### 3. Configurar ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
UNSTRUCTURED_API_KEY=sua_chave_aqui
```

A chave pode ser obtida em:
https://unstructured.io/

---

### 4. Processar os PDFs científicos

Os PDFs do SPA devem estar em:

```text
RAG/PDFs/
```

Execute:

```bash
python RAG/main.py
```

Isso irá:
- extrair os documentos;
- limpar ruídos;
- gerar chunks semânticos;
- enriquecer metadados;
- salvar os JSONs processados.

---

### 5. Criar a base vetorial (ChromaDB)

```bash
python RAG/vetorizacao.py
```

Isso irá:
- gerar embeddings `all-mpnet-base-v2`;
- indexar os chunks;
- criar a base vetorial persistente em `RAG/VECTOR_DB/`.

---

### 6. Testar recuperação semântica

```bash
python RAG/teste_busca.py
```

---

### 7. Carregar o benchmark

```python
import json

with open('PAR QA/conjunto_curado.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data[0]['conjunto_curado']['pergunta'])
```

---

## Aplicações

- Avaliação de LLMs especializados em domínio científico
- Pesquisa em RAG e recuperação semântica
- Auditoria e rastreabilidade de respostas de IA
- NLP aplicado à Amazônia e sustentabilidade
- Sistemas de QA com contexto científico

---

## Diferenciais

- ✅ Base científica confiável (Science Panel for the Amazon)
- ✅ Corpus estruturado com 130 pares QA validados
- ✅ Avaliação multimodelo (GPT-4, Claude, ClimateChat, Gemini, LLaMA)
- ✅ Métricas quantitativas + qualitativas
- ✅ Pipeline RAG completo e reprodutível
- ✅ Rastreabilidade total até a fonte original

---

## Autoria

**Ana Clara Guerra**
Pesquisa em Inteligência Artificial aplicada à Amazônia Sustentável

---

## Licença

Este projeto está sob a licença [MIT](https://opensource.org/licenses/MIT).

---

## Contribuição

Pull requests são bem-vindos!
Para mudanças maiores, abra uma issue primeiro para discutir o que você gostaria de alterar.
