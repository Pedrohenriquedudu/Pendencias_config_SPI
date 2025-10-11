import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

# --- Configuração inicial ---
st.set_page_config(page_title="Gestão de Tarefas", layout="centered")

# --- Inicialização de dados persistentes ---
if "tarefas" not in st.session_state:
    st.session_state["tarefas"] = []

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# --- Função para ajustar horário ---
def agora_brasilia():
    return (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

# --- Função para login ---
def login():
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "123":
            st.session_state["usuario"] = "admin"
            st.success("Login de administrador realizado!")
            st.experimental_rerun()
        elif usuario:
            st.session_state["usuario"] = usuario
            st.success(f"Bem-vindo, {usuario}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos!")

# --- Tela principal ---
def app():
    st.title("📋 Sistema de Tarefas")

    usuario = st.session_state["usuario"]

    st.sidebar.write(f"👤 Usuário logado: **{usuario}**")
    if st.sidebar.button("Sair"):
        st.session_state["usuario"] = None
        st.experimental_rerun()

    # --- Adicionar nova tarefa ---
    st.subheader("➕ Adicionar nova tarefa")
    with st.form("form_tarefa"):
        nome_tecnico = st.text_input("Nome do técnico")
        telefone = st.text_input("Telefone do técnico")
        descricao = st.text_area("Descrição da tarefa")
        enviar = st.form_submit_button("Adicionar tarefa")

        if enviar:
            if nome_tecnico and telefone and descricao:
                nova = {
                    "técnico": nome_tecnico,
                    "telefone": telefone,
                    "descrição": descricao,
                    "status": "Pendente",
                    "criado_em": agora_brasilia(),
                    "assumido_por": "",
                    "assumido_em": "",
                    "encerrado_por": "",
                    "encerrado_em": ""
                }
                st.session_state["tarefas"].append(nova)
                st.success("✅ Tarefa adicionada com sucesso!")
            else:
                st.warning("Por favor, preencha todos os campos.")

    # --- Listar tarefas ---
    st.subheader("📋 Tarefas atuais")
    tarefas = st.session_state["tarefas"]

    if not tarefas:
        st.info("Nenhuma tarefa cadastrada ainda.")
    else:
        for i, tarefa in enumerate(tarefas):
            with st.expander(f"{tarefa['descrição']} — [{tarefa['status']}]"):
                st.write(f"👷 Técnico: {tarefa['técnico']}")
                st.write(f"📞 Telefone: {tarefa['telefone']}")
                st.write(f"🕒 Criada em: {tarefa['criado_em']}")
                if tarefa["assumido_por"]:
                    st.write(f"👤 Assumida por: {tarefa['assumido_por']} em {tarefa['assumido_em']}")
                if tarefa["encerrado_por"]:
                    st.write(f"✅ Encerrada por: {tarefa['encerrado_por']} em {tarefa['encerrado_em']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Assumir", key=f"assumir_{i}"):
                        if tarefa["status"] == "Pendente":
                            tarefa["status"] = "Em andamento"
                            tarefa["assumido_por"] = usuario
                            tarefa["assumido_em"] = agora_brasilia()
                            st.success("Tarefa assumida!")
                            st.experimental_rerun()
                        else:
                            st.warning("Esta tarefa já foi assumida.")
                with col2:
                    if st.button("Encerrar", key=f"encerrar_{i}"):
                        if tarefa["status"] != "Encerrada":
                            tarefa["status"] = "Encerrada"
                            tarefa["encerrado_por"] = usuario
                            tarefa["encerrado_em"] = agora_brasilia()
                            st.success("Tarefa encerrada!")
                            st.experimental_rerun()

    # --- Somente admin pode apagar todas ---
    if usuario == "admin" and tarefas:
        st.divider()
        if st.button("🗑️ Apagar todas as tarefas"):
            st.session_state["tarefas"] = []
            st.warning("Todas as tarefas foram apagadas.")
            st.experimental_rerun()

    # --- Exportar tarefas ---
    if tarefas:
        st.divider()
        st.subheader("📤 Exportar tarefas em Excel (.xlsx)")

        df_export = pd.DataFrame(tarefas)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Tarefas")
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar arquivo Excel",
            data=buffer,
            file_name="tarefas_exportadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Execução principal ---
if st.session_state["usuario"]:
    app()
else:
    login()
