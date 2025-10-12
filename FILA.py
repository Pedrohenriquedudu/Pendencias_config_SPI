import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import io
import numpy

st.set_page_config(page_title="Sistema de Tarefas B2B SPI", layout="wide")

# --------------------------
# Configuração
# --------------------------
ARQUIVO_TAREFAS = "tarefas.json"
PRAZO_PADRAO_DIAS = 3

USUARIOS = [
    {"usuario": "Pedro Martins", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Sergio Kohara", "senha": "Coordenador", "tipo": "admin"},
    {"usuario": "Sergio Alves", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Alberto Ferraz", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Madson Reis", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Silvana Terrivel", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Jessica Torres", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Gustavo Durão", "senha": "Analista", "tipo": "admin"},
    {"usuario": "Marcio Barreira", "senha": "Analista", "tipo": "admin"},
]

# --------------------------
# Funções auxiliares
# --------------------------

def validar_login(usuario, senha):
    """Verifica usuário e senha"""
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

def carregar_tarefas():
    """Carrega tarefas do arquivo JSON"""
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_tarefas(tarefas):
    """Salva tarefas no arquivo JSON"""
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=2)

def calcular_status(tarefa):
    """Atualiza status para atrasada se o prazo passar"""
    if tarefa["status"] == "Encerrada":
        return "Encerrada"
    data_criacao = datetime.strptime(tarefa["data_criacao"], "%d-%m-%Y %H:%M:%S")
    if datetime.now() - data_criacao > timedelta(days=PRAZO_PADRAO_DIAS):
        return "Atrasada"
    return tarefa["status"]

# --------------------------
# Sessão de login
# --------------------------
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# Tela de login
if not st.session_state.usuario_logado:
    st.title("🔐 Login no Sistema de Tarefas B2B SPI")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = validar_login(usuario, senha)
        if user:
            st.session_state.usuario_logado = user
            st.success(f"✅ Bem-vindo, {usuario}!")
            st.session_state.refresh = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# --------------------------
# Área principal
# --------------------------
usuario_atual = st.session_state.usuario_logado["usuario"]
tipo_usuario = st.session_state.usuario_logado["tipo"]

st.sidebar.title(f"👋 {usuario_atual}")
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.rerun()

st.title("📋 Sistema de Tarefas B2B SPI")

# Carrega as tarefas persistentes
tarefas = carregar_tarefas()


# --------------------------
# Adicionar nova tarefa
# --------------------------
st.subheader("➕ Adicionar Nova Tarefa")
with st.form("form_tarefa"):
    id_tarefa = st.text_input("ID da tarefa")
    nome = st.text_input("Nome do técnico responsável")
    telefone = st.text_input("Telefone do técnico")
    descricao = st.text_area("Descrição da tarefa")
    enviar = st.form_submit_button("Adicionar Tarefa")

    if enviar:
            
            if id_tarefa and nome and telefone and descricao:
                usuario_criador = st.session_state["usuario"]
                nova_tarefa = {
                "id": id_tarefa,
                "nome": nome,
                "telefone": telefone,
                "descricao": descricao,
                "status": "Pendente",
                "criado_por": usuario_criador,
                "data_criacao": (datetime.now() - timedelta(hours=3)).strftime("%d-%m-%Y %H:%M:%S"),
                "data_assumido": "",
                "data_encerrado": "",
                "assumido_por": "",
                "encerrado_por": "",
                }
                tarefas.append(nova_tarefa)
                salvar_tarefas(tarefas)
                st.session_state["tarefas"].append(nova)
                st.success(f"✅ Tarefa adicionada com sucesso!")
            else:
                st.warning("Por favor, preencha todos os campos.")

# --------------------------
# Lista de tarefas
# --------------------------
st.subheader("📌 Tarefas Atuais")

if not tarefas:
    st.info("Nenhuma tarefa cadastrada.")
else:
    for i, tarefa in enumerate(tarefas):
        cor_emoji = {
            "Pendente": "🟡",
            "Em andamento": "🔵",
            "Encerrada": "🟢",
            "Atrasada": "🔴"
        }.get(tarefa["status"], "⚪")

        with st.expander(f"{cor_emoji} {tarefa['descricao']}"):
            st.write(f"🆔 ID: {tarefa['id']} | ✍️ Criado por: {tarefa['criado_por']} em {tarefa['criado_em']}")
            st.write(f"👨‍🔧 Técnico: {tarefa['nome']}")
            st.write(f"📞 Telefone: {tarefa['telefone']}")
            st.write(f"📅 Criada em: {tarefa['data_criacao']}")
            st.write(f"📍 Status atual: **{tarefa['status']}**")
            if  tarefa.get("assumido_por"):
                st.write(f"👷 Assumido por: **{tarefa['assumido_por']}** em {tarefa['data_assumido']}")
            if tarefa.get("encerrado_por"):
                st.write(f"✅ Encerrado por: **{tarefa['encerrado_por']}** em {tarefa['data_encerrado']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                    if tarefa["status"] == "Pendente":
                        tarefa["status"] = "Em andamento"
                        tarefa["data_assumido"] = (datetime.now() - timedelta(hours=3)).strftime("%d-%m-%Y %H:%M:%S")
                        tarefa["assumido_por"] = usuario_atual
                        salvar_tarefas(tarefas)
                        st.success(f"✅ Tarefa assumida por {usuario_atual}!")
                        st.rerun()
                    else:
                        st.warning("Esta tarefa já foi assumida ou encerrada.")
            with col2:
                if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                    if tarefa["status"] != "Encerrada":
                        tarefa["status"] = "Encerrada"
                        tarefa["data_encerrado"] = (datetime.now() - timedelta(hours=3)).strftime("%d-%m-%Y %H:%M:%S")
                        tarefa["encerrado_por"] = usuario_atual
                        salvar_tarefas(tarefas)
                        st.success("🏁 Tarefa encerrada com sucesso por {usuario_atual}!")
                        st.rerun()
                    else:
                        st.warning("Esta tarefa já está encerrada.")


if tarefas:
    st.divider()
    st.subheader("📤 Exportar tarefas Excel")

    df_export = pd.DataFrame(tarefas)

    buffer = io.StringIO()
    df_export.to_csv(buffer, index=False, sep=",")
    csv_bytes = buffer.getvalue().encode("utf-8")  # bytes para download

    st.download_button(
        label="📥 Baixar tarefas em Excel",
        data=csv_bytes,
        file_name="tarefas_exportadas.csv",
        mime="text/csv"
    )


# --------------------------
# Botão do Admin
# --------------------------
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        tarefas = []
        salvar_tarefas(tarefas)
        st.warning("Todas as tarefas foram apagadas pelo Admin!")
        st.rerun()
