import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(page_title="Gestão de Tarefas SPI", layout="wide")

# --- Arquivos ---
ARQUIVO_CSV = "tarefas.csv"
USUARIOS_CSV = "usuarios.csv"

# --- Funções auxiliares ---
def carregar_tarefas():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV).to_dict(orient="records")
    return []

def salvar_tarefas(tarefas):
    pd.DataFrame(tarefas).to_csv(ARQUIVO_CSV, index=False)

def gerar_excel(tarefas):
    df = pd.DataFrame(tarefas)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tarefas")
    return output.getvalue()

def carregar_usuarios():
    if os.path.exists(USUARIOS_CSV):
        return pd.read_csv(USUARIOS_CSV).to_dict(orient="records")
    else:
        # Cria um admin padrão
        df = pd.DataFrame([{"usuario": "operador", "senha": "Regional_spi", "tipo": "admin"}])
        df.to_csv(USUARIOS_CSV, index=False)
        return df.to_dict(orient="records")

def salvar_usuarios(usuarios):
    pd.DataFrame(usuarios).to_csv(USUARIOS_CSV, index=False)

def validar_login(usuario, senha):
    for u in carregar_usuarios():
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

# --- Sessão ---
if "tarefas" not in st.session_state:
    st.session_state.tarefas = carregar_tarefas()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# --- Tela de Login ---
