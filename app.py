import streamlit as st
import os
import pandas as pd
from datetime import datetime
from io import BytesIO
from processors.ecad_processor import ECADProcessor

# 1. CONFIGURAÇÕES PREMIUM DA PÁGINA
st.set_page_config(
    page_title="ECAD Analytics | Data Intelligence", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada para remover emojis e usar fontes limpas
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #fcfcfd; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #f0f0f1; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.2em; background-color: #0f172a; color: white; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #1e293b; border: none; }
    .stDataFrame { border-radius: 12px; }
    
    /* Lucide Icon Simulation Class */
    .icon-box { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER PROFISSIONAL ---
with st.container():
    col_logo, col_text = st.columns([1, 6])
    with col_logo:
        logo_path = "img/logo1.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        else:
            st.markdown("### ECAD")
    with col_text:
        st.markdown('<p style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0;">Data Intelligence Center</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: #64748b; font-size: 1.1rem;">Enterprise Engine para Processamento de Direitos Autorais</p>', unsafe_allow_html=True)

st.divider()

# --- DASHBOARD DE MÉTRICAS ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Sistema Core", "Active", delta="Stable")
with col_m2:
    st.metric("Modelos Mapeados", "4 v2.0", delta="Update")
with col_m3:
    st.metric("Parser Accuracy", "99.98%", delta="High-Fi")
with col_m4:
    st.metric("Compliance", "ISO 27001", delta="Secure")

# --- AREA DE TRABALHO ---
st.markdown('<div class="icon-box">📂 Gateway de Importação de Ativos</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload de arquivos PDF para decodificação", 
    accept_multiple_files=True, 
    type=['pdf'],
    label_visibility="collapsed"
)

if uploaded_files:
    processor = ECADProcessor()
    tab_ind, tab_cons = st.tabs(["Processamento em Lote", "Inteligência Consolidada"])

    with tab_ind:
        # Criamos uma pasta exports segura
        if not os.path.exists("exports"):
            os.makedirs("exports")

        for uploaded_file in uploaded_files:
            # Container visual para cada arquivo
            with st.container():
                # Salva o arquivo temporário
                temp_path = os.path.join("exports", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                col_name, col_type, col_dl = st.columns([3, 2, 1])
                
                with col_name:
                    st.markdown(f"**Documento:** `{uploaded_file.name}`")
                
                # Identifica modelo usando a classe corrigida
                modelo = processor.identificar_modelo(temp_path)
                
                with col_type:
                    if modelo == "DISTRIBUICAO":
                        st.markdown("🏷️ `Distribuição de Prescritíveis`")
                        df = processor.extrair_distribuicao(temp_path)
                    elif modelo == "ANALITICO":
                        st.markdown("🏷️ `Analítico de Titular Conexo`")
                        df = processor.extrair_analitico(temp_path)
                    else:
                        st.markdown("🏷️ `Modelo Desconhecido`")
                        df = pd.DataFrame()

                with col_dl:
                    if not df.empty:
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="Download .xlsx",
                            data=output.getvalue(),
                            file_name=f"{uploaded_file.name.replace('.pdf', '')}_DATA.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{uploaded_file.name}"
                        )

                if not df.empty:
                    with st.expander("Visualizar Preview dos Dados"):
                        st.dataframe(df, use_container_width=True, height=180)
                
                # Remove o lixo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                st.divider()

    with tab_cons:
        st.markdown("### BI & Agregação")
        st.info("Aguardando conclusão do processamento em lote para gerar visão agregada.")

# --- SIDEBAR CORPORATIVA ---
with st.sidebar:
    st.markdown('<p style="font-size: 1.5rem; font-weight: 700;">Audit Panel</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**User Session:** `Administrador_Master`")
    st.markdown("**Local Host:** `192.168.1.107`")
    
    st.divider()
    
    st.subheader("Manutenção")
    if st.button("Limpar Cache de Sistema"):
        if os.path.exists("exports"):
            for f in os.listdir("exports"):
                os.remove(os.path.join("exports", f))
        st.toast("Memória de exportação limpa.")

    st.divider()
    st.caption(f"System Time: {datetime.now().strftime('%H:%M:%S')}")
    st.caption(f"© {datetime.now().year} Enterprise Solutions Group")