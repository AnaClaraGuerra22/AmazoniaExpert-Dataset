import os
import json
import pandas as pd


PASTA_JSON = r"C:\Users\anacl\OneDrive\Área de Trabalho\periodos\XI periodo\TCCII\UNSTRUCTURED\Dados_Limpos"

def gerar_auditoria():
    print("--- Iniciando Auditoria ---")
    
    arquivos = [f for f in os.listdir(PASTA_JSON) if f.lower().endswith('.json')]
    
    resumo_capitulos = []
    chunks_suspeitos = []
    
    for arquivo in arquivos:
        caminho_completo = os.path.join(PASTA_JSON, arquivo)
        
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            try:
                chunks = json.load(f)
            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")
                continue
                
        if not chunks:
            print(f"O arquivo {arquivo} está vazio!\n")
            continue


        meta_geral = chunks[0].get('metadata', {})
        capitulo_num = meta_geral.get('chapter_number', 'N/A')
        capitulo_nome = meta_geral.get('chapter_name', 'N/A')
        
        paginas_processadas = set()
        secoes_unicas = set()
        tipos_elementos = set()
        alertas = 0
        
        for c in chunks:
            texto = c.get('text', '')
            tipo = c.get('type', '')
            meta = c.get('metadata', {})
            
            pag = meta.get('page', 0)
            secao_pai = meta.get('parent_section_name', 'Desconhecida')
            
            paginas_processadas.add(pag)
            secoes_unicas.add(secao_pai)
            tipos_elementos.add(tipo)
            
  
            motivos_suspeita = []
            

            if secao_pai == "General Content" and pag > 5:
                motivos_suspeita.append("General Content em página avançada (Falha na extração de título?)")
                

            if len(texto) < 30 and tipo not in ["Table", "Title"]:
                motivos_suspeita.append("Texto muito curto (Possível lixo de OCR)")
                

            if "........" in texto or "...." in texto:
                motivos_suspeita.append("Possível vazamento de Sumário (Pontos sequenciais)")
                

            if len(texto) > 100 and texto.count(' ') / len(texto) < 0.1:
                motivos_suspeita.append("Densidade de espaços muito baixa (Palavras coladas?)")


            if motivos_suspeita:
                alertas += 1
                chunks_suspeitos.append({
                    "Arquivo": arquivo,
                    "Capítulo": capitulo_num,
                    "Página": pag,
                    "Seção Pai": secao_pai,
                    "Tipo Elemento": tipo,
                    "Tamanho Texto": len(texto),
                    "Motivo do Alerta": " | ".join(motivos_suspeita),
                    "Prévia do Texto": texto[:120] + "..." if len(texto) > 120 else texto
                })
                

        paginas_ordenadas = sorted(list(paginas_processadas))
        resumo_capitulos.append({
            "Arquivo": arquivo,
            "Capítulo": capitulo_num,
            "Nome do Capítulo": capitulo_nome,
            "Total de Chunks": len(chunks),
            "Total de Páginas Úteis": len(paginas_processadas),
            "Páginas Lidas (Min-Max)": f"{paginas_ordenadas[0]} até {paginas_ordenadas[-1]}" if paginas_ordenadas else "N/A",
            "Páginas Ignoradas (Buracos)": encontrar_paginas_faltantes(paginas_ordenadas),
            "Total de Seções Únicas": len(secoes_unicas),
            "Tipos Identificados": ", ".join(tipos_elementos),
            "Chunks com Alertas": alertas
        })


    pasta_auditoria = os.path.join(PASTA_JSON, "Auditoria")
    os.makedirs(pasta_auditoria, exist_ok=True)
    
    df_resumo = pd.DataFrame(resumo_capitulos)
    df_suspeitos = pd.DataFrame(chunks_suspeitos)
    

    if not df_resumo.empty:
        df_resumo.to_csv(os.path.join(pasta_auditoria, "Resumo_Capitulos.csv"), index=False, sep=';', encoding='utf-8-sig')
        df_resumo.to_excel(os.path.join(pasta_auditoria, "Resumo_Capitulos.xlsx"), index=False)
        
    if not df_suspeitos.empty:
        df_suspeitos.to_csv(os.path.join(pasta_auditoria, "Log_Chunks_Suspeitos.csv"), index=False, sep=';', encoding='utf-8-sig')
        df_suspeitos.to_excel(os.path.join(pasta_auditoria, "Log_Chunks_Suspeitos.xlsx"), index=False)
        
    print(f"Auditoria concluída! {len(resumo_capitulos)} arquivos analisados.\n")
    print(f"Os relatórios foram salvos na pasta: {pasta_auditoria}\n")

def encontrar_paginas_faltantes(lista_paginas):
    if not lista_paginas:
        return ""
    intervalo_completo = set(range(lista_paginas[0], lista_paginas[-1] + 1))
    faltantes = sorted(list(intervalo_completo - set(lista_paginas)))
    return ", ".join(map(str, faltantes)) if faltantes else "Nenhuma"

if __name__ == "__main__":
    gerar_auditoria()