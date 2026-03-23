"""
Script para ler e executar a anonimização em arquivos CSV.
Lê o CSV, aplica os detectores e salva o resultado.
"""

import os
import sys
import pandas as pd
import traceback
import argparse
import textwrap
import warnings
from anonbr.anonymizer import Anonymizer
from anonbr.detectors.pdf import PDFDetector

def load_data(path, separator):
    # Lê o CSV e retorna um DataFrame:
    if not os.path.exists(path):
        print(f"\nArquivo não encontrado: {path}")
        return None

    # Configuração padrão
    df = pd.read_csv(
        path,
        sep=separator,
        encoding='utf-8',
        engine='python',
        on_bad_lines='skip'
    )

    print(f"\nArquivo carregado: {path}")
    print(f"Linhas: {len(df)}, Colunas: {list(df.columns)}")
    
    return df

def save_data(df, path, separator):
    # Salva o CSV com os dados censurados  
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Diretório criado: {directory}")

    df.to_csv(path, sep=separator, index=False, encoding='utf-8')
    print(f"Arquivo salvo: {path}\n")

# Cores: não tente editar, senão vai ficar piscando kkkkkk
DARK_BLUE = '\033[38;5;20m'
NAVY = '\033[38;5;18m'
BLUE = '\033[34m'
GREEN = '\033[32m'
CYAN = '\033[36m'
RED = '\033[31m'
BOLD = '\033[1m'
WHITE = '\033[37m'
RESET = '\033[0m'

""" O BOLD serve para deixar a cor mais viva/ brilhante, no formato atual ANON- está em branco
    e BR em verde. Se remover o RESET vai colorir todo o texto de saída no terminal."""

# Pois é, parece uma gambiarra do krl, mas tá bonito no terminal. 
logo = f'''\n{BOLD}{WHITE}
 █████╗ ███╗   ██╗ ██████╗ ███╗   ██╗      {GREEN}██████╗ ██████╗ {WHITE}
██╔══██╗████╗  ██║██╔═══██╗████╗  ██║      {GREEN}██╔══██╗██╔══██╗{WHITE}
███████║██╔██╗ ██║██║   ██║██╔██╗ ██║█████╗{GREEN}██████╔╝██████╔╝{WHITE}
██╔══██║██║╚██╗██║██║   ██║██║╚██╗██║╚════╝{GREEN}██╔══██╗██╔══██╗{WHITE}
██║  ██║██║ ╚████║╚██████╔╝██║ ╚████║      {GREEN}██████╔╝██║  ██║{WHITE}
╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═══╝      {GREEN}╚═════╝ ╚═╝  ╚═╝{RESET}\n'''

spacebar = " " * 20
def create_parser():
    parser = argparse.ArgumentParser(
        prog='ATENÇÃO',
        # Formatação proposital para exibição mais organizada no terminal.
        usage=f'''LinkedIn: Yuri Pontes\n
  -i, --input       Local e o nome do arquivo (ex: documentos/dados.csv)
  -o, --output      Destino e o nome do arquivo. (padrão: dados_censurados.csv)
  -l, --level       Nível de censura dos dados.
{spacebar}default: padrão \n{spacebar}high: alto \n{spacebar}low: baixo
  -s, --sep         Separador do CSV. (padrão: vírgula)
  -r, --report      Exibe relatório de colunas com dados sensíveis detectados.
  ''',
    )

    # Argumento obrigatório (arquivo de entrada)
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Local e o nome do arquivo (ex: documentos/dados.csv)'
    )

    # Argumento opcional (nome do arquivo pronto)
    parser.add_argument(
        '-o', '--output',
        default='dados_censurados.csv',
        help='Destino e o nome do arquivo. (padrão: dados_censurados.csv)'
    )

    # Argumento opcional (Nível de censura)
    parser.add_argument(
        '-l', '--level',
        choices=['default', 'high', 'low'],
        default='default',
        help='Nível de censura dos dados: default, high, low. (padrão, alto, baixo)'
    )

    # Argumento opcional (separador do CSV)
    parser.add_argument(
        '-s', '--sep',
        default=',',
        help='Separador do CSV. (padrão: vírgula)'
    )

    # Argumento opcional (gera relatório)
    parser.add_argument(
        '-r', '--report',
        action='store_true',
        help='Exibe relatório de colunas com dados sensíveis detectados.'
    )
    
    return parser

def main():
    # Imprime a logo (ANON-BR) no terminal 
    print(logo)
    
    # Parseia os argumentos no terminal
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.input.endswith('.pdf'):
            # Fluxo PDF
            detector = PDFDetector(level=args.level)
            output = args.output if args.output != 'dados_censurados.csv' else 'censurado.pdf'
            summary = detector.mask(args.input, output)
            print(f"\nOperação concluída.")
            print(f"CPFs: {summary['cpf']}, CNPJs: {summary['cnpj']}, Emails: {summary['email']}, Telefones: {summary['phone']}")
            print(f"Páginas processadas: {summary['pages_processed']}")
            print(f"Arquivo salvo: {output}\n")
            return 0

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

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
        return 1
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())