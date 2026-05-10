import os
# from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma

# python -m pip install langchain-chroma
# python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
#PASTA_VECTORDB = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\VECTOR_DB"
#CAMINHO_MODELO = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\MODELO\ClimateChat.i1-Q4_K_M.gguf"


#PASTA_VECTORDB = r"C:\TCCII\VECTOR_DB"
#CAMINHO_MODELO = r"C:\TCCII\MODELO\ClimateChat.i1-Q4_K_M.gguf"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASTA_VECTORDB = os.path.join(BASE_DIR, "VECTOR_DB")
CAMINHO_MODELO = os.path.join(BASE_DIR, "MODELO", "ClimateChat.i1-Q4_K_M.gguf")

if not os.path.exists(CAMINHO_MODELO):
    raise FileNotFoundError(
        f"Modelo não encontrado em: {CAMINHO_MODELO}\n"
        f"Baixe o modelo GGUF e coloque na pasta RAG/MODELO/"
    )


def iniciar_chatbot():
    print("Iniciando o sistema RAG da Amazônia Sustentável...")
    

    print("Conectando ao banco de dados vetorial...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectordb = Chroma(persist_directory=PASTA_VECTORDB, embedding_function=embeddings)
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    print("Carregando o ClimateChat...")
    llm = LlamaCpp(
        model_path=CAMINHO_MODELO,
        temperature=0.1,      # Temperatura baixa (0.1) = Respostas factuais, sem criatividade/alucinação
        max_tokens=1024,      # Tamanho máximo da resposta gerada
        n_ctx=4096,           # Tamanho da "janela de contexto" (espaço para caber os 5 chunks + a pergunta)
        n_gpu_layers=0,       # 0 = Usar apenas CPU (já que é o formato GGUF otimizado)
        verbose=False         # Desliga os logs técnicos do C++ no terminal
    )


    template = """You are a scientific assistant specialized in the sustainable development of the Amazon.
Your task is to answer the user's question based EXCLUSIVELY on the provided context from the Science Panel for the Amazon (SPA) reports.
Do not use outside knowledge. If the answer is not contained in the context, say "I don't know based on the provided documents".

Context extracted from reports:
{context}

Question: {question}

Scientific Answer:"""
    
    prompt_template = PromptTemplate(template=template, input_variables=["context", "question"])

    print("\n\n")
    print("SISTEMA PRONTO! Digite 'sair' para encerrar.")
    print("\n\n")

    while True:
        pergunta = input("\nSua pergunta sobre a Amazônia: ")
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            break
            
        if not pergunta.strip():
            continue

        print("\nBuscando informações nos relatórios...")
        

        docs_recuperados = retriever.invoke(pergunta)
        
        textos_contexto = []
        for i, doc in enumerate(docs_recuperados):
            cap = doc.metadata.get('chapter_number', 'N/A')
            pag = doc.metadata.get('page', 'N/A')
            textos_contexto.append(f"[Trecho {i+1} | Cap {cap} | Pág {pag}]: {doc.page_content}")
            
        contexto_unido = "\n\n".join(textos_contexto)
        
        prompt_final = prompt_template.format(contexto=contexto_unido, question=pergunta)
        
        print("ClimateChat está formulando a resposta...")
        resposta = llm.invoke(prompt_final)
        
        print("\n" + "-"*50)
        print("RESPOSTA:\n" + resposta.strip())
        print("-"*50)
        print("\nFontes utilizadas na resposta:")
        for doc in docs_recuperados:
            print(f"- Capítulo {doc.metadata.get('chapter_number')}, Seção {doc.metadata.get('section_number')}, Página {doc.metadata.get('page')}")

if __name__ == "__main__":
    iniciar_chatbot()