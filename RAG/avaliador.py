import os
import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Configurar o Juiz (Google Gemini API)
# COLOQUE A SUA CHAVE AQUI DENTRO DAS ASPAS


# python -m pip install google-generativeai pandas
# python -m pip install python-dotenv

load_dotenv()
chave_gemini = os.getenv("GEMINI_API_KEY")  

genai.configure(api_key=chave_gemini)
juiz_llm = genai.GenerativeModel('gemini-1.5-flash')

# Caminho para as pastas onde você salvou os TXTs das IAs
PASTA_QA = r"C:\TCCII\PARES QA"

def extrair_qa_do_txt(caminho_arquivo):
    """Lê o arquivo TXT e usa Regex para separar as perguntas, respostas e classificações."""
    pares = []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    

    blocos = re.split(r'Pair \d+', conteudo)
    
    for bloco in blocos[1:]: 
        try:
            pergunta = re.search(r'Question \d+:\s*(.*?)\s*Answer \d+:', bloco, re.DOTALL).group(1).strip()
            resposta_gabarito = re.search(r'Answer \d+:\s*(.*?)\s*Difficulty:', bloco, re.DOTALL).group(1).strip()
            dificuldade = re.search(r'Difficulty:\s*(.*?)\s*Classification:', bloco, re.DOTALL).group(1).strip()
            classificacao = re.search(r'Classification:\s*(.*)', bloco, re.DOTALL).group(1).strip()
            
            pares.append({
                "Pergunta": pergunta,
                "Gabarito": resposta_gabarito,
                "Dificuldade": dificuldade,
                "Classificacao": classificacao
            })
        except AttributeError:
            continue # Pula se o bloco estiver mal formatado
            
    return pares

def avaliar_com_juiz_ia(pergunta, gabarito, resposta_gerada):
    """Envia os dados para a API do Gemini atuar como juiz rigoroso."""
    prompt_juiz = f"""
    You are an expert evaluator grading an AI assistant's answers.
    You will be given a Question, a Ground Truth Reference Answer, and the Generated Answer by the AI.
    
    Your task is to grade the Generated Answer from 0 to 5 based on Factuality and Relevance to the Ground Truth.
    0 = Completely wrong, hallucinated, or irrelevant.
    5 = Perfect match in meaning and facts (even if using different words).
    
    Question: {pergunta}
    Ground Truth: {gabarito}
    Generated Answer: {resposta_gerada}
    
    Provide your evaluation in the following strict format:
    Score: [0-5]
    Justification: [Brief explanation of the score]
    """
    
    try:
        resposta_juiz = juiz_llm.generate_content(prompt_juiz)
        texto = resposta_juiz.text
        nota = re.search(r'Score:\s*(\d+)', texto).group(1)
        justificativa = re.search(r'Justification:\s*(.*)', texto, re.DOTALL).group(1).strip()
        return int(nota), justificativa
    except Exception as e:
        return 0, f"Erro na avaliação da API: {e}"

def iniciar_auditoria():
    print("Iniciando auditoria automatizada do RAG...")
    
    # Importar a função do seu app.py (certifique-se de que o app.py está na mesma pasta)
    from app import gerar_resposta_rag
    
    resultados_finais = []
    
    # 2. Varrer todas as pastas de QA (Claude, Gemini, GPT)
    for pasta_ia in os.listdir(PASTA_QA):
        caminho_pasta = os.path.join(PASTA_QA, pasta_ia)
        if not os.path.isdir(caminho_pasta): continue
            
        for arquivo_txt in os.listdir(caminho_pasta):
            if not arquivo_txt.endswith('.txt'): continue
                
            caminho_txt = os.path.join(caminho_pasta, arquivo_txt)
            print(f"\nProcessando arquivo: {arquivo_txt} (Origem: {pasta_ia})")
            
            # Extrair os dados do arquivo
            pares_qa = extrair_qa_do_txt(caminho_txt)
            
            # Aqui você pode colocar um limite (ex: avaliar apenas os 2 primeiros pares de cada TXT para teste)
            for par in pares_qa[:2]: 
                pergunta = par['Pergunta']
                print(f"Testando: {pergunta[:50]}...")
                
                # A. Pede para o seu RAG local responder
                resposta_gerada, fontes_citadas = gerar_resposta_rag(pergunta)
                
                # B. Pede para o Juiz na nuvem avaliar
                nota, justificativa = avaliar_com_juiz_ia(pergunta, par['Gabarito'], resposta_gerada)
                
                # C. Salva o resultado
                resultados_finais.append({
                    "Origem": pasta_ia,
                    "Arquivo": arquivo_txt,
                    "Classificacao": par['Classificacao'],
                    "Dificuldade": par['Dificuldade'],
                    "Pergunta": pergunta,
                    "Gabarito": par['Gabarito'],
                    "Resposta_Gerada": resposta_gerada,
                    "Fontes_Recuperadas": fontes_citadas,
                    "Nota_0_a_5": nota,
                    "Justificativa_Juiz": justificativa
                })
                
    # 3. Exportar para CSV
    df = pd.DataFrame(resultados_finais)
    caminho_csv = r"C:\TCCII\Resultados_Auditoria_RAG.csv"
    df.to_csv(caminho_csv, index=False, encoding='utf-8')
    print(f"\nAuditoria concluída! Resultados salvos em: {caminho_csv}")

if __name__ == "__main__":
    iniciar_auditoria()