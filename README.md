<div align="center">

# 🌿 SPAmazon-QA

### Benchmarking de LLMs na Amazônia Sustentável com RAG

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)](https://www.trychroma.com/)
[![Modelo](https://img.shields.io/badge/Embeddings-all--mpnet--base--v2-green)](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)

</div>

---

## Visão Geral

O **SPAmazon-QA** é um benchmark científico desenvolvido para avaliar modelos de linguagem (LLMs) no domínio da **Amazônia Sustentável**, utilizando uma arquitetura baseada em **RAG (*Retrieval-Augmented Generation*)**.

A base de conhecimento é fundamentada nos relatórios do **Science Panel for the Amazon (SPA)** — a única fonte de autoridade científica do projeto.

### Objetivos

| Objetivo | Descrição |
|---|---|
| 🧠 Reduzir alucinações | Respostas ancoradas em corpus científico verificado |
| 🔍 Rastreabilidade | Cada resposta vinculada à fonte original |
| 📊 Avaliação semântica | Métricas quantitativas e qualitativas |
| 🏆 Padrão-ouro | Benchmark estruturado com 130 pares QA |

---

## Pipeline Metodológico

<p align="center">
  <img src="assets/fluxograma_datasetdivido.png" alt="Fluxo Metodológico" width="800"/>
</p>

O pipeline é composto por **6 etapas sequenciais**, desde a curadoria do corpus até a criação do padrão-ouro:

1. **Seleção e Curadoria** — 38 documentos científicos, 1.337 páginas do SPA
2. **Extração com Unstructured** — preservação de tabelas, layouts e múltiplas colunas
3. **Limpeza e Chunking** — regex + segmentação semântica em blocos de 500–1.000 caracteres → 6.899 chunks
4. **Enriquecimento com Metadados** — capítulo, seção, página e ID único por chunk
5. **Indexação Vetorial** — embeddings `all-mpnet-base-v2` indexados no ChromaDB
6. **Criação do Padrão-Ouro** — 130 pares QA gerados e validados por humanos

---

## Arquitetura RAG

<p align="center">
  <img src="assets/RAG_climate.png" alt="Fluxo RAG" width="650"/>
</p>

---

## Estrutura do Repositório

```
SPAmazon-QA/
│
├── PAR QA/
│   ├── gold_standard_amazonia.json   # Dataset padrão-ouro (130 pares QA)
│   ├── gerar_json.py                 # Script de geração do benchmark
│   └── titulos.txt                   # Metadados auxiliares
│
├── RAG/
│   ├── Dados_Limpos/                 # Corpus extraído, tratado e enriquecido (JSON)
│   ├── Dados_Tratados_CC/            # Corpus dos Cross Chapters (JSON)
│   │
│   ├── app.py                        # Interface / execução principal
│   ├── main.py                       # Pipeline principal RAG
│   ├── mainCross.py                  # Execução cross-model
│   ├── vetorizacao.py                # Indexação vetorial (ChromaDB)
│   ├── teste_busca.py                # Testes de recuperação
│   └── auditoria.py                  # Auditoria das respostas
│
├── assets/
│   ├── fluxograma_datasetdivido.png  # Fluxograma metodológico
│   └── RAG_climate.png               # Arquitetura RAG
│
└── README.md
```

---

## Benchmark — Gold Standard

**Localização:** `PAR QA/gold_standard_amazonia.json`

### Estrutura de cada entrada

```json
{
  "metadados_pergunta": {
    "dificuldade": "Easy | Medium | Hard",
    "tipo": "Direct | Indirect",
    "capitulo_spa": "...",
    "indice_subjetividade": 0.0
  },
  "padrao_ouro": {
    "pergunta": "...",
    "resposta_esperada": "..."
  },
  "avaliacoes_modelos": {
    "GPT-4": "...",
    "Claude 3.5": "...",
    "Gemini 2.5": "...",
    "LLaMA 3": "...",
    "AmazoniaExpert": "..."
  },
  "similaridade_faiss_percentual": {
    "similaridade_cosseno": 0.0,
    "diagnostico": "..."
  }
}
```

### Modelos avaliados

`GPT-4` · `Claude 3.5` · `Gemini 2.5` · `LLaMA 3` · `AmazoniaExpert`

---

## Como Usar

### 1. Carregar o benchmark

```python
import json

with open('PAR QA/gold_standard_amazonia.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data[0]['padrao_ouro']['pergunta'])
```

### 2. Executar o pipeline RAG

```bash
python RAG/main.py
```

### 3. Testar recuperação semântica

```bash
python RAG/teste_busca.py
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
- ✅ Benchmark estruturado com 130 pares QA validados
- ✅ Avaliação multimodelo (GPT-4, Claude, Gemini, LLaMA)
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