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

# --- Listagem de tarefas com cores avançadas ---
st.subheader("📌 Tarefas Cadastradas")

if not tarefas_filtradas:
    st.info("Nenhuma tarefa encontrada para o filtro selecionado.")
else:
    for i, tarefa in enumerate(tarefas_filtradas):
        # Definir cor de fundo baseado no status
        if tarefa['status'] == "Pendente":
            cor = "#FFFACD"
        elif tarefa['status'] == "Em andamento":
            cor = "#ADD8E6"
        elif tarefa['status'] == "Encerrada":
            cor = "#90EE90"
        elif tarefas_atrasadas(tarefa):
            cor = "#FF7F7F"  # vermelho para atrasadas

        with st.container():
            st.markdown(
                f"<div style='background-color:{cor}; padding:10px; border-radius:8px'>"
                f"**Técnico:** {tarefa['nome']}  📞 {tarefa['telefone']}<br>"
                f"**Descrição:** {tarefa['descricao']}<br>"
                f"**Status:** {tarefa['status']}<br>"
                f"**Criada em:** {tarefa['data_criacao']}<br>"
                f"{'**Assumida por:** ' + tarefa['assumido_por'] + ' em ' + tarefa['data_assumido'] if tarefa['assumido_por'] else ''}<br>"
                f"{'**Encerrada por:** ' + tarefa['encerrado_por'] + ' em ' + tarefa['data_encerrado'] if tarefa['encerrado_por'] else ''}"
                f"</div>",
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)
            # Assumir
            with col1:
                if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                    if tarefa["status"] == "Pendente":
                        tarefa["status"] = "Em andamento"
                        tarefa["assumido_por"] = usuario_atual
                        tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        salvar_tarefas(tarefas)
                        st.toast("Tarefa assumida com sucesso!", icon="✅")
                        st.experimental_rerun()
                    else:
                        st.warning("Tarefa já foi assumida ou encerrada.")

            # Encerrar
            with col2:
                if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                    if tarefa["status"] != "Encerrada":
                        tarefa["status"] = "Encerrada"
                        tarefa["encerrado_por"] = usuario_atual
                        tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        salvar_tarefas(tarefas)
                        st.toast("Tarefa encerrada com sucesso!", icon="✅")
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

# --- Gráficos profissionais ---
st.subheader("📊 Painel de Produtividade")

if tarefas:
    df = pd.DataFrame(tarefas)

    # Status das tarefas
    status_count = df['status'].value_counts().reset_index()
    status_count.columns = ['Status', 'Quantidade']
    fig_status = px.pie(status_count, names='Status', values='Quantidade', title='Distribuição por Status')
    st.plotly_chart(fig_status, use_container_width=True)

    # Tarefas encerradas por técnico
    encerradas = df[df['status']=='Encerrada']
    if not encerradas.empty:
        encerradas_count = encerradas['encerrado_por'].value_counts().reset_index()
        encerradas_count.columns = ['Técnico', 'Tarefas Encerradas']
        fig_tecnico = px.bar(encerradas_count, x='Técnico', y='Tarefas Encerradas', 
                             title='Tarefas encerradas por técnico', text='Tarefas Encerradas')
        st.plotly_chart(fig_tecnico, use_container_width=True)

    # Tarefas atrasadas por técnico
    atrasadas = df[df.apply(tarefas_atrasadas, axis=1)]
    if not atrasadas.empty:
        atrasadas_count = atrasadas['nome'].value_counts().reset_index()
        atrasadas_count.columns = ['Técnico', 'Tarefas Atrasadas']
        fig_atrasadas = px.bar(atrasadas_count, x='Técnico', y='Tarefas Atrasadas',
                               title='Tarefas atrasadas por técnico', text='Tarefas Atrasadas', color='Tarefas Atrasadas')
        st.plotly_chart(fig_atrasadas, use_container_width=True)

