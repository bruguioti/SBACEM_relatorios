import streamlit as st
import os
import pandas as pd
from processors.ecad_processor import ECADProcessor

# 1. Configurações iniciais da página
st.set_page_config(page_title="ECAD Data Converter", page_icon="📊", layout="wide")

# Garante que a pasta de exportação existe
if not os.path.exists("exports"):
    os.makedirs("exports")

# --- FRONT-END: LOGO E TÍTULO ---
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    # Caminho da imagem
    logo_path = "img/logo1.jpg"
    
    # Verifica se o arquivo existe para não dar erro de 'FileNotFound'
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        # Caso a imagem não exista, exibe um ícone padrão
        st.markdown("### 🏢 **ECAD**\n**CONVERTER**")

with col_titulo:
    st.title("Conversor Inteligente de Relatórios ECAD")
    st.markdown("Transforme PDFs complexos em planilhas editáveis instantaneamente.")

st.divider()

# --- ÁREA DE UPLOAD ---
st.subheader("📤 Carregar Arquivos")
uploaded_files = st.file_uploader(
    "Selecione os PDFs para conversão", 
    accept_multiple_files=True, 
    type=['pdf'],
    help="Você pode arrastar vários arquivos de uma vez."
)

if uploaded_files:
    processor = ECADProcessor()
    
    for uploaded_file in uploaded_files:
        # Salva temporariamente
        path = os.path.join("exports", uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Identifica o modelo
        modelo = processor.identificar_modelo(path)
        
        # --- IDENTIFICAÇÃO VISUAL DO MODELO ---
        with st.expander(f"🔍 Analisando: {uploaded_file.name}", expanded=True):
            
            # Mapeamento de nomes solicitado
            if modelo == "DISTRIBUICAO":
                nome_relatorio = "📄 1. Distribuição de Prescritíveis"
                cor_box = "blue"
            elif modelo == "ANALITICO":
                nome_relatorio = "📄 2. Relatório Analítico de Titular Conexo e suas Gravações"
                cor_box = "green"
            else:
                nome_relatorio = "⚠️ Modelo Desconhecido"
                cor_box = "orange"

            st.markdown(f"**Tipo de Relatório Identificado:** :{cor_box}[{nome_relatorio}]")

            # Processamento
            df = pd.DataFrame()
            
            with st.spinner(f"Extraindo dados de {uploaded_file.name}..."):
                if modelo == "ANALITICO":
                    df = processor.extrair_analitico(path)
                elif modelo == "DISTRIBUICAO":
                    df = processor.extrair_distribuicao(path)
            
            # Exibição e Download
            if not df.empty:
                st.success(f"Dados extraídos com sucesso!")
                st.dataframe(df, use_container_width=True, height=250)
                
                # Conversão para Excel
                excel_name = uploaded_file.name.replace(".pdf", ".xlsx")
                excel_path = os.path.join("exports", excel_name)
                df.to_excel(excel_path, index=False, engine='openpyxl')
                
                # Botão de Download
                with open(excel_path, "rb") as f_excel:
                    st.download_button(
                        label=f"💾 Baixar Planilha - {excel_name}",
                        data=f_excel,
                        file_name=excel_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"btn_{uploaded_file.name}"
                    )
            else:
                if modelo == "DESCONHECIDO":
                    st.warning("O sistema não conseguiu mapear os campos deste PDF.")
                else:
                    st.error("Erro ao processar o conteúdo do arquivo.")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    st.info("Este sistema automatiza a leitura de dados do ECAD.")
    
    if st.button("🗑️ Limpar Arquivos Temporários"):
        arquivos = os.listdir("exports")
        for f in arquivos:
            os.remove(os.path.join("exports", f))
        st.success(f"Limpeza concluída!")

    st.markdown("---")
    st.caption("v1.0.0 - Sistema Interno")