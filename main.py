"""
Script para ler e executar a anonimização em arquivos CSV.
Lê o CSV, aplica os detectores e salva o resultado.
"""

import os
import pandas as pd
import traceback
import argparse
from anonbr.anonymizer import Anonymizer

def load_data(path, separator):
    # Lê o CSV e retorna um DataFrame:
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return None

    df = pd.read_csv(
        path,
        sep=separator,
        encoding='utf-8',
        engine='python',
        on_bad_lines='skip'
    )

    print(f"Arquivo carregado: {path}")
    print(f"Linhas: {len(df)}, Colunas: {list(df.columns)}")
    
    return df

def save_data(df, path, separator):
    # Salva o CSV com os dados censurados  
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Diretório criado: {directory}")

    df.to_csv(path, sep=separator, index=False, encoding='utf-8')
    print(f"Arquivo salvo: {path}")

def create_parser():
    # Cria e configura o parser de argumentos.
    parser = argparse.ArgumentParser(
        description='Anonbr - teste CSV'
    )

    # Argumento obrigatório (arquivo de entrada)
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Caminho em que arquivo CSV está salvo.'
    )

    # Argumento opcional (nome do arquivo pronto)
    parser.add_argument(
        '-o', '--output',
        default='dados_censurados.csv',
        help='Nome do arquivo pronto. (padrão: dados_censurados.csv)'
    )

    # Argumento opcional (Nível de censura)
    parser.add_argument(
        '-l', '--level',
        choices=['default', 'high', 'low'],
        default='default',
        help='Nível de censura dos dados: defult, high, low. (padrão, alto, baixo)'
    )

    # Argumento opcional (separador do CSV)
    parser.add_argument(
        '-s', '--sep',
        default=',',
        help='Separador do CSV. (padão: vírgula)'
    )

    # Argumento opcional (gera relatório)
    parser.add_argument(
        '-r', '--report',
        action='store_true',
        help='Exibe relatório de colunas com dados sensíveis detectados.'
    )

    return parser

def main():
    # Parseia os argumentos no terminal
    parser = create_parser()
    args = parser.parse_args()

    try:
        # carregar
        df = load_data(args.input, args.sep)
        if df is None:
            return 1

        # Criar anonimizador
        create_anonymizer = Anonymizer(level=args.level)

        # Relatório (se solicitado)
        if args.report:
            report = create_anonymizer.report(df)
            print("\n--- Dados sensíveis detectados ---")
            for data_type, columns in report.items():
                if columns:
                    print(f"{data_type}: {columns}")

        # Verificar se há dados sensíveis
        report = create_anonymizer.report(df)
        total_detected = sum(len(cols) for cols in report.values())

        if total_detected == 0:
            print("Nenhum dados sinsível detectado. Nada a fazer")
            return 0

        # Anonimizar
        df_anonymized = create_anonymizer.anonymize(df)

        print(f"\nAnonimização concluída. {total_detected} colunas processadas.")
        print(f"Nível de mascaramento: {args.level}")

        # Salvar
        save_data(df_anonymized, args.output, args.sep)
        return 0

    except FileExistsError as e:
        print(f"Arquivo não encontrado: {e}")
        return 1
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())