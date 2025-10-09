import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Tarefas", layout="centered")

# --- Inicializar banco de dados em memória ---
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

st.title("📋 Sistema de Gestão de Tarefas")

# --- Formulário para adicionar tarefa ---
with st.form("nova_tarefa"):
    st.subheader("Adicionar nova tarefa")
    nome = st.text_input("Nome do técnico")
    telefone = st.text_input("Telefone")
    descricao = st.text_area("Descrição da tarefa")
    submitted = st.form_submit_button("➕ Adicionar Tarefa")

    if submitted:
        if nome and telefone and descricao:
            nova_tarefa = {
                "nome": nome,
                "telefone": telefone,
                "descricao": descricao,
                "status": "Pendente"
            }
            st.session_state.tarefas.append(nova_tarefa)
            st.success("Tarefa adicionada com sucesso!")
        else:
            st.warning("Preencha todos os campos antes de adicionar.")

# --- Exibir tarefas cadastradas ---
st.divider()
st.subheader("📌 Tarefas Cadastradas")

if len(st.session_state.tarefas) == 0:
    st.info("Nenhuma tarefa cadastrada ainda.")
else:
    for i, tarefa in enumerate(st.session_state.tarefas):
        with st.container(border=True):
            st.write(f"**Técnico:** {tarefa['nome']}")
            st.write(f"**Telefone:** {tarefa['telefone']}")
            st.write(f"**Descrição:** {tarefa['descricao']}")
            st.write(f"**Status:** {tarefa['status']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                    st.session_state.tarefas[i]["status"] = "Em andamento"
                    st.experimental_rerun()
            with col2:
                if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                    st.session_state.tarefas[i]["status"] = "Encerrada"
                    st.experimental_rerun()