if not st.session_state.usuario_logado:
    st.title("🔐 Sistema de Gestão de Tarefas - Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user_data = validar_login(usuario, senha)
        if user_data:
            st.session_state.usuario_logado = user_data
            st.success(f"✅ Bem-vindo, {usuario}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.info("💡 Usuário padrão: **admin** / Senha: **1234**")
    st.stop()

# --- Após login ---
usuario_atual = st.session_state.usuario_logado["usuario"]
tipo_usuario = st.session_state.usuario_logado["tipo"]

st.sidebar.title("👋 Olá, " + usuario_atual)
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.experimental_rerun()

# --- Página principal ---
st.title("📋 Gestão de Tarefas")

# --- Opção Admin: Cadastrar novo usuário ---
if tipo_usuario == "admin":
    with st.expander("⚙️ Cadastro de novos usuários (somente Admin)"):
        st.write("Crie novos técnicos ou administradores para acessar o sistema.")

        usuarios = carregar_usuarios()
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Senha", type="password")
        tipo = st.selectbox("Tipo de usuário", ["tecnico", "admin"])
        if st.button("➕ Cadastrar usuário"):
            if novo_usuario and nova_senha:
                if any(u["usuario"] == novo_usuario for u in usuarios):
                    st.warning("⚠️ Este usuário já existe!")
                else:
                    usuarios.append({"usuario": novo_usuario, "senha": nova_senha, "tipo": tipo})
                    salvar_usuarios(usuarios)
                    st.success(f"✅ Usuário '{novo_usuario}' cadastrado com sucesso!")
            else:
                st.warning("Preencha todos os campos para cadastrar o usuário.")

# --- Layout principal ---
col1, col2 = st.columns([2, 1])

# --- Formulário nova tarefa ---
with col1:
    with st.form("nova_tarefa"):
        st.subheader("➕ Nova Tarefa")
        nome = st.text_input("Nome do técnico responsável pela criação")
        telefone = st.text_input("Telefone")
        descricao = st.text_area("Descrição da tarefa")
        submitted = st.form_submit_button("Adicionar")

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
                st.success("✅ Tarefa adicionada!")
            else:
                st.warning("Preencha todos os campos antes de adicionar.")

# --- Gráficos ---
with col2:
    st.subheader("📊 Indicadores")
    if len(st.session_state.tarefas) > 0:
        df = pd.DataFrame(st.session_state.tarefas)
        status_count = df["status"].value_counts()

        fig, ax = plt.subplots()
        ax.bar(status_count.index, status_count.values, color=["orange", "deepskyblue", "lightgreen"])
        ax.set_title("Distribuição por Status")
        st.pyplot(fig)

        # Produtividade
        prod_df = df[df["assumido_por"] != ""]
        if len(prod_df) > 0:
            assumidas = prod_df["assumido_por"].value_counts()
            encerradas = df[df["encerrado_por"] != ""]["encerrado_por"].value_counts()
            tecnicos = sorted(set(assumidas.index) | set(encerradas.index))

            fig2, ax2 = plt.subplots()
            ax2.bar(tecnicos, [assumidas.get(t, 0) for t in tecnicos], label="Assumidas", color="cornflowerblue")
            ax2.bar(tecnicos, [encerradas.get(t, 0) for t in tecnicos], label="Encerradas", color="lightgreen", alpha=0.7)
            ax2.legend()
            ax2.set_title("Produtividade por Técnico")
            plt.xticks(rotation=20)
            st.pyplot(fig2)
        else:
            st.info("Nenhuma tarefa assumida ainda.")
    else:
        st.info("Sem tarefas no momento.")

# --- Listagem ---
st.divider()
st.subheader("📌 Tarefas")

filtro = st.selectbox("Filtrar por status:", ["Todas", "Pendente", "Em andamento", "Encerrada"])
tarefas = st.session_state.tarefas
if filtro != "Todas":
    tarefas = [t for t in tarefas if t["status"] == filtro]

if not tarefas:
    st.info("Nenhuma tarefa encontrada.")
else:
    for i, tarefa in enumerate(tarefas):
        idx = st.session_state.tarefas.index(tarefa)
        with st.container(border=True):
            st.markdown(f"**Criada por:** {tarefa['nome_criador']}  📞 {tarefa['telefone']}")
            st.markdown(f"**Descrição:** {tarefa['descricao']}")
            st.markdown(f"**Status:** {tarefa['status']}")

            if tarefa["assumido_por"]:
                st.write(f"👷 Assumido por: {tarefa['assumido_por']} em {tarefa['data_assumido']}")
            if tarefa["encerrado_por"]:
                st.write(f"✅ Encerrado por: {tarefa['encerrado_por']} em {tarefa['data_encerrado']}")

            colA, colB, colC = st.columns(3)

            with colA:
                if st.button("🧑‍🔧 Assumir", key=f"assumir_{i}"):
                    if tarefa["status"] in ["Encerrada", "Em andamento"]:
                        st.warning("Tarefa já foi assumida ou encerrada.")
                    else:
                        tarefa["status"] = "Em andamento"
                        tarefa["assumido_por"] = usuario_atual
                        tarefa["data_assumido"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        st.session_state.tarefas[idx] = tarefa
                        salvar_tarefas(st.session_state.tarefas)
                        st.success("Tarefa assumida!")
                        st.experimental_rerun()

            with colB:
                if st.button("✅ Encerrar", key=f"encerrar_{i}"):
                    if tarefa["status"] == "Encerrada":
                        st.info("Tarefa já encerrada.")
                    else:
                        tarefa["status"] = "Encerrada"
                        tarefa["encerrado_por"] = usuario_atual
                        tarefa["data_encerrado"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        st.session_state.tarefas[idx] = tarefa
                        salvar_tarefas(st.session_state.tarefas)
                        st.success("Tarefa encerrada!")
                        st.experimental_rerun()

            with colC:
                if st.button("✏️ Editar", key=f"editar_{i}"):
                    with st.expander(f"Editar Tarefa {i+1}"):
                        novo_nome = st.text_input("Nome criador", tarefa["nome_criador"], key=f"edit_nome_{i}")
                        novo_tel = st.text_input("Telefone", tarefa["telefone"], key=f"edit_tel_{i}")
                        nova_desc = st.text_area("Descrição", tarefa["descricao"], key=f"edit_desc_{i}")
                        if st.button("💾 Salvar", key=f"salvar_edit_{i}"):
                            tarefa["nome_criador"] = novo_nome
                            tarefa["telefone"] = novo_tel
                            tarefa["descricao"] = nova_desc
                            st.session_state.tarefas[idx] = tarefa
                            salvar_tarefas(st.session_state.tarefas)
                            st.success("Tarefa atualizada!")
                            st.experimental_rerun()

# --- Exportar / limpar ---
st.divider()
if len(st.session_state.tarefas) > 0:
    excel = gerar_excel(st.session_state.tarefas)
    st.download_button(
        "📥 Baixar relatório Excel",
        excel,
        f"tarefas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if tipo_usuario == "admin":
    if st.button("🗑️ Limpar todas as tarefas"):
        st.session_state.tarefas = []
        salvar_tarefas([])
        st.warning("Todas as tarefas foram apagadas.")
