import os
import json
import re
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared, operations
from html.parser import HTMLParser

load_dotenv()


PASTA_ORIGEM = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\Artigos\Ingles"
PASTA_DESTINO = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Limpos"

os.makedirs(PASTA_DESTINO, exist_ok=True)
client = UnstructuredClient(api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"))


MAPA_PARTES = {
    "Part_I": "The Amazon as a Regional Entity of the Earth System",
    "Part_II": "Social-Ecological Transformations: Changes in the Amazon",
    "Part_III": "The Solution Space: Finding Sustainable Pathways for the Amazon",
    "Annex": "Annexes and Definitions"
}

MAPA_CAPITULOS = {
    1: "Geology and Geodiversity of the Amazon: Three Billion Years of History", 2: "Evolution of Amazonian Biodiversity",
    3: "Biological Diversity and Ecological Networks in the Amazon", 4: "Amazonian Ecosystems and Their Ecological Functions",
    5: "The Physical Hydroclimate System of the Amazon", 6: "Biogeochemical Cycles in the Amazon",
    7: "Biogeophysical Cycles: Water Recycling, Climate Regulation", 8: "Peoples of the Amazon Before European Colonization",
    9: "Peoples of the Amazon and European Colonization (16th-18th Centuries)", 10: "Critical Interconnections Between the Cultural and Biological Diversity of Amazonian Peoples and Ecosystems",
    11: "Economic Drivers in the Amazon from the 19th Century to the 1970s", 12: "Languages of the Amazon: Dimensions of Diversity",
    13: "African Presence in the Amazon: A Glance", 14: "Amazon in Motion: Changing Politics, Development Strategies, Peoples, Landscapes, and Livelihoods",
    15: "Complex, Diverse, and Changing Agribusiness and Livelihood Systems in the Amazon", 16: "The State of Conservation Policies, Protected Areas, and Indigenous Territories, from the Past to the Present",
    17: "Globalization, Extractivism, and Social Exclusion: Threats and Opportunities to Amazon Governance in Brazil", 18: "Globalization, Extractivism, and Social Exclusion: Country-Specific Manifestations",
    19: "Drivers and Ecological Impacts of Deforestation and Forest Degradation", 20: "Drivers and Impacts of Changes in Aquatic Ecosystems",
    21: "Human Well-Being and Health Impacts of the Degradation of Terrestrial and Aquatic Ecosystems", 22: "Long-Term Variability, Extremes, and Changes in Temperature and Hydro Meteorology",
    23: "Impacts of Deforestation and Climate Change on Biodiversity, Ecological Processes, and Environmental Adaptation", 24: "Resilience of the Amazon Forest to Global Changes: Assessing the Risk of Tipping Points",
    25: "A Pan-Amazonian sustainable development vision", 26: "Sustainable Development Goals (SDGs) and the Amazon",
    27: "Conservation measures to counter the main threats to Amazonian biodiversity", 28: "Restoration options for the Amazon",
    29: "Restoration priorities and benefits within landscapes and catchments and across the Amazon Basin", 30: "Opportunities and challenges for a healthy standing forest and flowing rivers bioeconomy in the Amazon",
    31: "Strengthening land and natural resource governance and management: Protected areas, Indigenous lands, and local communities territories", 32: "Milestones and challenges in the construction and expansion of participatory intercultural education in the Amazon",
    33: "Connecting and sharing diverse knowledges to support sustainable pathways in the Amazon", 34: "Boosting relations between the Amazon forest and its globalizing cities",
    "CC1": "Cross Chapter 1: The Amazon Carbon Budget",
    "CC2": "Cross Chapter 2: Legacy from the Ancestors: Amazonian Biocultural Landscapes and Global Sustainability in a Post-COVID-19 World",
    "Annex I": "The multiple viewpoints for the Amazon: geographic limits and meanings",
    "Annex II": "Definition of Indigenous peoples and local communities for the Science Panel for the Amazon"
}

PAGINAS_INDEX_POR_CAPITULO = {
    25: [3, 4],
    "Annex II": [2],
    "Annex I": []
}

class SimpleHTMLTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_data = []; self.current_row = []; self.current_cell = ""; self.in_cell = False
    def handle_starttag(self, tag, attrs):
        if tag in ["td", "th"]: self.in_cell = True
    def handle_endtag(self, tag):
        if tag in ["td", "th"]:
            self.current_row.append(self.current_cell.strip())
            self.current_cell = ""; self.in_cell = False
        elif tag == "tr":
            self.table_data.append(self.current_row); self.current_row = []
    def handle_data(self, data):
        if self.in_cell: self.current_cell += data

def deve_pular_pagina(pagina, capitulo, texto):
    if capitulo == "Annex I": 
        return False
    
    try: pagina = int(pagina)
    except: pass
    
    if pagina == 1: 
        return True
    
    if capitulo in PAGINAS_INDEX_POR_CAPITULO and pagina in PAGINAS_INDEX_POR_CAPITULO[capitulo]:
        return True
        
    if isinstance(capitulo, int) and capitulo != 25 and pagina == 3:
        return True
        
    texto_upper = texto.upper()
    if "ABOUT THE SCIENCE PANEL FOR THE AMAZON" in texto_upper: return True
    if "INDEX" in texto_upper and re.search(r'\.{5,}', texto): return True
    return False

def identificar_ruido_visual(texto):
    if not texto: return True
    if len(texto) > 10 and (texto.count(' ') / len(texto)) > 0.35: return True
    letras = re.findall(r'[a-zA-Z]', texto)
    if len(texto) > 40 and (len(letras) / len(texto)) < 0.2: return True
    return False

def limpar_ruido_ocr(texto, capitulo_atual, nome_capitulo):
    if not texto: return ""
    
    padroes_remover = [
        r"Amazon Assessment Report 2021", 
        r"CONTACT INFORMATION.*", 
        r"Science Panel for the Amazon",
        r"THE\s+AMAZON\s+WE\s+WANT", 
        r"SUSTAINABLE DEVELOPMENT.*?UNITED NATIONS", 
        r"SPA Technical-Scientific Secretariat.*"
    ]
    for padrao in padroes_remover:
        texto = re.sub(padrao, '', texto, flags=re.IGNORECASE | re.DOTALL)

    prefixo = f"Chapter {capitulo_atual}" if str(capitulo_atual).isdigit() else str(capitulo_atual)
    palavras_titulo = [re.escape(p) for p in str(nome_capitulo).replace('-', ' ').split() if len(p) > 2]
    
    if palavras_titulo:
        padrao_titulo = r'[\s\W]*'.join(palavras_titulo[:5])
        padrao_inline = rf'\b(?:\d{{1,3}}\s+)?{prefixo}[\s\W]+.*?{padrao_titulo}.*?(?=\s+[a-z]|\n|$)'
        texto = re.sub(padrao_inline, ' ', texto, flags=re.IGNORECASE)
    else:
        padrao_inline = rf'\b(?:\d{{1,3}}\s+)?{prefixo}\s*:.*?(?=\s+[a-z]|\n|$)'
        texto = re.sub(padrao_inline, ' ', texto, flags=re.IGNORECASE)

    texto = re.sub(r'^\d{1,3}\s+', '', texto)
    texto = re.sub(r'\s+\d{1,3}$', '', texto)
    
    texto = re.sub(r'([^a-zA-Z0-9\s])\1{2,}', '', texto)
    
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def extrair_metadados_nome(nome):
    meta = {"part_key": "Other", "chapter": None}
    n_low = nome.lower()
    
    if "part_iii" in n_low: meta["part_key"] = "Part_III"
    elif "part_ii" in n_low: meta["part_key"] = "Part_II"
    elif "part_i" in n_low: meta["part_key"] = "Part_I"
    elif "annex" in n_low: meta["part_key"] = "Annex"

    if "annex_ii" in n_low or "annex ii" in n_low: meta["chapter"] = "Annex II"
    elif "annex_i" in n_low or "annex i" in n_low: meta["chapter"] = "Annex I"
    elif "cc1" in n_low or "cross_chapter_1" in n_low: meta["chapter"] = "CC1"
    elif "cc2" in n_low or "cross_chapter_2" in n_low: meta["chapter"] = "CC2"
    else:
        cap_match = re.search(r'cap_(\d+)', nome, re.I)
        if cap_match: meta["chapter"] = int(cap_match.group(1))
    return meta

def iniciar_processamento():
    print("--- iniciando processamento ---\n")
    arquivos = [f for f in os.listdir(PASTA_ORIGEM) if f.lower().endswith('.pdf')]
    
    for nome_arquivo in arquivos:
        info = extrair_metadados_nome(nome_arquivo)
        nome_parte = MAPA_PARTES.get(info["part_key"], "Other")
        nome_capitulo = MAPA_CAPITULOS.get(info["chapter"], "Special Section/Annex")
        
        print(f"processando: {nome_arquivo} | ID: {info['chapter']}")
        with open(os.path.join(PASTA_ORIGEM, nome_arquivo), "rb") as f:
            data = f.read()

        params = shared.PartitionParameters(
            files=shared.Files(content=data, file_name=nome_arquivo),
            strategy="hi_res", 
            languages=["eng"], 
            model_name="layout_v1", 
            chunking_strategy="by_title", 
            max_characters=1000, 
            combine_under_n_chars=500,
            multipage_sections=True, 
            infer_table_structure=True
        )
        
        try:
            res = client.general.partition(request=operations.PartitionRequest(partition_parameters=params))
            chunks_finais = []
            pular_pag = set()
            dentro_annex_33_2 = False
            secao_pai_num = str(info["chapter"])
            secao_pai_nome = "General Content"
            cont = 0

            for el in res.elements:
                pg = el.get("metadata", {}).get("page_number")
                if deve_pular_pagina(pg, info["chapter"], el.get("text", "")):
                    pular_pag.add(pg)

            for el in res.elements:
                texto_bruto = el.get("text", "").strip()
                pagina = el.get("metadata", {}).get("page_number")
                tipo = str(el.get("type"))

                if pagina in pular_pag or not texto_bruto: continue
                
                texto_bruto = re.sub(r'([a-zA-Z]+)-\s*\n\s*([a-zA-Z]+)', r'\1\2', texto_bruto)
                texto_bruto = re.sub(r'([a-zA-Z]+)-\s+([a-zA-Z]+)', r'\1\2', texto_bruto)

                # --- LÓGICA DE DIVISÃO (SPLIT) OTIMIZADA ---
                padrao_split = r'(?:^|\n|\s)(\d+(?:\.\d+)+)[\.\s]+(?=[A-Z])'
                ocorrencias = list(re.finditer(padrao_split, texto_bruto))
                
                partes = []
                if ocorrencias:
                    indices = [m.start() + (1 if texto_bruto[m.start()].isspace() else 0) for m in ocorrencias]
                    
                    if indices[0] > 0:
                        partes.append(texto_bruto[0:indices[0]].strip())
                    
                    for i in range(len(indices)):
                        inicio = indices[i]
                        fim = indices[i+1] if i+1 < len(indices) else len(texto_bruto)
                        partes.append(texto_bruto[inicio:fim].strip())
                else:
                    partes.append(texto_bruto)

                for txt_p in partes:
                    if not txt_p: continue

                    m_h = re.match(r'^(\d+(?:\.\d+)+)[\.\s]+([A-Z].*)', txt_p)
                    if m_h and not dentro_annex_33_2:
                        num_det = m_h.group(1)
                        if len(num_det.split('.')) <= 4:
                            secao_pai_num = num_det
                            secao_pai_nome = m_h.group(2).split('\n')[0][:100].strip()

                    # Correção de Títulos Especiais (Abstract, Key Messages)
                    m_especial = re.match(r'^(ABSTRACT|GRAPHICAL ABSTRACT|KEY MESSAGES)', txt_p, re.IGNORECASE)
                    if m_especial:
                        secao_pai_num = str(info["chapter"])
                        secao_pai_nome = m_especial.group(1).title()

                    # Tratamento Capítulo 32 e 33
                    if info["chapter"] == 32:
                        m32 = re.match(r'^(A32\.\d+)[\.\s]+(.*)', txt_p)
                        if m32: secao_pai_num = m32.group(1); secao_pai_nome = m32.group(2).split('\n')[0].strip()

                    if info["chapter"] == 33:
                        if "ANNEX 33.1" in txt_p.upper():
                            secao_pai_num = "33.1"; secao_pai_nome = "Conceptual Framework"; dentro_annex_33_2 = False
                        elif "ANNEX 33.2" in txt_p.upper():
                            secao_pai_num = "33.2"; secao_pai_nome = "Illustrative experiences"; dentro_annex_33_2 = True
                        if dentro_annex_33_2 and "Country:" in txt_p:
                            secao_pai_num = "33.2-EXP"; secao_pai_nome = re.split(r'Country:', txt_p, flags=re.I)[0].strip()[:100]

                    # Filtros de Ruído
                    imunidade = (tipo == "Table" or re.match(r'^(Figure|Table|Figura|Tabela)\s+\d+', txt_p, re.I))
                    if not imunidade and tipo not in ["Title", "Table"]:
                        if identificar_ruido_visual(txt_p): continue

                    # Limpeza Final (Enviando também o nome_capitulo para caçar rodapés intrometidos)
                    texto_limpo = limpar_ruido_ocr(txt_p, info["chapter"], nome_capitulo)
                    if not imunidade and len(texto_limpo) < 25 and tipo not in ["Title", "Table"]: continue

                    cont += 1
                    chunk = {
                        "text": texto_limpo, "type": tipo,
                        "metadata": {
                            "source": nome_arquivo, "part_name": nome_parte, "chapter_name": nome_capitulo,
                            "chapter_number": info["chapter"], "chunk_seq": cont,
                            "parent_section_number": secao_pai_num, "parent_section_name": secao_pai_nome,
                            "page": pagina, "element_id": el.get("element_id")
                        }
                    }

                    if "Table" in tipo and "text_as_html" in el.get("metadata", {}):
                        html = el["metadata"]["text_as_html"]; chunk["metadata"]["table_html"] = html
                        try:
                            parser = SimpleHTMLTableParser(); parser.feed(html)
                            chunk["metadata"]["table_data_structured"] = parser.table_data
                        except: chunk["metadata"]["table_data_structured"] = None

                    chunks_finais.append(chunk)

            # 4. Salvar Arquivo Json
            nome_json = nome_arquivo.replace(".pdf", ".json")
            with open(os.path.join(PASTA_DESTINO, nome_json), "w", encoding="utf-8") as f_out:
                json.dump(chunks_finais, f_out, indent=4, ensure_ascii=False)
            print(f"sucesso: {nome_arquivo} ({len(chunks_finais)} chunks)\n")

        except Exception as e:
            print(f"erro crítico em {nome_arquivo}: {e}")

if __name__ == "__main__":
    iniciar_processamento()