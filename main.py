"""
Script para ler e executar a anonimização em arquivos CSV.
Lê o CSV, aplica os detectores e salva o resultado.
"""

import os
import pandas as pd
import traceback
from anonbr.anonymizer import Anonymizer

arquivo_entrada = os.path.join('exemples', 'dados_exemplo.csv')
diretorio_saida = os.path.join('exemples', 'anonymized_data')
arquivo_saida = os.path.join(diretorio_saida, 'censurados.csv')

def carregar_dados(caminho):
    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        return True

    df = pd.read_csv(
        caminho,
        sep=',',
        encoding='utf-8',
        engine='python',
        on_bad_lines='skip'
    )

    print(f"Arquivo carregado: {caminho}")
    print(f"linhas: {len(df)}, colunas: {list(df.columns)}")

    return df

def salvar_dados(df, caminho):
    diretorio = os.path.dirname(caminho)
    if diretorio and not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"Diretório criado: {diretorio}")

    df.to_csv(caminho, sep=',', index=False, encoding='utf-8')
    print(f"Arquivo salvo: {caminho}")

def main():
    try:
        df = carregar_dados(arquivo_entrada)
        if df is None:
            return 1

        anonimizador = Anonymizer(nivel='padrao')
        relatorio = anonimizador.relatorio(df)

        print("\n--- Dados sensíveis detectados ---")
        for tipo, colunas in relatorio.items():
            if colunas:
                print(f" {tipo}: {colunas}")

        total_detectado = sum(len(cols) for cols in relatorio.values())
        if total_detectado == 0:
            print("Nenhum dado sensível detectado.")
            return 0

        df_anonimizado = anonimizador.anonimizar(df)
        print(f"\nAnonimização concluída. {total_detectado} colunas processadas.")

        salvar_dados(df_anonimizado, arquivo_saida)
        return 0

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
        return 1
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())