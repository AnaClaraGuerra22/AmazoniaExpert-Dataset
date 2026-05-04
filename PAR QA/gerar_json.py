import pandas as pd
import json
import re
import os
import math
import unicodedata

# Função para normalizar strings (remove acentos, espaços extras e deixa minúsculo)
def normalizar_chave(texto):
    if not isinstance(texto, str):
        return ""
    # Remove acentos
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    # Remove espaços múltiplos e deixa em minúsculo
    return re.sub(r'\s+', ' ', texto_sem_acento.strip().lower())

# ==========================================
# 1. MAPEAMENTO DE CAPÍTULOS
# ==========================================
MAPEAMENTO_BRUTO = {
    "Capítulo 1": "Chapter 1: Geology and Geodiversity of the Amazon: Three Billion Years of History",
    "Capítulo 2": "Chapter 2: Evolution of Amazonian Biodiversity",
    "Capítulo 3": "Chapter 3: Biological Diversity and Ecological Networks in the Amazon",
    "Capítulo 4": "Chapter 4: Amazonian Ecosystems and Their Ecological Functions",
    "Capítulo 5": "Chapter 5: The Physical Hydroclimate System of the Amazon",
    "Capítulo 6": "Chapter 6: Biogeochemical Cycles in the Amazon",
    "Capítulo 7": "Chapter 7: Biogeophysical Cycles: Water Recycling, Climate Regulation",
    "Capítulo 8": "Chapter 8: Peoples of the Amazon Before European Colonization",
    "Capítulo 9": "Chapter 9: Peoples of the Amazon and European Colonization (16th-18th Centuries)",
    "Capítulo 10": "Chapter 10: Critical Interconnections Between the Cultural and Biological Diversity of Amazonian Peoples and Ecosystems",
    "Capítulo 11": "Chapter 11: Economic Drivers in the Amazon from the 19th Century to the 1970s",
    "Capítulo 12": "Chapter 12: Languages of the Amazon: Dimensions of Diversity",
    "Capítulo 13": "Chapter 13: African Presence in the Amazon: A Glance",
    "Capítulo 14": "Chapter 14: Amazon in Motion: Changing Politics, Development Strategies, Peoples, Landscapes, and Livelihoods",
    "Capítulo 15": "Chapter 15: Complex, Diverse, and Changing Agribusiness and Livelihood Systems in the Amazon",
    "Capítulo 16": "Chapter 16: The State of Conservation Policies, Protected Areas, and Indigenous Territories, from the Past to the Present",
    "Capítulo 17": "Chapter 17: Globalization, Extractivism, and Social Exclusion: Threats and Opportunities to Amazon Governance in Brazil",
    "Capítulo 18": "Chapter 18: Globalization, Extractivism, and Social Exclusion: Country-Specific Manifestations",
    "Capítulo 19": "Chapter 19: Drivers and Ecological Impacts of Deforestation and Forest Degradation",
    "Capítulo 20": "Chapter 20: Drivers and Impacts of Changes in Aquatic Ecosystems",
    "Capítulo 21": "Chapter 21: Human Well-Being and Health Impacts of the Degradation of Terrestrial and Aquatic Ecosystems",
    "Capítulo 22": "Chapter 22: Long-Term Variability, Extremes, and Changes in Temperature and Hydro Meteorology",
    "Capítulo 23": "Chapter 23: Impacts of Deforestation and Climate Change on Biodiversity, Ecological Processes, and Environmental Adaptation",
    "Capítulo 24": "Chapter 24: Resilience of the Amazon Forest to Global Changes: Assessing the Risk of Tipping Points",
    "Capítulo 25": "Chapter 25: A Pan-Amazonian sustainable development vision",
    "Capítulo 26": "Chapter 26: Sustainable Development Goals (SDGs) and the Amazon",
    "Capítulo 27": "Chapter 27: Conservation measures to counter the main threats to Amazonian biodiversity",
    "Capítulo 28": "Chapter 28: Restoration options for the Amazon",
    "Capítulo 29": "Chapter 29: Restoration priorities and benefits within landscapes and catchments and across the Amazon Basin",
    "Capítulo 30": "Chapter 30: Opportunities and challenges for a healthy standing forest and flowing rivers bioeconomy in the Amazon",
    "Capítulo 31": "Chapter 31: Strengthening land and natural resource governance and management: Protected areas, Indigenous lands, and local communities’ territories",
    "Capítulo 32": "Chapter 32: Milestones and challenges in the construction and expansion of participatory intercultural education in the Amazon",
    "Capítulo 33": "Chapter 33: Connecting and sharing diverse knowledges to support sustainable pathways in the Amazon",
    "Capítulo 34": "Chapter 34: Boosting relations between the Amazon forest and its globalizing cities",
    
    # Tratamento para Cross Chapters e Anexos
    "Capítulo Cross Chapter 1": "Cross Chapter 1: The Amazon Carbon Budget",
    "Cross Chapter 1": "Cross Chapter 1: The Amazon Carbon Budget",
    "Capítulo Cross Chapter 2": "Cross Chapter 2: Legacy from the Ancestors: Amazonian Biocultural Landscapes and Global Sustainability in a Post-COVID-19 World",
    "Cross Chapter 2": "Cross Chapter 2: Legacy from the Ancestors: Amazonian Biocultural Landscapes and Global Sustainability in a Post-COVID-19 World",
    "Capítulo Annex 1": "Annex I: The Multiple Viewpoints for the Amazon: Geographic Limits and Meaning",
    "Annex 1": "Annex I: The Multiple Viewpoints for the Amazon: Geographic Limits and Meaning",
    "Capítulo Annex 2": "Annex II: Definition of Indigenous peoples and local communities (IPLCs)",
    "Annex 2": "Annex II: Definition of Indigenous peoples and local communities (IPLCs)"
}

