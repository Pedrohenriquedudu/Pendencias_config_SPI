import streamlit as st
from datetime import datetime

# Inicializa a lista de tarefas
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

st.title("📋 Sistema de Tarefas")

# --- Formulário para adicionar tarefa ---
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

for i, tarefa in enumerate(st.session_state.tarefas):
    st.markdown(f"**Técnico:** {tarefa['nome']}  📞 {tarefa['telefone']}")
    st.markdown(f"**Descrição:** {tarefa['descricao']}")
    st.markdown(f"**Status:** {tarefa['status']}")
    st.markdown(f"**Data de criação:** {tarefa['data_criacao']}")
    
    col1, col2 = st.columns(2)

    # Botão para assumir a tarefa
    with col1:
        if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
            if tarefa["status"] == "Pendente":
                tarefa["status"] = "Em andamento"
                tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.success("Tarefa assumida!")
            else:
                st.warning("Tarefa já foi assumida ou encerrada.")

    # Botão para encerrar a tarefa
    with col2:
        if st.button("✅ Encerrar", key=f"encerrar_{i}"):
            if tarefa["status"] != "Encerrada":
                tarefa["status"] = "Encerrada"
                tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.success("Tarefa encerrada!")
            else:
                st.warning("Tarefa já está encerrada.")
