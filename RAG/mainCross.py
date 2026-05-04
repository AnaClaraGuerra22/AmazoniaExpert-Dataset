import os
import json
import re

PASTA_ENTRADA = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Limpos"
PASTA_SAIDA = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Tratados_CC"

os.makedirs(PASTA_SAIDA, exist_ok=True)

SECOES_FIXAS = {
    "CC1": ["Abstract", "CB1. CO2 Uptake and Emissions", "CB2. Methane Emissions", "CB3. References"],
    "CC2": ["CC2.1 Introduction", "CC2.2 The Amazon Sacred Headwaters Initiative", "CC2.3 Ally Guayusa Cooperative", "CC2.4 The Amazon Hopes Collective", "CC2.5 Recommendations", "CC2.6 References"]
}

PADROES_LIXO = [
    r"Cross-Chapter: The Amazon Carbon Budget",
    r"Cross-Chapter Box: Legacy from the Ancestors.*",
    r"Cross-Chapter: Legacy from the Ancestors: Amazonian Biocultural Landscapes and Global Sustainability in a Post-COVID-19 World",
    r"Science Panel for the Amazon",
    r"THE AMAZON WE WANT",
    r"CONTACT INFORMATION.*",
    r"SPA Technical-Scientific Secretariat.*",
    r"Sustainable Development Solutions Network.*",
    r"About the Science Panel for the Amazon.*",
    r"Av\. dos Astronautas.*?\d{5}-\d{3}.*?Brazil", 
    r"Av\. Prof\. Lineu Prestes.*?Brazil",          
    r"University of California.*?USA",
    r"University of Arizona.*?USA",
    r"Lancaster University.*?UK",
    r"University of Leeds.*?United Kingdom"
]

def limpar_profundo(texto):
    if "During the last 40 to 50 years" in texto and "Mapping" in texto:
        texto = ("During the last 40 to 50 years, the Amazon has experienced strong human impacts from "
                 "deforestation and land use change. According to the Brazilian Annual Land Use and "
                 "Land Cover Mapping Project (Mapbiomas Amazonia 2020), a cumulative total of 17% "
                 "was deforested by 2019.")

    texto = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', texto)
    padrao_afiliacoes = r"(^|\s)[a-g]\s[A-Z][a-zA-Z\s,.\-\/]+(Brazil|USA|UK|Colombia|Kingdom|Ecuador|Secretariat|University|Institute)"
    texto = re.sub(padrao_afiliacoes, '', texto, flags=re.MULTILINE)

    for padrao in PADROES_LIXO:
        texto = re.sub(padrao, '', texto, flags=re.IGNORECASE)
    
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def tratar_json_manual():
    print("--- Iniciando Processamento (Pulando Página 1) ---")
    arquivos = [f for f in os.listdir(PASTA_ENTRADA) if f.endswith('.json')]
    
    for nome_arquivo in arquivos:
        if "Cross Chapter" not in nome_arquivo: continue
        
        cap_key = "CC1" if "Cross Chapter 1" in nome_arquivo else "CC2"
        caminho_in = os.path.join(PASTA_ENTRADA, nome_arquivo)
        with open(caminho_in, "r", encoding="utf-8") as f:
            dados = json.load(f)

        novos_chunks = []
        secao_atual_nome = "General Content"
        secao_atual_num = cap_key
        lista_secoes = SECOES_FIXAS[cap_key]
        
        titulo_extraido_p1 = False

        for chunk in dados:
            metadata = chunk.get("metadata", {})
            pagina = metadata.get("page", 0)
            texto_bruto = chunk.get("text", "")


            if pagina == 1:
                if not titulo_extraido_p1 and "Cross Chapter" in texto_bruto:
                    chunk["text"] = limpar_profundo(texto_bruto)
                    novos_chunks.append(chunk)
                    titulo_extraido_p1 = True

                continue


            secao_encontrada = None
            for secao in lista_secoes:
                if secao in texto_bruto:
                    secao_encontrada = secao
                    break
            
            if secao_encontrada:
                partes = texto_bruto.split(secao_encontrada)
                
                t1 = limpar_profundo(partes[0])
                if len(t1) > 20:
                    c1 = chunk.copy()
                    c1.update({"text": t1, "metadata": {**metadata, "parent_section_number": secao_atual_num, "parent_section_name": secao_atual_nome}})
                    novos_chunks.append(c1)
                
                secao_atual_nome = secao_encontrada
                match_num = re.search(r'([A-Z0-9\.]+)', secao_encontrada)
                secao_atual_num = match_num.group(1) if match_num else cap_key
                
                t2 = limpar_profundo(partes[1])
                if len(t2) > 20:
                    c2 = chunk.copy()
                    c2.update({"text": t2, "metadata": {**metadata, "parent_section_number": secao_atual_num, "parent_section_name": secao_atual_nome}})
                    novos_chunks.append(c2)
            else:
                t_limpo = limpar_profundo(texto_bruto)
                if len(t_limpo) > 20:
                    chunk.update({"text": t_limpo, "metadata": {**metadata, "parent_section_number": secao_atual_num, "parent_section_name": secao_atual_nome}})
                    novos_chunks.append(chunk)

        caminho_out = os.path.join(PASTA_SAIDA, nome_arquivo)
        with open(caminho_out, "w", encoding="utf-8") as f_out:
            json.dump(novos_chunks, f_out, indent=4, ensure_ascii=False)

    print(f"--- Processo concluído! Arquivos em: {PASTA_SAIDA} ---")

if __name__ == "__main__":
    tratar_json_manual()