# Cria o dicionário final blindado usando as chaves normalizadas
MAPEAMENTO_CAPITULOS = {normalizar_chave(k): v for k, v in MAPEAMENTO_BRUTO.items()}

# ==========================================
# 2. DEFINIÇÃO DE CAMINHOS
# ==========================================
pasta_saida = r"C:\TCCII\DSW\PAR QA"
arquivo_saida = os.path.join(pasta_saida, "gold_standard_amazonia.json")

cam_txt = r"C:\TCCII\BD e Questoes\Caderno_Questoes_Final.txt"
cam_respostas = r"C:\TCCII\RESULTADOS\Super_Planilha_Respostas_1_130.xlsx"
cam_notas = r"C:\TCCII\RESULTADOS\Super_Planilha_Notas_1_130.xlsx"
cam_faiss = r"C:\TCCII\RESULTADOS\Auditoria_FAISS_Completa_1_130.xlsx"
cam_subj = r"C:\TCCII\RESULTADOS\Subjetividade_Completa_1_130.xlsx"
cam_climate = r"C:\TCCII\Inferencia IA\Resultados_Finais_Com_Juiz.csv"

# ==========================================
# 3. CARREGAMENTO DOS DADOS (PLANILHAS)
# ==========================================
print("Carregando planilhas e resultados...")
df_resp = pd.read_excel(cam_respostas)
df_notas = pd.read_excel(cam_notas)
df_faiss = pd.read_excel(cam_faiss)
df_subj = pd.read_excel(cam_subj)
df_climate = pd.read_csv(cam_climate) 

print("Corrigindo falha nas respostas do ClimateChat (IDs 1 a 60)...")
for index, row in df_climate.iterrows():
    id_q = int(row['ID_Questao'])
    if id_q <= 60:
        df_resp.loc[df_resp['ID_Questao'] == id_q, 'CLIMATECHAT'] = row['Resposta_ClimateChat']

def float_limpo(valor):
    try:
        f_val = float(valor)
        if math.isnan(f_val):
            return 0.0
        return f_val
    except:
        return 0.0

# ==========================================
# 4. EXTRAÇÃO DO ARQUIVO TXT VIA REGEX
# ==========================================
print("Analisando e extraindo dados do Caderno de Questões (TXT)...")
with open(cam_txt, 'r', encoding='utf-8') as f:
    conteudo_txt = f.read()

blocos_questoes = conteudo_txt.split("QUESTÃO ")[1:]

dataset_final = []

