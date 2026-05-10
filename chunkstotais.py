import json
import glob
import os

def calcular_total_chunks_por_seq(diretorio):
    caminho_busca = os.path.join(diretorio, "*.json")
    arquivos_json = glob.glob(caminho_busca)
    
    chunk_total = 0
    arquivos_processados = 0
    
    print(f"Iniciando a soma do último 'chunk_seq' no diretório: {diretorio}\n")
    
    for caminho_arquivo in arquivos_json:
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
                
                # Verifica se não está vazio e se é uma lista
                if isinstance(dados, list) and len(dados) > 0:
                    # Pega o último elemento da lista
                    ultimo_elemento = dados[-1]
                    
                    # Acessa o chunk_seq dentro do metadata
                    ultimo_seq = ultimo_elemento.get("metadata", {}).get("chunk_seq", 0)
                    
                    chunk_total += ultimo_seq
                    arquivos_processados += 1
                    
                    print(f"- {os.path.basename(caminho_arquivo)}: último chunk_seq = {ultimo_seq}")
                else:
                    print(f"[Aviso] O arquivo {os.path.basename(caminho_arquivo)} está vazio ou não é uma lista.")
                    
        except KeyError:
            print(f"[Erro] Estrutura de metadata/chunk_seq não encontrada em: {os.path.basename(caminho_arquivo)}")
        except json.JSONDecodeError:
            print(f"[Erro] JSON inválido: {os.path.basename(caminho_arquivo)}")
        except Exception as e:
            print(f"[Erro] Falha ao ler {os.path.basename(caminho_arquivo)}: {e}")

    print("\n" + "-"*40)
    print("RESUMO FINAL:")
    print(f"Arquivos processados: {arquivos_processados}")
    print(f"Total de chunks (soma dos últimos chunk_seq): {chunk_total}")
    print("-"*40)

# Altere o caminho abaixo se necessário
diretorio_dados = r"C:\TCCII\DSW\RAG\Dados_Limpos"

if __name__ == "__main__":
    calcular_total_chunks_por_seq(diretorio_dados)