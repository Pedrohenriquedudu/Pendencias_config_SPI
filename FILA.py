import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import io

st.set_page_config(page_title="Gestão de Tarefas", layout="wide")

ARQUIVO_TAREFAS = "tarefas.json"
FUSO_HORARIO_HORAS = 3  # subtrair 3 horas -> UTC-3

# usuários de exemplo
USUARIOS = [
    {"usuario": "admin", "senha": "123", "tipo": "admin"},
    {"usuario": "tecnico1", "senha": "123", "tipo": "tecnico"},
    {"usuario": "tecnico2", "senha": "123", "tipo": "tecnico"},
]

# ------------------------
# helpers: I/O e horário
# ------------------------
def agora_brasilia():
    return (datetime.now() - timedelta(hours=FUSO_HORARIO_HORAS)).strftime("%Y-%m-%d %H:%M:%S")

def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        try:
            with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=2)

def validar_login(usuario, senha):
    for u in USUARIOS:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

def gerar_id_automatico(tarefas):
    # Gera ID no formato T001, T002, ... verificando os já existentes
    max_n = 0
    for t in tarefas:
        tid = t.get("id", "")
        if isinstance(tid, str) and tid.upper().startswith("T"):
            try:
                n = int(tid[1:])
                if n > max_n:
                    max_n = n
            except:
                pass
    return f"T{(max_n + 1):03d}"

