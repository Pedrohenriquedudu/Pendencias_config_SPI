import streamlit as st
import json
from datetime import datetime, timedelta
import os
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Sistema de Tarefas Profissional", layout="wide")

ARQUIVO_TAREFAS = "tarefas.json"

# --- Usuários ---
USUARIOS = [
    {"usuario": "admin", "senha": "1234", "tipo": "admin"},
    {"usuario": "tecnico1", "senha": "123", "tipo": "tecnico"},
    {"usuario": "tecnico2", "senha": "123", "tipo": "tecnico"}
]

# --- Funções ---
def validar_login(usuario, senha):
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r") as f:
            return json.load(f)
    return []

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, "w") as f:
        json.dump(tarefas, f, indent=4)

def gerar_excel(tarefas):
    df = pd.DataFrame(tarefas)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tarefas")
    return output.getvalue()

def tarefas_atrasadas(tarefa, dias_limite=3):
    data_criacao = datetime.strptime(tarefa['data_criacao'], "%d/%m/%Y %H:%M:%S")
    if tarefa['status'] != "Encerrada" and datetime.now() - data_criacao > timedelta(days=dias_limite):
        return True
    return False

# --- Sessão ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# --- Login ---
if not st.session_state.usuario_logado:
    st.title("🔐 Login")
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

# --- Tela principal ---
usuario_atual = st.session_state.usuario_logado["usuario"]
tipo_usuario = st.session_state.usuario_logado["tipo"]

st.sidebar.title(f"👋 Olá, {usuario_atual}")
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.experimental_rerun()

st.title("📋 Sistema de Tarefas Profissional")

# --- Carregar tarefas ---
tarefas = carregar_tarefas()

# --- Formulário nova tarefa ---
st.subheader("➕ Adicionar Nova Tarefa")
with st.form("form_tarefa"):
    nome = st.text_input("Nome do técnico")
    telefone = st.text_input("Telefone")
    descricao = st.text_area("Descrição da tarefa")
    submitted = st.form_submit_button("Adicionar tarefa")
    
    if submitted:
        if nome and telefone and descricao:
            tarefa = {
                "nome": nome,
                "telefone": telefone,
                "descricao": descricao,
                "status": "Pendente",
                "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "assumido_por": "",
                "data_assumido": "",
                "encerrado_por": "",
                "data_encerrado": ""
            }
            tarefas.append(tarefa)
            salvar_tarefas(tarefas)
            st.success("✅ Tarefa adicionada!")
            st.experimental_rerun()
            
         else:
            st.warning("Preencha todos os campos!")

# --- Filtro por status ---
status_filtro = st.selectbox("Filtrar tarefas por status:", ["Todas", "Pendente", "Em andamento", "Encerrada", "Atrasadas"])
if status_filtro == "Atrasadas":
    tarefas_filtradas = [t for t in tarefas if tarefas_atrasadas(t)]
elif status_filtro == "Todas":
    tarefas_filtradas = tarefas
else:
    tarefas_filtradas = [t for t in tarefas if t["status"] == status_filtro]


# --- Botão Admin apagar todas ---
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        tarefas = []
        salvar_tarefas(tarefas)
        st.warning("Todas as tarefas foram apagadas pelo Admin!")
        st.experimental_rerun()

# --- Botão download Excel ---
st.subheader("📥 Relatórios e Exportação")
if st.button("📄 Baixar todas as tarefas em Excel"):
    excel_bytes = gerar_excel(tarefas)
    st.download_button(
        label="Download Excel",
        data=excel_bytes,
        file_name=f"tarefas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


