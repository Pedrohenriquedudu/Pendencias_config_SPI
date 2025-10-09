import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Gestão de Tarefas", layout="centered")

ARQUIVO_CSV = "tarefas.csv"

# --- Funções auxiliares ---
def carregar_tarefas():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV).to_dict(orient="records")
    return []

def salvar_tarefas(tarefas):
    df = pd.DataFrame(tarefas)
    df.to_csv(ARQUIVO_CSV, index=False)

# --- Inicializar tarefas ---
if "tarefas" not in st.session_state:
    st.session_state.tarefas = carregar_tarefas()

st.title("📋 Sistema de Gestão de Tarefas")

# --- Formulário para adicionar tarefa ---
with st.form("nova_tarefa"):
    st.subheader("Adicionar nova tarefa")
    nome = st.text_input("Nome do técnico responsável pela criação")
    telefone = st.text_input("Telefone")
    descricao = st.text_area("Descrição da tarefa")
    submitted = st.form_submit_button("➕ Adicionar Tarefa")

    if submitted:
        if nome and telefone and descricao:
            nova_tarefa = {
                "nome_criador": nome,
                "telefone": telefone,
                "descricao": descricao,
                "status": "Pendente",
                "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "assumido_por": "",
                "data_assumido": "",
                "encerrado_por": "",
                "data_encerrado": ""
            }
            st.session_state.tarefas.append(nova_tarefa)
            salvar_tarefas(st.session_state.tarefas)
            st.success("✅ Tarefa adicionada com sucesso!")
        else:
            st.warning("⚠️ Preencha todos os campos antes de adicionar.")

# --- Filtro de visualização ---
st.divider()
st.subheader("📌 Tarefas Cadastradas")

opcoes_status = ["Todas", "Pendente", "Em andamento", "Encerrada"]
filtro = st.selectbox("Filtrar por status:", opcoes_status)

# --- Filtrar tarefas ---
if filtro != "Todas":
    tarefas_filtradas = [t for t in st.session_state.tarefas if t["status"] == filtro]
else:
    tarefas_filtradas = st.session_state.tarefas

# --- Exibir tarefas ---
if len(tarefas_filtradas) == 0:
    st.info("Nenhuma tarefa encontrada para este filtro.")
else:
    for i, tarefa in enumerate(tarefas_filtradas):
        with st.container(border=True):
            st.write(f"**Criada por:** {tarefa['nome_criador']}  📞 {tarefa['telefone']}")
            st.write(f"**Descrição:** {tarefa['descricao']}")
            st.write(f"**Status:** {tarefa['status']}")
            st.write(f"**Data de criação:** {tarefa['data_criacao']}")

            if tarefa["assumido_por"]:
                st.write(f"**Assumido por:** {tarefa['assumido_por']} em {tarefa['data_assumido']}")
            if tarefa["encerrado_por"]:
                st.write(f"**Encerrado por:** {tarefa['encerrado_por']} em {tarefa['data_encerrado']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}_{tarefa['descricao']}"):
                    if tarefa["status"] == "Encerrada":
                        st.warning("Esta tarefa já foi encerrada.")
                    elif tarefa["status"] == "Em andamento":
                        st.info("Esta tarefa já foi assumida.")
                    else:
                        tecnico = st.text_input(
                            f"Digite seu nome para assumir a tarefa {i+1}:",
                            key=f"input_assumir_{i}"
                        )
                        if tecnico:
                            tarefa["status"] = "Em andamento"
                            tarefa["assumido_por"] = tecnico
                            tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            salvar_tarefas(st.session_state.tarefas)
                            st.success(f"Tarefa assumida por {tecnico}")
                            st.experimental_rerun()

            with col2:
                if st.button("✅ Encerrar", key=f"encerrar_{i}_{tarefa['descricao']}"):
                    if tarefa["status"] == "Encerrada":
                        st.info("Esta tarefa já foi encerrada.")
                    else:
                        tecnico_encerrar = st.text_input(
                            f"Digite seu nome para encerrar a tarefa {i+1}:",
                            key=f"input_encerrar_{i}"
                        )
                        if tecnico_encerrar:
                            tarefa["status"] = "Encerrada"
                            tarefa["encerrado_por"] = tecnico_encerrar
                            tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            salvar_tarefas(st.session_state.tarefas)
                            st.success(f"Tarefa encerrada por {tecnico_encerrar}")
                            st.experimental_rerun()

# --- Botão para limpar todas as tarefas ---
st.divider()
if st.button("🗑️ Limpar todas as tarefas"):
    st.session_state.tarefas = []
    salvar_tarefas([])
    st.warning("Todas as tarefas foram removidas.")
