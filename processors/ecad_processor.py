import pdfplumber
import re
import pandas as pd

class ECADProcessor:
    @staticmethod
    def identificar_modelo(caminho_pdf):
        with pdfplumber.open(caminho_pdf) as pdf:
            primeira_pagina = pdf.pages[0].extract_text()
            if not primeira_pagina:
                return "VAZIO"
            
            # Identificação baseada nos prints enviados
            if "RELATÓRIO ANALÍTICO" in primeira_pagina.upper():
                return "ANALITICO"
            elif "DEMONSTRATIVO" in primeira_pagina.upper() or "DISTRIBUIÇÃO" in primeira_pagina.upper():
                return "DISTRIBUICAO"
        return "DESCONHECIDO"

    def extrair_analitico(self, caminho_pdf):
        dados = []
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                linhas = text.split('\n')
                isrc_atual, titulo_atual = "", ""
                
                for linha in linhas:
                    # Captura ISRC e Título
                    match_obra = re.search(r'([A-Z0-9-]{12})\s+LIBERADO\s+(.*)', linha)
                    if match_obra:
                        isrc_atual = match_obra.group(1)
                        titulo_atual = match_obra.group(2).split("NÃO")[0].strip()
                        continue
                    
                    # Captura Titulares
                    match_titular = re.search(r'(\d{4,})\s+(.*?)\s+(?:[A-Z]{1,2}\s+){2,}[A-Z]+\s+(\d+,\d+)', linha)
                    if match_titular:
                        dados.append({
                            "ISRC": isrc_atual,
                            "TITULO": titulo_atual,
                            "TITULAR": match_titular.group(2).strip(),
                            "PARTICIPACAO_%": match_titular.group(3)
                        })
        return pd.DataFrame(dados)

    def extrair_distribuicao(self, caminho_pdf):
        dados = []
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                linhas = text.split('\n')
                obra_atual = ""

                for linha in linhas:
                    # Identifica a Obra (geralmente em destaque no modelo 2)
                    if re.match(r'^\d{7,}\s+', linha): 
                        obra_atual = linha.split('  ')[0] # Pega o início da linha
                    
                    # Captura Rubrica e Rendimentos (ex: AP-CARNAVAL ... 140,57)
                    match_valores = re.search(r'([A-Z-]{3,}\s.*?)\s+(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)', linha)
                    if match_valores:
                        dados.append({
                            "OBRA": obra_atual,
                            "RUBRICA": match_valores.group(1).strip(),
                            "RENDIMENTO": match_valores.group(2),
                            "RATEIO": match_valores.group(4)
                        })
        return pd.DataFrame(dados)