for bloco in blocos_questoes:
    try:
        id_match = re.match(r'(\d+)', bloco)
        if not id_match:
            continue
        id_questao = int(id_match.group(1))
        
        modelo_gerador = re.search(r'Modelo de IA Gerador\s*:\s*(.+)', bloco).group(1).strip()
        capitulo_extraido = re.search(r'Capítulo de Origem\s*:\s*(.+)', bloco).group(1).strip()
        dificuldade = re.search(r'Dificuldade\s*:\s*(.+)', bloco).group(1).strip()
        tipo = re.search(r'Classificação\s*:\s*(.+)', bloco).group(1).strip()
        
        # AQUI OCORRE A MÁGICA DA NORMALIZAÇÃO
        chave_normalizada = normalizar_chave(capitulo_extraido)
        capitulo_completo = MAPEAMENTO_CAPITULOS.get(chave_normalizada, capitulo_extraido) # Se por um acaso extremo não achar, mantém o original
        
        pergunta = re.search(r'\[PERGUNTA\]\n(.*?)(?=\n\n\[GABARITO\])', bloco, re.DOTALL).group(1).strip()
        gabarito = re.search(r'\[GABARITO\]\n(.*?)(?=\n-{10,}|\Z)', bloco, re.DOTALL).group(1).strip()
        
        linha_subj = df_subj[df_subj['ID_Questao'] == id_questao]
        indice_subjetividade = float_limpo(linha_subj.iloc[0]['Nota_Subjetividade']) if not linha_subj.empty else 0.0
        
        documento = {
            "id_questao": id_questao,
            "metadados_pergunta": {
                "capitulo_alvo": capitulo_completo,
                "dificuldade": dificuldade,
                "tipo": tipo,
                "modelo_gerador_qa": modelo_gerador,
                "indice_subjetividade_textblob": indice_subjetividade
            },
            "padrao_ouro": {
                "pergunta": pergunta,
                "resposta_esperada": gabarito
            },
            "avaliacoes_modelos": []
        }
        
        row_resp = df_resp[df_resp['ID_Questao'] == id_questao]
        row_notas = df_notas[df_notas['ID_Questao'] == id_questao]
        row_faiss = df_faiss[df_faiss['ID_Questao'] == id_questao]
        
        if not row_resp.empty and not row_notas.empty and not row_faiss.empty:
            row_resp = row_resp.iloc[0]
            row_notas = row_notas.iloc[0]
            row_faiss = row_faiss.iloc[0]
            
            modelos_auditados = [
                {"nome": "AmazoniaExpert.IA", "col_resp": "AMAZONIAEXPERT", "col_nota": "Nota_AMAZONIAEXPERT", "col_justificativa": "Justificativa_AMAZONIAEXPERT"},
                {"nome": "ClimateChat Puro", "col_resp": "CLIMATECHAT", "col_nota": "Nota_CLIMATECHAT", "col_justificativa": "Justificativa_CLIMATECHAT"},
                {"nome": "LLaMA 3.3", "col_resp": "LLHAMA", "col_nota": "Nota_LLHAMA", "col_justificativa": "Justificativa_LLHAMA"},
                {"nome": "GPT-4", "col_resp": "GPT", "col_nota": "Nota_GPT", "col_justificativa": "Justificativa_GPT"},
                {"nome": "Claude 3.5 Sonnet", "col_resp": "CLAUDE", "col_nota": "Nota_CLAUDE", "col_justificativa": "Justificativa_CLAUDE"},
                {"nome": "Gemini 2.5 Pro", "col_resp": "GEMINI", "col_nota": "Nota_GEMINI", "col_justificativa": "Justificativa_GEMINI"}
            ]
            
            for modelo in modelos_auditados:
                avaliacao = {
                    "modelo_avaliado": modelo["nome"],
                    "resposta_gerada": str(row_resp.get(modelo["col_resp"], "")).strip(),
                    "juiz_llm": {
                        "nota_likert": int(float_limpo(row_notas.get(modelo["col_nota"], 0))),
                        "justificativa_tecnica": str(row_notas.get(modelo["col_justificativa"], "")).strip()
                    }
                }
                
                if modelo["nome"] == "AmazoniaExpert.IA":
                    avaliacao["similaridade_faiss_percentual"] = float_limpo(row_faiss.get("FAISS_AMAZONIAEXPERT", 0.0))
                
                documento["avaliacoes_modelos"].append(avaliacao)
        
        dataset_final.append(documento)
        
    except Exception as e:
        print(f"Aviso: Não foi possível processar completamente o bloco da QUESTÃO {id_match.group(1) if id_match else 'Desconhecida'}. Erro: {e}")

# ==========================================
# 5. EXPORTAÇÃO
# ==========================================
os.makedirs(pasta_saida, exist_ok=True)
print(f"Processamento concluído. Exportando JSON com {len(dataset_final)} questões e avaliações aninhadas...")

with open(arquivo_saida, 'w', encoding='utf-8') as f:
    json.dump(dataset_final, f, ensure_ascii=False, indent=4)

print(f"Sucesso! Dataset estruturado gerado em: {arquivo_saida}")