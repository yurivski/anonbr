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
  --cpf             Executa apenas para dados de CPF.
  --email           Executa apenas para dados de E-Mail.
  --phone           Executa apenas para dados de Telefone.
  --detect          Apenas detecta os dados, sem mascarar.
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

    # Filtro: executa apenas para CPF
    parser.add_argument(
        '--cpf',
        action='store_true',
        help='Executa apenas para dados de CPF.'
    )

    # Filtro: executa apenas para e-mail
    parser.add_argument(
        '--email',
        action='store_true',
        help='Executa apenas para dados de E-Mail.'
    )

    # Filtro: executa apenas para telefone
    parser.add_argument(
        '--phone',
        action='store_true',
        help='Executa apenas para dados de Telefone.'
    )

    # Modo detecção: roda o sistema sem mascarar nada
    parser.add_argument(
        '--detect',
        action='store_true',
        help='Apenas detecta os dados sensíveis, sem mascarar.'
    )

    return parser

def main():
    # Imprime a logo (ANON-BR) no terminal
    print(logo)

    # Parseia os argumentos no terminal
    parser = create_parser()
    args = parser.parse_args()

    # Monta a lista de tipos ativos com base nos filtros passados.
    # Se nenhum filtro for passado, data_types fica None e o sistema processa tudo.
    selected_types = []
    if args.cpf:
        selected_types.append('cpf')
    if args.email:
        selected_types.append('email')
    if args.phone:
        selected_types.append('phone')
    data_types = selected_types if selected_types else None

    try:
        if args.input.endswith('.pdf'):
            # Fluxo PDF
            detector = PDFDetector(level=args.level, data_types=data_types)
            output = args.output if args.output != 'dados_censurados.csv' else 'censurado.pdf'

            if args.detect:
                # Modo detecção: apenas reporta o que foi encontrado, sem gerar arquivo
                findings = detector.detect(args.input)
                counts = {'cpf': 0, 'cnpj': 0, 'email': 0, 'phone': 0}
                for page_items in findings.values():
                    for item in page_items:
                        if item['type'] in counts:
                            counts[item['type']] += 1

                total = sum(counts.values())
                print(f"\nDetecção concluída. {total} dado(s) sensível(is) encontrado(s).")
                for dtype, count in counts.items():
                    if count > 0:
                        print(f"  {dtype.upper()}: {count}")
                return 0

            summary = detector.mask(args.input, output)
            print(f"\nOperação concluída.")
            print(f"CPFs: {summary['cpf']}, CNPJs: {summary['cnpj']}, Emails: {summary['email']}, Telefones: {summary['phone']}")
            print(f"Páginas processadas: {summary['pages_processed']}")
            print(f"Arquivo salvo: {output}\n")
            return 0

        df = load_data(args.input, args.sep)
        if df is None:
            return 1

        # Criar anonimizador com os tipos de dados selecionados
        create_anonymizer = Anonymizer(level=args.level, data_types=data_types)

        # Calcula o relatório uma vez só (usado no --report, --detect e na verificação)
        report = create_anonymizer.report(df)
        total_detected = sum(len(cols) for cols in report.values())

        # Exibe relatório se --report ou --detect foi solicitado
        if args.report or args.detect:
            print("\n--- Dados sensíveis detectados ---")
            for data_type, columns in report.items():
                if columns:
                    print(f"  {data_type}: {columns}")

        # Modo detecção: para aqui sem mascarar nada
        if args.detect:
            if total_detected == 0:
                print("Nenhum dado sensível detectado.")
            return 0

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
