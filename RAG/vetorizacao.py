import os
import json
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

# pip install llama-cpp-python langchain langchain-community
# pip install huggingface_hub

# python -m pip install langchain-chroma

# python -m pip install langchain langchain-core langchain-community langchain-huggingface sentence-transformers chromadb


PASTA_JSON = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Limpos"
PASTA_JSON_CC = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Tratados_CC"
#PASTA_VECTORDB = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\VECTOR_DB"


# PASTA_JSON = r"C:\TCCII\UNSTRUCTURED\Dados_Limpos"
#PASTA_JSON_CC = r"C:\TCCII\UNSTRUCTURED\Dados_Tratados_CC"
PASTA_VECTORDB = r"C:\TCCII\VECTOR_DB"

def criar_base_vetorial():

    os.makedirs(PASTA_VECTORDB, exist_ok=True)
    
    # modelo de embeddings (all-mpnet-base-v2)
    print("Carregando o modelo de embeddings (all-mpnet-base-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    
    caminhos_arquivos = []
    
    if os.path.exists(PASTA_JSON):
        for f in os.listdir(PASTA_JSON):
            if f.lower().endswith('.json') and "cross chapter" not in f.lower():
                caminhos_arquivos.append(os.path.join(PASTA_JSON, f))
                
    # cross chapters
    if os.path.exists(PASTA_JSON_CC):
        for f in os.listdir(PASTA_JSON_CC):
            if f.lower().endswith('.json'):
                caminhos_arquivos.append(os.path.join(PASTA_JSON_CC, f))
    
    print(f"Processando {len(caminhos_arquivos)} ficheiros JSON...")
    
    documentos = []


    for caminho_completo in caminhos_arquivos:
        nome_arquivo = os.path.basename(caminho_completo)
        
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            try:
                chunks = json.load(f)
            except Exception as e:
                print(f"Erro ao ler {nome_arquivo}: {e}")
                continue
            
            for c in chunks:
                texto_base = c.get("text", "")
                meta = c.get("metadata", {})
                
                if not texto_base:
                    continue
                    
                cap_nome = meta.get("chapter_name", "Unknown Chapter")
                sec_num = meta.get("parent_section_number", "")
                sec_nome = meta.get("parent_section_name", "")
                

                label_secao = sec_nome if sec_nome else "Content"
                
                texto_enriquecido = f"Chapter: {cap_nome}\nSection {sec_num}: {label_secao}\nContent: {texto_base}"
                
                metadados_limpos = {
                    "source": str(meta.get("source", nome_arquivo)),
                    "chapter_number": str(meta.get("chapter_number", "N/A")),
                    "section_number": str(sec_num),
                    "page": int(meta.get("page", 0))
                }
                
                doc = Document(page_content=texto_enriquecido, metadata=metadados_limpos)
                documentos.append(doc)
                
    print(f"\nTotal de fragmentos prontos: {len(documentos)}\n")
    

    print("\nGerando vetores e populando o banco de dados...")
    print("(Isso pode levar alguns minutos dependendo da sua CPU)")
    
    Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=PASTA_VECTORDB
    )
    
    print(f"\nBanco de vetores atualizado em: {PASTA_VECTORDB}")
    print("Agora os metadados estão sincronizados com os seus ficheiros JSON.")

if __name__ == "__main__":
    criar_base_vetorial()