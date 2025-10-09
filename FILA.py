import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Sistema de Tarefas", layout="wide")

# --- Usuários ---
USUARIOS = [
    {"usuario": "Pedrinho", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Super", "senha": "Gestão_Campo", "tipo": "tecnico"},
    {"usuario": "Super", "senha": "Gestão_Campo", "tipo": "tecnico"}
]

def validar_login(usuario, senha):
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

# --- Sessão ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

# --- Tela de Login ---
if not st.session_state.usuario_logado:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = validar_login(usuario, senha)
        if user:
            st.session_state.usuario_logado = user
            st.success(f"✅ Bem-vindo, {usuario}!")
            
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

st.title("📋 Sistema de Tarefas")

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
                "data_assumido": "",
                "data_encerrado": ""
            }
            st.session_state.tarefas.append(tarefa)
            st.success("✅ Tarefa adicionada!")
        else:
            st.warning("Preencha todos os campos!")

# --- Listagem de tarefas ---
st.subheader("📌 Tarefas Cadastradas")

if not st.session_state.tarefas:
    st.info("Nenhuma tarefa cadastrada.")
else:
    for i, tarefa in enumerate(st.session_state.tarefas):
        st.markdown(f"**Técnico:** {tarefa['nome']}  📞 {tarefa['telefone']}")
        st.markdown(f"**Descrição:** {tarefa['descricao']}")
        st.markdown(f"**Status:** {tarefa['status']}")
        st.markdown(f"**Data de Criação:** {tarefa['data_criacao']}")
        
        col1, col2 = st.columns(2)

        # Assumir
        with col1:
            if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                if tarefa["status"] == "Pendente":
                    tarefa["status"] = "Em andamento"
                    tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    st.success("Tarefa assumida!")
                else:
                    st.warning("Tarefa já foi assumida ou encerrada.")

        # Encerrar
        with col2:
            if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                if tarefa["status"] != "Encerrada":
                    tarefa["status"] = "Encerrada"
                    tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    st.success("Tarefa encerrada!")
                else:
                    st.warning("Tarefa já está encerrada.")

# --- Botão Admin para apagar todas as tarefas ---
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        st.session_state.tarefas = []
        st.warning("Todas as tarefas foram apagadas pelo Admin!")

