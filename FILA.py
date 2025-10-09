import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Inicializa a lista de tarefas
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

st.title("📋 Sistema de Tarefas com Excel")

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
                "Nome": nome,
                "Telefone": telefone,
                "Descrição": descricao,
                "Status": "Pendente",
                "Data de Criação": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Data de Assumido": "",
                "Data de Encerrado": ""
            }
            st.session_state.tarefas.append(tarefa)
            st.success("✅ Tarefa adicionada!")
        else:
            st.warning("Preencha todos os campos!")

# --- Listagem de tarefas ---
st.subheader("📌 Tarefas Cadastradas")

for i, tarefa in enumerate(st.session_state.tarefas):
    st.markdown(f"**Técnico:** {tarefa['Nome']}  📞 {tarefa['Telefone']}")
    st.markdown(f"**Descrição:** {tarefa['Descrição']}")
    st.markdown(f"**Status:** {tarefa['Status']}")
    st.markdown(f"**Data de Criação:** {tarefa['Data de Criação']}")
    
    col1, col2 = st.columns(2)

    # Botão para assumir a tarefa
    with col1:
        if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
            if tarefa["Status"] == "Pendente":
                tarefa["Status"] = "Em andamento"
                tarefa["Data de Assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.success("Tarefa assumida!")
            else:
                st.warning("Tarefa já foi assumida ou encerrada.")

    # Botão para encerrar a tarefa
    with col2:
        if st.button("✅ Encerrar", key=f"encerrar_{i}"):
            if tarefa["Status"] != "Encerrada":
                tarefa["Status"] = "Encerrada"
                tarefa["Data de Encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.success("Tarefa encerrada!")
            else:
                st.warning("Tarefa já está encerrada.")

# --- Gerar Excel ---
def gerar_excel(tarefas):
    # Converte todos os valores para string para evitar erros
    tarefas_str = []
    for t in tarefas:
        tarefas_str.append({k: str(v) for k, v in t.items()})

    df = pd.DataFrame(tarefas_str)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tarefas")
    return output.getvalue()
