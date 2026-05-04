#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings




# python -m pip install langchain-chroma
PASTA_VECTORDB = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\VECTOR_DB"

def testar_banco():
    print("Conectando ao banco de vetores...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectordb = Chroma(persist_directory=PASTA_VECTORDB, embedding_function=embeddings)
    
    # qtd chunks 
    total_docs = vectordb._collection.count()
    print(f"Total de fragmentos no banco: {total_docs}\n")
    
    # teste busca semantica
    pergunta_teste = "What are the main sustainable development policies to prevent deforestation in the Amazon?"
    print(f"Pergunta de teste: '{pergunta_teste}'\n")
    
    # Traz os 3 fragmentos mais matematicamente próximos da pergunta
    documentos_recuperados = vectordb.similarity_search(pergunta_teste, k=3)
    
    for i, doc in enumerate(documentos_recuperados):
        print(f"========== RESULTADO {i+1} ==========")
        # Imprime os metadados para você ver se a extração funcionou
        print(f"Arquivo de Origem: {doc.metadata.get('source')}")
        print(f"Capítulo: {doc.metadata.get('chapter_number')} | Seção: {doc.metadata.get('section_number')} | Página: {doc.metadata.get('page')}")
        
        # Imprime os primeiros 300 caracteres do texto para checar a coerência
        print(f"Trecho Recuperado:\n{doc.page_content[:300]}...\n")

if __name__ == "__main__":
    testar_banco()