# ------------------------
# session_state inicial
# ------------------------
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ------------------------
# Tela de login
# ------------------------
def tela_login():
    st.title("🔐 Login")
    col1, col2 = st.columns([2,1])
    with col1:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
    with col2:
        st.write("**Usuários de teste:**")
        st.write("- admin / 123 (admin)")
        st.write("- tecnico1 / 123")
        st.write("- tecnico2 / 123")

    if st.button("Entrar"):
        u = validar_login(usuario, senha)
        if u:
            st.session_state["usuario"] = u["usuario"]
            st.session_state["tipo_usuario"] = u["tipo"]
            st.success(f"Bem-vindo, {u['usuario']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

if not st.session_state["usuario"]:
    tela_login()
    st.stop()

# ------------------------
# App principal
# ------------------------
usuario_atual = st.session_state["usuario"]
tipo_usuario = st.session_state.get("tipo_usuario", "tecnico")

st.sidebar.markdown(f"**Usuário:** {usuario_atual}")
if st.sidebar.button("Sair"):
    st.session_state["usuario"] = None
    st.session_state["tipo_usuario"] = None
    st.rerun()

st.title("📋 Gestão de Tarefas")

# carrega tarefas do disco (compartilhadas entre todas as sessões)
tarefas = carregar_tarefas()

# ------------------------
# Formulário: nova tarefa
# ------------------------
st.subheader("➕ Adicionar nova tarefa")
with st.form("form_add"):
    id_input = st.text_input("ID da tarefa (deixe em branco para gerar automaticamente)")
    tecnico_input = st.text_input("Nome do técnico")
    telefone_input = st.text_input("Telefone do técnico")
    descricao_input = st.text_area("Descrição da tarefa")
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        if not tecnico_input or not telefone_input or not descricao_input:
            st.warning("Preencha nome, telefone e descrição.")
        else:
            # gerar id se vazio
            if not id_input:
                id_novo = gerar_id_automatico(tarefas)
            else:
                id_novo = id_input
                # checar duplicidade
                if any(t.get("id") == id_novo for t in tarefas):
                    st.error(f"ID {id_novo} já existe. Escolha outro.")
                    st.stop()

            nova = {
                "id": id_novo,
                "técnico": tecnico_input,
                "telefone": telefone_input,
                "descrição": descricao_input,
                "status": "Pendente",
                "criado_por": usuario_atual,
                "criado_em": agora_brasilia(),
                "assumido_por": "",
                "assumido_em": "",
                "encerrado_por": "",
                "encerrado_em": ""
            }
            tarefas.append(nova)
            salvar_tarefas(tarefas)
            st.success(f"Tarefa {id_novo} criada por {usuario_atual}.")
            st.rerun()

# ------------------------
# Lista de tarefas
# ------------------------
st.subheader("📋 Tarefas atuais")

if not tarefas:
    st.info("Nenhuma tarefa cadastrada.")
else:
    # opção de filtro
    filtro = st.selectbox("Filtrar por status:", ["Todas", "Pendente", "Em andamento", "Encerrada", "Atrasadas"])
    # calcular atrasadas (padrão 3 dias)
    def is_atrasada(t):
        try:
            criado = datetime.strptime(t["criado_em"], "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - timedelta(hours=FUSO_HORARIO_HORAS) - criado) > timedelta(days=3) and t["status"] != "Encerrada"
        except Exception:
            return False

    tarefas_mostradas = []
    for t in tarefas:
        status_calc = "Atrasada" if is_atrasada(t) else t["status"]
        t["_status_calc"] = status_calc
        if filtro == "Todas" or filtro == status_calc:
            tarefas_mostradas.append(t)

    for t in tarefas_mostradas:
        header = f"{t['id']} — {t['descrição']}  [{t['_status_calc']}]"
        with st.expander(header):
            st.write(f"🆔 ID: **{t['id']}**")
            st.write(f"✍️ Criado por: **{t['criado_por']}** em {t['criado_em']}")
            st.write(f"👷 Técnico: {t['técnico']} | 📞 {t['telefone']}")
            st.write(f"📍 Status: **{t['_status_calc']}**")
            if t.get("assumido_por"):
                st.write(f"👤 Assumida por: **{t['assumido_por']}** em {t['assumido_em']}")
            if t.get("encerrado_por"):
                st.write(f"✅ Encerrada por: **{t['encerrado_por']}** em {t['encerrado_em']}")

            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("Assumir", key=f"assumir_{t['id']}"):
                    # localizar tarefa no array principal por id
                    for tt in tarefas:
                        if tt["id"] == t["id"]:
                            if tt["status"] == "Pendente":
                                tt["status"] = "Em andamento"
                                tt["assumido_por"] = usuario_atual
                                tt["assumido_em"] = agora_brasilia()
                                salvar_tarefas(tarefas)
                                st.success(f"Tarefa {tt['id']} assumida por {usuario_atual}.")
                                st.rerun()
                            else:
                                st.warning("Tarefa já assumida ou encerrada.")
                            break
            with col2:
                if st.button("Encerrar", key=f"encerrar_{t['id']}"):
                    for tt in tarefas:
                        if tt["id"] == t["id"]:
                            if tt["status"] != "Encerrada":
                                tt["status"] = "Encerrada"
                                tt["encerrado_por"] = usuario_atual
                                tt["encerrado_em"] = agora_brasilia()
                                salvar_tarefas(tarefas)
                                st.success(f"Tarefa {tt['id']} encerrada por {usuario_atual}.")
                                st.rerun()
                            else:
                                st.warning("Tarefa já encerrada.")
                            break

# ------------------------
# Apagar todas (admin)
# ------------------------
if tipo_usuario == "admin":
    st.divider()
    if st.button("🗑️ Apagar todas as tarefas"):
        tarefas = []
        salvar_tarefas(tarefas)
        st.success("Todas as tarefas foram apagadas pelo Admin.")
        st.rerun()

# ------------------------
# Exportar XLSX
# ------------------------
if tarefas:
    st.divider()
    st.subheader("📤 Exportar tarefas em Excel (.xlsx)")
    df_export = pd.DataFrame(tarefas)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Tarefas")
    buffer.seek(0)
    st.download_button(
        label="📥 Baixar tarefas (XLSX)",
        data=buffer.getvalue(),
        file_name="tarefas_exportadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
