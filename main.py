"""
Script para ler e executar a anonimização em arquivos CSV.
Lê o CSV, aplica os detectores e salva o resultado.
"""

import os
import pandas as pd
import traceback
from anonbr.anonymizer import Anonymizer

input_file = os.path.join('exemples', 'dados_teste_validacao.csv')
output_directory = os.path.join('exemples', 'anonymized_data')
output_file = os.path.join(output_directory, 'censurados.csv')

def load_data(path):
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return True

    df = pd.read_csv(
        path,
        sep=',',
        encoding='utf-8',
        engine='python',
        on_bad_lines='skip'
    )

    print(f"Arquivo carregado: {path}")
    print(f"linhas: {len(df)}, colunas: {list(df.columns)}")

    return df

def save_data(df, path):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Diretório criado: {directory}")

    df.to_csv(path, sep=',', index=False, encoding='utf-8')
    print(f"Arquivo salvo: {path}")

def main():
    try:
        df = load_data(input_file)
        if df is None:
            return 1

        anonymizer = Anonymizer(level='default')
        report = anonymizer.report(df)

        print("\n--- Dados sensíveis detectados ---")
        for data_type, columns in report.items():
            if columns:
                print(f" {data_type}: {columns}")

        total_detected = sum(len(cols) for cols in report.values())
        if total_detected == 0:
            print("Nenhum dado sensível detectado.")
            return 0

        anonymized_df = anonymizer.anonymize(df)
        print(f"\nAnonimização concluída. {total_detected} colunas processadas.")

        save_data(anonymized_df, output_file)
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