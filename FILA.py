import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="Sistema de Tarefas Online", layout="wide")

ARQUIVO_TAREFAS = "tarefas.json"

# --- Usuários ---
USUARIOS = [
    {"usuario": "admin", "senha": "1234", "tipo": "admin"},
    {"usuario": "tecnico1", "senha": "123", "tipo": "tecnico"},
    {"usuario": "tecnico2", "senha": "123", "tipo": "tecnico"}
]

def validar_login(usuario, senha):
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

# --- Funções para tarefas ---
def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r") as f:
            return json.load(f)
    return []

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, "w") as f:
        json.dump(tarefas, f, indent=4)

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

st.title("📋 Sistema de Tarefas Online")

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
status_filtro = st.selectbox("Filtrar tarefas por status:", ["Todas", "Pendente", "Em andamento", "Encerrada"])
tarefas_filtradas = tarefas if status_filtro == "Todas" else [t for t in tarefas if t["status"] == status_filtro]

# --- Listagem de tarefas ---
st.subheader("📌 Tarefas Cadastradas")

if not tarefas_filtradas:
    st.info("Nenhuma tarefa encontrada para o filtro selecionado.")
else:
    for i, tarefa in enumerate(tarefas_filtradas):
        st.markdown(f"**Técnico:** {tarefa['nome']}  📞 {tarefa['telefone']}")
        st.markdown(f"**Descrição:** {tarefa['descricao']}")
        st.markdown(f"**Status:** {tarefa['status']}")
        st.markdown(f"**Criada em:** {tarefa['data_criacao']}")
        if tarefa["assumido_por"]:
            st.markdown(f"**Assumida por:** {tarefa['assumido_por']} em {tarefa['data_assumido']}")
        if tarefa["encerrado_por"]:
            st.markdown(f"**Encerrada por:** {tarefa['encerrado_por']} em {tarefa['data_encerrado']}")

        col1, col2 = st.columns(2)

        # Botão Assumir
        with col1:
            if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                if tarefa["status"] == "Pendente":
                    tarefa["status"] = "Em andamento"
                    tarefa["assumido_por"] = usuario_atual
                    tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    salvar_tarefas(tarefas)
                    st.success("Tarefa assumida!")
                    st.experimental_rerun()
                else:
                    st.warning("Tarefa já foi assumida ou encerrada.")

        # Botão Encerrar
        with col2:
            if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                if tarefa["status"] != "Encerrada":
                    tarefa["status"] = "Encerrada"
                    tarefa["encerrado_por"] = usuario_atual
                    tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    salvar_tarefas(tarefas)
                    st.success("Tarefa encerrada!")
                    st.experimental_rerun()
                else:
                    st.warning("Tarefa já está encerrada.")

# --- Botão Admin apagar todas ---
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        tarefas = []
        salvar_tarefas(tarefas)
        st.warning("Todas as tarefas foram apagadas pelo Admin!")
        st.experimental_rerun()

