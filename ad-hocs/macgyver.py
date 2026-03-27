# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pdfplumber",
# ]
# ///

import argparse
import pdfplumber

def check_pdf(file_path, search_term, page_num=19):
    try:
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[page_num]
            text = ''.join(c['text'] for c in page.chars)

            if search_term.lower() in text.lower():
                idx = text.lower().index(search_term.lower())
                print(f"Encontrado: {repr(text[idx-30:idx+30])}")
            else:
                print(f"'{search_term}' não encontrado na página {page_num + 1}")
                print(f"Fim da página: {repr(text[-200:])}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca texto em uma página de PDF")
    parser.add_argument("-f", "--file", required=True, metavar="ARQUIVO", help="Caminho do arquivo PDF")
    parser.add_argument("-p", "--page", type=int, default=20, metavar="PÁGINA", help="Número da página (padrão: 20)")
    parser.add_argument("-i", "--input", required=True, metavar="FRASE", help="Frase a buscar")
    args = parser.parse_args()

    check_pdf(args.file, args.input, args.page - 1)