import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Sistema de Tarefas Profissional", layout="wide")

# --- Configuração ---
ARQUIVO = "tarefas.csv"
PRAZO_PADRAO_DIAS = 3

# --- Usuários cadastrados ---
USUARIOS = [
    {"usuario": "admin", "senha": "1234", "tipo": "admin"},
    {"usuario": "tecnico1", "senha": "123", "tipo": "tecnico"},
    {"usuario": "tecnico2", "senha": "123", "tipo": "tecnico"},
]

# --- Função de login ---
def validar_login(usuario, senha):
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

# --- Carrega tarefas do CSV ---
def carregar_tarefas():
    if os.path.exists(ARQUIVO):
        return pd.read_csv(ARQUIVO)
    else:
        return pd.DataFrame(columns=["nome", "telefone", "descricao", "status", "data_criacao", "data_assumido", "data_encerrado"])

# --- Salva tarefas no CSV ---
def salvar_tarefas(df):
    df.to_csv(ARQUIVO, index=False)

# --- Verifica atraso ---
def calcular_status_completo(row):
    if row["status"] == "Encerrada":
        return "Encerrada"
    data_criacao = datetime.strptime(row["data_criacao"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() - data_criacao > timedelta(days=PRAZO_PADRAO_DIAS):
        return "Atrasada"
    return row["status"]

# --- Sessão ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# --- Login ---
if not st.session_state.usuario_logado:
    st.title("🔐 Login no Sistema de Tarefas")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = validar_login(usuario, senha)
        if user:
            st.session_state.usuario_logado = user
            st.success(f"✅ Bem-vindo, {usuario}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# --- Dados do usuário logado ---
usuario_atual = st.session_state.usuario_logado["usuario"]
tipo_usuario = st.session_state.usuario_logado["tipo"]

st.sidebar.title(f"👋 {usuario_atual}")
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.experimental_rerun()

st.title("📋 Sistema de Tarefas Profissional")

# --- Carregar tarefas ---
tarefas_df = carregar_tarefas()

# --- Adicionar tarefa ---
st.subheader("➕ Nova Tarefa")
with st.form("form_tarefa"):
    nome = st.text_input("Nome do técnico")
    telefone = st.text_input("Telefone")
    descricao = st.text_area("Descrição da tarefa")
    if st.form_submit_button("Adicionar tarefa"):
        if nome and telefone and descricao:
            nova = pd.DataFrame([{
                "nome": nome,
                "telefone": telefone,
                "descricao": descricao,
                "status": "Pendente",
                "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_assumido": "",
                "data_encerrado": ""
            }])
            tarefas_df = pd.concat([tarefas_df, nova], ignore_index=True)
            salvar_tarefas(tarefas_df)
            st.success("✅ Tarefa adicionada!")
        else:
            st.warning("Preencha todos os campos.")

# --- Atualizar status (atrasadas) ---
tarefas_df["status"] = tarefas_df.apply(calcular_status_completo, axis=1)
salvar_tarefas(tarefas_df)

# --- Exibir tarefas ---
st.subheader("📌 Lista de Tarefas")

if tarefas_df.empty:
    st.info("Nenhuma tarefa cadastrada.")
else:
    for i, row in tarefas_df.iterrows():
        cor = {
            "Pendente": "⚠️",
            "Em andamento": "🔵",
            "Encerrada": "✅",
            "Atrasada": "🔴"
        }.get(row["status"], "📝")

        st.markdown(f"### {cor} {row['descricao']}")
        st.write(f"👨‍🔧 Técnico: {row['nome']} | 📞 {row['telefone']}")
        st.write(f"📅 Criada em: {row['data_criacao']}")
        st.write(f"📍 Status: **{row['status']}**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                if row["status"] == "Pendente":
                    tarefas_df.at[i, "status"] = "Em andamento"
                    tarefas_df.at[i, "data_assumido"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    salvar_tarefas(tarefas_df)
                    st.toast("🧑‍🔧 Tarefa assumida!")
                    st.experimental_rerun()
                else:
                    st.warning("Tarefa já assumida ou encerrada.")
        with col2:
            if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                if row["status"] != "Encerrada":
                    tarefas_df.at[i, "status"] = "Encerrada"
                    tarefas_df.at[i, "data_encerrado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    salvar_tarefas(tarefas_df)
                    st.toast("✅ Tarefa encerrada!")
                    st.experimental_rerun()
                else:
                    st.warning("Tarefa já está encerrada.")

# --- Apagar todas (somente admin) ---
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        tarefas_df = tarefas_df.iloc[0:0]
        salvar_tarefas(tarefas_df)
        st.warning("Todas as tarefas foram apagadas pelo Admin!")
        st.experimental_rerun()

# --- Relatório semanal ---
st.divider()
st.subheader("📊 Relatório Semanal por Técnico")

if not tarefas_df.empty:
    tarefas_df["data_criacao"] = pd.to_datetime(tarefas_df["data_criacao"], errors="coerce")
    semana_atual = datetime.now().isocalendar()[1]
    relatorio = tarefas_df[tarefas_df["data_criacao"].dt.isocalendar().week == semana_atual]
    relatorio = relatorio[relatorio["status"] == "Encerrada"]
    resumo = relatorio.groupby("nome").size().reset_index(name="Tarefas Encerradas")
    st.dataframe(resumo)

    # Download Excel
    if not resumo.empty:
        resumo.to_excel("relatorio_semana.xlsx", index=False)
        with open("relatorio_semana.xlsx", "rb") as f:
            st.download_button(
                label="📥 Baixar relatório em Excel",
                data=f,
                file_name="relatorio_semana.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
