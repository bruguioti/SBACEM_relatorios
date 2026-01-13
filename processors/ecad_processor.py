import pdfplumber
import re
import pandas as pd
import os
from datetime import datetime

class ECADProcessor:
    def __init__(self):
        # Regex para Modelos de DISTRIBUIÇÃO (Financeiros)
        self.reg_isrc = re.compile(r'ISRC\s+([A-Z0-9-]{12,15})')
        self.reg_fin = re.compile(r'^(.+?)\s+(\d{2}/\d{4}.*?)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)')
        
        # Regex para Modelos ANALÍTICOS (Cadastrais)
        self.reg_obra_analitica = re.compile(r'^(\d{7,})\s+([A-Z0-9-]{10,})\s+LIBERADO\s+(.*)')

    def _to_float(self, valor_str):
        """Converte strings financeiras do PT-BR para float calculável."""
        try:
            if not valor_str: return 0.0
            return float(valor_str.replace('.', '').replace(',', '.'))
        except:
            return 0.0

    def identificar_modelo(self, fonte):
        """
        Aceita um caminho (str) ou um objeto pdfplumber.PDF.
        Resolve o erro 'AttributeError: str object has no attribute pages'.
        """
        if isinstance(fonte, str):
            with pdfplumber.open(fonte) as pdf:
                return self._detectar_texto(pdf)
        else:
            return self._detectar_texto(fonte)

    def _detectar_texto(self, pdf):
        """Lógica interna de detecção de texto no topo do PDF."""
        primeira_pag = pdf.pages[0].extract_text() or ""
        topo = primeira_pag[:600].upper()
        
        if "ANALÍTICO DE TITULAR CONEXO" in topo:
            return "ANALITICO"
        elif "ANALÍTICO DE TITULAR AUTORAL" in topo:
            return "ANALITICO"
        elif "DEMONSTRATIVO DO TITULAR" in topo or "DISTRIBUIÇÃO" in topo:
            return "DISTRIBUICAO"
        return "DESCONHECIDO"

    def extrair_distribuicao(self, fonte):
        """Extração para modelo financeiro."""
        if isinstance(fonte, str):
            with pdfplumber.open(fonte) as pdf:
                return self._logica_distribuicao(pdf)
        else:
            return self._logica_distribuicao(fonte)

    def _logica_distribuicao(self, pdf):
        dados = []
        isrc_atual = "N/A"
        for page in pdf.pages:
            linhas = (page.extract_text() or "").split('\n')
            for linha in linhas:
                m_isrc = self.reg_isrc.search(linha)
                if m_isrc: 
                    isrc_atual = m_isrc.group(1)
                
                m_fin = self.reg_fin.search(linha)
                if m_fin:
                    dados.append({
                        "ISRC": isrc_atual,
                        "RUBRICA": m_fin.group(1).strip(),
                        "PERIODO": m_fin.group(2).strip(),
                        "VALOR_BRUTO": self._to_float(m_fin.group(3)),
                        "PARTICIPACAO_%": self._to_float(m_fin.group(4)),
                        "VALOR_RECEBIDO": self._to_float(m_fin.group(5)),
                        "TIPO_RELATORIO": "Distribuição Mensal"
                    })
        return pd.DataFrame(dados)

    def extrair_analitico(self, fonte):
        """Extração para modelo cadastral."""
        if isinstance(fonte, str):
            with pdfplumber.open(fonte) as pdf:
                return self._logica_analitico(pdf)
        else:
            return self._logica_analitico(fonte)

    def _logica_analitico(self, pdf):
        dados = []
        isrc_atual = ""
        for page in pdf.pages:
            linhas = (page.extract_text() or "").split('\n')
            for linha in linhas:
                m_obra = self.reg_obra_analitica.search(linha)
                if m_obra:
                    isrc_atual = m_obra.group(2)
                    continue
                
                m_part = re.search(r'(.*?)\s+([A-Z]{3,})\s+(\d+,\d+)$', linha)
                if m_part and isrc_atual:
                    dados.append({
                        "ISRC": isrc_atual,
                        "TITULAR": m_part.group(1).strip(),
                        "ASSOCIACAO": m_part.group(2),
                        "QUOTA_PARTE": self._to_float(m_part.group(3)),
                        "TIPO_RELATORIO": "Cadastro Conexo"
                    })
        return pd.DataFrame(dados)