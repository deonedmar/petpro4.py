import streamlit as st
import pandas as pd
import hashlib
import requests
from datetime import datetime, date

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Pet & Taxi Pro",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  SUPABASE — conexão via API REST (sem PostgreSQL direto)
# ══════════════════════════════════════════════════════════════════════════════
SUPA_URL = st.secrets.get("SUPABASE_URL", "https://adhwhugtnexfuhgnlzte.supabase.co")
SUPA_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkaHdodWd0bmV4ZnVoZ25senRlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODI1Njc3MCwiZXhwIjoyMDkzODMyNzcwfQ.wamY1K5PyN2EU0rqtHvX2ow1RrYQiNSedV4e7GL1fis")

HEADERS = {
    "apikey":        SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}


def sb_get(tabela, filtros="", order=""):
    """Lê registros de uma tabela."""
    url = f"{SUPA_URL}/rest/v1/{tabela}?select=*"
    if filtros: url += f"&{filtros}"
    if order:   url += f"&order={order}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    return pd.DataFrame()


def sb_post(tabela, dados):
    """Insere um registro e retorna o id."""
    url = f"{SUPA_URL}/rest/v1/{tabela}"
    r = requests.post(url, headers=HEADERS, json=dados, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0].get("id")
    return None


def sb_patch(tabela, filtro, dados):
    """Atualiza registros."""
    url = f"{SUPA_URL}/rest/v1/{tabela}?{filtro}"
    r = requests.patch(url, headers=HEADERS, json=dados, timeout=15)
    return r.status_code in (200, 204)


def sb_delete(tabela, filtro):
    """Deleta registros."""
    url = f"{SUPA_URL}/rest/v1/{tabela}?{filtro}"
    r = requests.delete(url, headers=HEADERS, timeout=15)
    return r.status_code in (200, 204)


def sb_upsert(tabela, dados, conflict):
    """Insere ou atualiza (upsert)."""
    url = f"{SUPA_URL}/rest/v1/{tabela}"
    hdrs = {**HEADERS, "Prefer": f"resolution=merge-duplicates,return=representation"}
    r = requests.post(url, headers=hdrs, json=dados, timeout=15,
                      params={"on_conflict": conflict})
    return r.status_code in (200, 201)


# ══════════════════════════════════════════════════════════════════════════════
#  ESTILOS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; font-weight: 800; }

.login-wrap { max-width:420px; margin:60px auto 0 auto; background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:40px 44px; box-shadow:0 8px 32px rgba(0,0,0,.08); }
.login-logo  { text-align:center; font-size:3.2rem; margin-bottom:6px; }
.login-title { text-align:center; font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; color:#0f172a; margin-bottom:4px; }
.login-sub   { text-align:center; font-size:.85rem; color:#94a3b8; margin-bottom:28px; }

[data-testid="stSidebar"] { background:#0f172a !important; border-right:1px solid #1e293b; }
[data-testid="stSidebar"] * { color:#cbd5e1 !important; }
[data-testid="stSidebar"] .stRadio label { padding:10px 14px; border-radius:8px; margin-bottom:4px; display:block; transition:background .2s; }
[data-testid="stSidebar"] .stRadio label:hover { background:#1e293b; }

[data-testid="metric-container"] { background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:20px !important; box-shadow:0 1px 3px rgba(0,0,0,.06); }
[data-testid="stMetricValue"] { font-family:'Syne',sans-serif !important; font-size:2rem !important; }

.stButton > button[kind="primary"] { background:#0f172a !important; color:white !important; border:none !important; border-radius:10px !important; font-family:'Syne',sans-serif !important; font-weight:700 !important; padding:10px 24px !important; transition:opacity .2s !important; }
.stButton > button[kind="primary"]:hover { opacity:.85 !important; }

.pet-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:18px 22px; margin-bottom:12px; box-shadow:0 1px 4px rgba(0,0,0,.05); }
.cliente-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:16px 20px; margin-bottom:10px; }
.user-card  { background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.preco-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px; margin-bottom:6px; }

.badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:.78rem; font-weight:700; font-family:'Syne',sans-serif; letter-spacing:.03em; }
.badge-admin { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:12px; font-size:.75rem; font-weight:700; }
.badge-func  { background:#eff6ff; color:#1e40af; padding:3px 10px; border-radius:12px; font-size:.75rem; font-weight:700; }

.legenda-wrap { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 18px 0; }
.legenda-item { display:flex; align-items:center; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:5px 12px; font-size:.8rem; }
.legenda-dot  { width:10px; height:10px; border-radius:50%; display:inline-block; flex-shrink:0; }

.info-box { background:#f0f9ff; border-left:4px solid #0ea5e9; border-radius:0 10px 10px 0; padding:14px 18px; margin:10px 0; }
.warn-box { background:#fffbeb; border-left:4px solid #f59e0b; border-radius:0 10px 10px 0; padding:14px 18px; margin:10px 0; }

.stExpander { border:1px solid #e2e8f0 !important; border-radius:12px !important; }
div[data-testid="stForm"] { border:none !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
def _hash(s): return hashlib.sha256(s.encode()).hexdigest()


def autenticar(login, senha):
    login_fmt = login.strip().lower()
    hash_senha = _hash(senha)
    # Busca só pelo login primeiro
    df_login = sb_get("usuarios", f"login=eq.{login_fmt}&ativo=eq.1")
    if df_login.empty:
        st.error(f"🔍 Debug: usuário '{login_fmt}' não encontrado ou inativo.")
        return None
    # Verifica hash
    hash_db = df_login.iloc[0]["senha_hash"]
    if hash_db != hash_senha:
        st.error(f"🔍 Debug: hash incorreto. Esperado: {hash_senha[:20]}... Banco: {hash_db[:20]}...")
        return None
    return df_login.iloc[0].to_dict()


def tela_login():
    st.markdown("""
    <style>
        [data-testid="stSidebar"]        { display:none !important; }
        [data-testid="collapsedControl"] { display:none !important; }
    </style>
    <div class='login-wrap'>
        <div class='login-logo'>🐾</div>
        <div class='login-title'>Pet & Taxi Pro</div>
        <div class='login-sub'>Faça login para continuar</div>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("form_login"):
            login = st.text_input("👤 Usuário", placeholder="seu_usuario")
            senha = st.text_input("🔒 Senha",   type="password", placeholder="••••••••")
            if st.form_submit_button("Entrar →", type="primary", use_container_width=True):
                u = autenticar(login, senha)
                if u:
                    st.session_state["usuario"] = u
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def horario_livre(data_str, horario):
    df = sb_get("agendamentos", f"data=eq.{data_str}&horario=eq.{horario}")
    return len(df) < 3


def upsert_cliente(tutor, pet, endereco):
    # tenta buscar existente
    df = sb_get("clientes", f"tutor=eq.{tutor}&pet=eq.{pet}")
    if df.empty:
        sb_post("clientes", {"tutor": tutor, "pet": pet,
                              "ultimo_endereco": endereco, "total_servicos": 1})
    else:
        cid = int(df.iloc[0]["id"])
        total = int(df.iloc[0]["total_servicos"]) + 1
        sb_patch("clientes", f"id=eq.{cid}",
                 {"ultimo_endereco": endereco, "total_servicos": total})


def get_precos():
    df = sb_get("precos", "tipo=eq.servico", "id")
    return dict(zip(df["nome"], df["valor"])) if not df.empty else {}


def get_taxas():
    df = sb_get("precos", "tipo=eq.logistica", "id")
    return dict(zip(df["nome"], df["valor"])) if not df.empty else {}


def get_precos_df():  return sb_get("precos", "tipo=eq.servico",   "id")
def get_taxas_df():   return sb_get("precos", "tipo=eq.logistica",  "id")


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES FIXAS
# ══════════════════════════════════════════════════════════════════════════════
HORARIOS      = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]
STATUS_BALCAO = ["Agendado","Aguardando","Em Banho","Secando","Pronto","Finalizado"]
STATUS_TAXI   = ["Agendado","A Caminho","Pet Coletado","Na Loja","Serviço Concluído","Retornando","Finalizado"]
COR_STATUS = {
    "Agendado":          ("#6B7280","#F3F4F6"),
    "Aguardando":        ("#D97706","#FFFBEB"),
    "Em Banho":          ("#2563EB","#EFF6FF"),
    "Secando":           ("#7C3AED","#F5F3FF"),
    "A Caminho":         ("#D97706","#FFFBEB"),
    "Pet Coletado":      ("#0891B2","#ECFEFF"),
    "Na Loja":           ("#7C3AED","#F5F3FF"),
    "Serviço Concluído": ("#059669","#ECFDF5"),
    "Retornando":        ("#EA580C","#FFF7ED"),
    "Pronto":            ("#059669","#ECFDF5"),
    "Finalizado":        ("#1F2937","#F9FAFB"),
}

def badge(s):
    t,b = COR_STATUS.get(s,("#6B7280","#F3F4F6"))
    return f"<span class='badge' style='color:{t};background:{b}'>{s}</span>"

def legenda_status(lista):
    itens = "".join(
        f"<div class='legenda-item'><span class='legenda-dot' style='background:{COR_STATUS.get(s,('#6B7280','#F3F4F6'))[0]}'></span><span style='color:#374151'>{s}</span></div>"
        for s in lista
    )
    return f"<div class='legenda-wrap'>{itens}</div>"


# ══════════════════════════════════════════════════════════════════════════════
#  VERIFICAR LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if "usuario" not in st.session_state:
    tela_login()

usuario_atual = st.session_state["usuario"]
is_admin      = usuario_atual["perfil"] == "admin"
HOJE          = str(date.today())


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
        <div style='font-size:3rem'>🐾</div>
        <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.3rem;color:#f1f5f9'>Pet & Taxi Pro</div>
        <div style='font-size:.78rem;color:#64748b;margin-top:4px'>Sistema de Gestão</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    opcoes = ["📊  Dashboard","📝  Novo Agendamento","🏠  Atendimento Balcão",
              "🚐  Logística Taxi Dog","👥  Base de Clientes","💲  Preços e Serviços"]
    if is_admin: opcoes.append("🔐  Usuários")
    pagina = st.radio("", opcoes, label_visibility="collapsed")
    st.markdown("---")

    ph = "<span class='badge-admin'>Admin</span>" if is_admin else "<span class='badge-func'>Funcionário</span>"
    st.markdown(f"<div style='font-size:.82rem;color:#94a3b8;padding:0 4px'>👤 <b style='color:#cbd5e1'>{usuario_atual['nome']}</b><br>{ph}</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True):
        del st.session_state["usuario"]; st.rerun()
    st.markdown("---")
    st.markdown(f"<div style='font-size:.8rem;color:#475569;text-align:center'>📅 {datetime.today().strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  1. DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in pagina:
    st.markdown("## 📊 Painel de Operações")

    df_hoje = sb_get("agendamentos", f"data=eq.{HOJE}", "horario")
    df_mes  = sb_get("agendamentos", f"data=like.{HOJE[:7]}*&status=eq.Finalizado")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("🗓 Agendamentos Hoje", len(df_hoje))
    c2.metric("🚐 Com Transporte",   len(df_hoje[df_hoje["logistica"]!="Sem Transporte"]) if not df_hoje.empty else 0)
    c3.metric("✅ Finalizados Hoje", len(df_hoje[df_hoje["status"]=="Finalizado"]) if not df_hoje.empty else 0)
    c4.metric("💰 Faturamento Hoje", f"R$ {df_hoje['valor'].sum():.2f}" if not df_hoje.empty else "R$ 0,00")
    c5.metric("📈 Faturamento Mês",  f"R$ {df_mes['valor'].sum():.2f}"  if not df_mes.empty  else "R$ 0,00")
    st.divider()

    if df_hoje.empty:
        st.markdown("<div class='info-box'>🐾 Nenhum agendamento para hoje. Use <b>Novo Agendamento</b> para começar!</div>", unsafe_allow_html=True)
    else:
        hora_agora = datetime.now().strftime("%H:%M")
        atrasados  = df_hoje[(df_hoje["horario"]<hora_agora)&(~df_hoje["status"].isin(["Finalizado"]))]
        if not atrasados.empty:
            st.markdown(f"<div class='warn-box'>⚠️ <b>{len(atrasados)} pet(s)</b> com horário passado ainda não finalizados!</div>", unsafe_allow_html=True)

        col_esq, col_dir = st.columns([3,2])
        with col_esq:
            st.markdown("### 📋 Fila do Dia")
            for _, r in df_hoje.iterrows():
                atrasado = r["horario"]<hora_agora and r["status"] not in ["Finalizado"]
                cor_hora = "#EF4444" if atrasado else "#0f172a"
                st.markdown(f"""
                <div class='pet-card'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <div>
                            <span style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:{cor_hora}'>{r['horario']}</span>
                            <span style='margin-left:12px;font-weight:600;font-size:1.05rem'>🐾 {r['pet']}</span>
                            <span style='color:#64748b;margin-left:8px'>· {r['tutor']}</span>
                        </div>
                        {badge(r['status'])}
                    </div>
                    <div style='margin-top:8px;color:#475569;font-size:.9rem'>
                        ✂️ {r['servico']} &nbsp;·&nbsp; 🚐 {r['logistica']} &nbsp;·&nbsp; 💰 R$ {float(r['valor']):.2f}
                    </div>
                </div>""", unsafe_allow_html=True)
        with col_dir:
            st.markdown("### 📊 Serviços de Hoje")
            cont = df_hoje["servico"].value_counts().reset_index()
            cont.columns = ["Serviço","Qtd"]
            st.bar_chart(cont.set_index("Serviço"), height=200)
            st.markdown("### 🚐 Rotas Ativas")
            taxi_ativo = df_hoje[(df_hoje["logistica"]!="Sem Transporte")&(~df_hoje["status"].isin(["Finalizado"]))]
            if taxi_ativo.empty:
                st.caption("Nenhuma rota ativa agora.")
            else:
                for _, r in taxi_ativo.iterrows():
                    st.markdown(f"<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:10px 14px;margin-bottom:8px'><b>{r['pet']}</b> — {r['horario']}<br><span style='font-size:.85rem;color:#64748b'>{r['logistica']}</span> &nbsp; {badge(r['status'])}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  2. NOVO AGENDAMENTO
# ══════════════════════════════════════════════════════════════════════════════
elif "Agendamento" in pagina:
    st.markdown("## 📝 Novo Agendamento")
    st.divider()
    PRECOS = get_precos(); TAXAS = get_taxas()

    with st.expander("🔍 Buscar cliente já cadastrado (opcional)"):
        busca_rapida = st.text_input("Digite nome do tutor ou pet")
        if busca_rapida:
            res = sb_get("clientes", f"or=(tutor.ilike.*{busca_rapida}*,pet.ilike.*{busca_rapida}*)")
            if not res.empty:
                for _, cli in res.head(5).iterrows():
                    label = f"📋 {cli['tutor']} — {cli['pet']}"
                    if cli["ultimo_endereco"]: label += f"  ({cli['ultimo_endereco']})"
                    if st.button(label, key=f"sel_{cli['id']}"):
                        st.session_state["pf_tutor"]    = cli["tutor"]
                        st.session_state["pf_pet"]      = cli["pet"]
                        st.session_state["pf_endereco"] = cli["ultimo_endereco"]
                        st.rerun()
            else:
                st.caption("Nenhum cliente encontrado.")

    def ss(k,d=""): return st.session_state.get(k,d)

    with st.form("form_agendamento", clear_on_submit=False):
        st.markdown("#### 👤 Dados do Cliente")
        c1,c2 = st.columns(2)
        tutor = c1.text_input("Nome do Tutor *", value=ss("pf_tutor"))
        pet   = c2.text_input("Nome do Pet *",   value=ss("pf_pet"))

        st.markdown("#### ✂️ Serviço")
        c3,c4,c5 = st.columns(3)
        servico = c3.selectbox("Serviço *", list(PRECOS.keys()))
        data    = c4.date_input("Data *", min_value=date.today())
        horario = c5.selectbox("Horário *", HORARIOS)

        st.markdown("#### 🚐 Transporte")
        logistica = st.radio("Transporte", list(TAXAS.keys()), horizontal=True)
        endereco  = st.text_input("Endereço Completo", value=ss("pf_endereco"),
                                  placeholder="Rua, número, bairro, cidade",
                                  disabled=(logistica=="Sem Transporte"))

        valor = PRECOS.get(servico,0) + TAXAS.get(logistica,0)
        taxa  = TAXAS.get(logistica,0)
        st.markdown(f"""
        <div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 20px;margin:10px 0'>
            💰 <b>Valor estimado:</b>
            <span style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#15803d'>R$ {valor:.2f}</span>
            <span style='color:#64748b;font-size:.85rem'>&nbsp;(Serviço: R$ {PRECOS.get(servico,0):.2f}{f" + Transporte: R$ {taxa:.2f}" if taxa>0 else ""})</span>
        </div>""", unsafe_allow_html=True)

        st.text_area("📝 Observações (opcional)", height=70, placeholder="Comportamento, raça, alergias...")
        submitted = st.form_submit_button("✅ Confirmar Agendamento", type="primary", use_container_width=True)

    if submitted:
        erros = []
        tutor = tutor.strip().title(); pet = pet.strip().title()
        if not tutor: erros.append("Nome do tutor é obrigatório.")
        if not pet:   erros.append("Nome do pet é obrigatório.")
        if logistica != "Sem Transporte" and not endereco.strip():
            erros.append("Endereço obrigatório para serviço com transporte.")
        data_str = str(data)
        if not horario_livre(data_str, horario):
            erros.append(f"Horário {horario} está cheio para esta data (máx. 3 pets).")

        if erros:
            for e in erros: st.error(f"❌ {e}")
        else:
            novo_id = sb_post("agendamentos", {
                "tutor": tutor, "pet": pet, "servico": servico,
                "data": data_str, "horario": horario, "logistica": logistica,
                "endereco": endereco.strip(), "status": "Agendado", "valor": valor
            })
            upsert_cliente(tutor, pet, endereco.strip())
            sb_post("historico", {"tutor": tutor, "pet": pet,
                                   "servico": servico, "data": data_str, "valor": valor})
            for k in ["pf_tutor","pf_pet","pf_endereco"]: st.session_state.pop(k,None)
            st.success(f"✅ Agendamento #{novo_id} criado! {pet} agendado para {data.strftime('%d/%m/%Y')} às {horario}.")
            st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
#  3. ATENDIMENTO BALCÃO
# ══════════════════════════════════════════════════════════════════════════════
elif "Balcão" in pagina:
    st.markdown("## 🏠 Atendimento Balcão")
    st.markdown("**Legenda de Status:**")
    st.markdown(legenda_status(STATUS_BALCAO), unsafe_allow_html=True)
    st.divider()

    data_sel = st.date_input("📅 Ver agenda do dia", value=date.today())
    df_all    = sb_get("agendamentos", f"data=eq.{data_sel}", "horario")
    df_balcao = df_all[df_all["logistica"]=="Sem Transporte"] if not df_all.empty else pd.DataFrame()

    if df_balcao.empty:
        st.markdown(f"<div class='info-box'>Nenhum pet de balcão para {data_sel.strftime('%d/%m/%Y')}.</div>", unsafe_allow_html=True)
    else:
        total=len(df_balcao); fin=len(df_balcao[df_balcao["status"]=="Finalizado"])
        st.progress(fin/total if total>0 else 0, text=f"✅ {fin} de {total} pets finalizados")
        st.divider()
        for _, r in df_balcao.iterrows():
            with st.container():
                c1,c2,c3 = st.columns([3,3,2])
                with c1:
                    st.markdown(f"""
                    <div style='margin-bottom:4px'>
                        <span style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800'>{r['horario']}</span>
                        &nbsp; <b>{r['pet']}</b> <span style='color:#94a3b8'>· {r['tutor']}</span>
                    </div>
                    <div style='color:#475569;font-size:.9rem'>✂️ {r['servico']} &nbsp;·&nbsp; 💰 R$ {float(r['valor']):.2f}</div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(badge(r["status"]), unsafe_allow_html=True)
                    idx  = STATUS_BALCAO.index(r["status"]) if r["status"] in STATUS_BALCAO else 0
                    novo = st.selectbox("Status", STATUS_BALCAO, index=idx, key=f"bal_{r['id']}", label_visibility="collapsed")
                with c3:
                    if st.button("💾 Salvar", key=f"save_bal_{r['id']}", type="primary"):
                        sb_patch("agendamentos", f"id=eq.{int(r['id'])}", {"status": novo})
                        st.success("Atualizado!"); st.rerun()
                st.divider()


# ══════════════════════════════════════════════════════════════════════════════
#  4. LOGÍSTICA TAXI DOG
# ══════════════════════════════════════════════════════════════════════════════
elif "Taxi" in pagina:
    st.markdown("## 🚐 Logística Taxi Dog")
    st.markdown("**Legenda de Status:**")
    st.markdown(legenda_status(STATUS_TAXI), unsafe_allow_html=True)
    st.divider()

    data_sel = st.date_input("📅 Ver rotas do dia", value=date.today())
    df_taxi  = sb_get("agendamentos", f"data=eq.{data_sel}&logistica=neq.Sem Transporte", "horario")

    if df_taxi.empty:
        st.markdown(f"<div class='info-box'>Sem rotas de Taxi Dog para {data_sel.strftime('%d/%m/%Y')}.</div>", unsafe_allow_html=True)
    else:
        c1,c2,c3,c4 = st.columns(4)
        em_rota   = len(df_taxi[df_taxi["status"].isin(["A Caminho","Retornando"])])
        na_loja   = len(df_taxi[df_taxi["status"].isin(["Na Loja","Pet Coletado","Serviço Concluído"])])
        concluido = len(df_taxi[df_taxi["status"]=="Finalizado"])
        c1.metric("Total de Rotas",len(df_taxi)); c2.metric("🚗 Em Trânsito",em_rota)
        c3.metric("🏪 Na Loja",na_loja); c4.metric("✅ Concluídos",concluido)
        st.divider()

        for _, r in df_taxi.iterrows():
            fin = r["status"]=="Finalizado"
            with st.expander(f"{'✅' if fin else '📍'}  {r['horario']}  —  {r['pet']}  ({r['logistica']})", expanded=not fin):
                col_info, col_acao = st.columns([3,2])
                with col_info:
                    st.markdown(f"""
                    <div class='pet-card'>
                        <div style='font-size:1.1rem;font-weight:700;margin-bottom:8px'>🐾 {r['pet']} <span style='color:#94a3b8;font-weight:400'>· {r['tutor']}</span></div>
                        <div style='color:#475569;line-height:1.9;font-size:.92rem'>
                            ✂️ <b>Serviço:</b> {r['servico']}<br>🚐 <b>Transporte:</b> {r['logistica']}<br>
                            📍 <b>Endereço:</b> {r['endereco'] or '—'}<br>💰 <b>Valor:</b> R$ {float(r['valor']):.2f}
                        </div>
                        <div style='margin-top:12px'>{badge(r['status'])}</div>
                    </div>""", unsafe_allow_html=True)
                    if r["endereco"]:
                        enc = str(r["endereco"]).replace(" ","+")
                        b1,b2 = st.columns(2)
                        b1.link_button("🗺️ Google Maps", f"https://www.google.com/maps/search/?api=1&query={enc}", use_container_width=True)
                        b2.link_button("🔵 Waze", f"https://waze.com/ul?q={enc}", use_container_width=True)
                with col_acao:
                    st.markdown("**Atualizar progresso:**")
                    idx = STATUS_TAXI.index(r["status"]) if r["status"] in STATUS_TAXI else 0
                    novo = st.select_slider("Status", options=STATUS_TAXI, value=STATUS_TAXI[idx], key=f"taxi_{r['id']}", label_visibility="collapsed")
                    if st.button("💾 Salvar Status", key=f"save_taxi_{r['id']}", type="primary", use_container_width=True):
                        sb_patch("agendamentos", f"id=eq.{int(r['id'])}", {"status": novo})
                        st.success("Status atualizado!"); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  5. BASE DE CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
elif "Clientes" in pagina:
    st.markdown("## 👥 Base de Clientes")
    st.divider()

    aba1, aba2 = st.tabs(["📋 Clientes Cadastrados","➕ Cadastrar Manualmente"])

    with aba1:
        col_b, col_o = st.columns([3,1])
        busca = col_b.text_input("🔍 Buscar por tutor ou pet", placeholder="Digite para filtrar...")
        ordem = col_o.selectbox("Ordenar por", ["Tutor A-Z","Mais Serviços"])

        if busca.strip():
            df_cli = sb_get("clientes", f"or=(tutor.ilike.*{busca.strip()}*,pet.ilike.*{busca.strip()}*)")
        else:
            df_cli = sb_get("clientes")

        if not df_cli.empty:
            df_cli = df_cli.sort_values("total_servicos" if ordem=="Mais Serviços" else "tutor",
                                        ascending=(ordem!="Mais Serviços"))

        if df_cli.empty:
            st.info("Nenhum cliente encontrado.")
        else:
            cc1,cc2 = st.columns(2)
            cc1.metric("Total de Clientes", len(df_cli))
            cc2.metric("Total de Serviços", int(df_cli["total_servicos"].sum()))
            st.divider()

            for _, cli in df_cli.iterrows():
                cid = int(cli["id"])
                st.markdown(f"""
                <div class='cliente-card'>
                    <div style='font-size:1.05rem;font-weight:700'>🐾 {cli['pet']}
                        <span style='color:#64748b;font-weight:400;margin-left:6px'>· {cli['tutor']}</span>
                    </div>
                    <div style='font-size:.85rem;color:#64748b;margin-top:4px'>
                        📍 {cli['ultimo_endereco'] or '—'} &nbsp;·&nbsp;
                        📞 {cli.get('telefone','') or '—'} &nbsp;·&nbsp;
                        🔁 <b>{cli['total_servicos']}</b> serviços
                    </div>
                </div>""", unsafe_allow_html=True)

                col_hist, col_edit, col_del = st.columns([3,2,1])
                with col_hist:
                    with st.expander(f"📜 Histórico de {cli['pet']}"):
                        hist = sb_get("historico", f"tutor=eq.{cli['tutor']}&pet=eq.{cli['pet']}", "data.desc")
                        if hist.empty:
                            st.caption("Nenhum serviço no histórico.")
                        else:
                            st.markdown(f"💰 **Total gasto:** R$ {hist['valor'].sum():.2f}")
                            st.dataframe(hist[["servico","data","valor"]].rename(columns={"servico":"Serviço","data":"Data","valor":"Valor (R$)"}), use_container_width=True, hide_index=True)

                with col_edit:
                    with st.expander("✏️ Editar dados"):
                        with st.form(f"form_edit_{cid}", clear_on_submit=False):
                            e_tutor = st.text_input("Tutor",    value=cli["tutor"],                key=f"et_{cid}")
                            e_pet   = st.text_input("Pet",      value=cli["pet"],                  key=f"ep_{cid}")
                            e_end   = st.text_input("Endereço", value=cli["ultimo_endereco"] or "", key=f"ee_{cid}")
                            e_tel   = st.text_input("Telefone", value=cli.get("telefone","") or "", key=f"etel_{cid}")
                            if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                                e_tutor=e_tutor.strip().title(); e_pet=e_pet.strip().title()
                                if e_tutor and e_pet:
                                    sb_patch("clientes", f"id=eq.{cid}",
                                             {"tutor":e_tutor,"pet":e_pet,"ultimo_endereco":e_end.strip(),"telefone":e_tel.strip()})
                                    st.success("✅ Atualizado!"); st.rerun()
                                else:
                                    st.error("Tutor e Pet são obrigatórios.")

                with col_del:
                    with st.expander("🗑️ Excluir"):
                        st.warning(f"Excluir **{cli['pet']}** ({cli['tutor']}) e todo o histórico?\n\n**Ação irreversível.**")
                        chk = st.checkbox("Confirmo", key=f"chk_{cid}")
                        if st.button("🗑️ Excluir", key=f"del_{cid}", type="primary"):
                            if chk:
                                sb_delete("clientes", f"id=eq.{cid}")
                                sb_delete("historico", f"tutor=eq.{cli['tutor']}&pet=eq.{cli['pet']}")
                                st.success("Excluído."); st.rerun()
                            else:
                                st.error("Marque a caixa de confirmação.")
                st.divider()

    with aba2:
        with st.form("form_cliente_manual", clear_on_submit=True):
            st.markdown("#### Dados do Cliente")
            mc1,mc2 = st.columns(2)
            n_tutor = mc1.text_input("Nome do Tutor *")
            n_pet   = mc2.text_input("Nome do Pet *")
            n_end   = st.text_input("Endereço Padrão")
            n_tel   = st.text_input("Telefone / WhatsApp")
            if st.form_submit_button("✅ Cadastrar Cliente", type="primary"):
                n_tutor=n_tutor.strip().title(); n_pet=n_pet.strip().title()
                if n_tutor and n_pet:
                    df_exist = sb_get("clientes", f"tutor=eq.{n_tutor}&pet=eq.{n_pet}")
                    if df_exist.empty:
                        sb_post("clientes", {"tutor":n_tutor,"pet":n_pet,"ultimo_endereco":n_end.strip(),"telefone":n_tel.strip(),"total_servicos":0})
                        st.success(f"✅ {n_pet} ({n_tutor}) cadastrado!"); st.rerun()
                    else:
                        st.warning("⚠️ Pet já cadastrado para este tutor.")
                else:
                    st.error("Preencha nome do tutor e do pet.")


# ══════════════════════════════════════════════════════════════════════════════
#  6. PREÇOS E SERVIÇOS
# ══════════════════════════════════════════════════════════════════════════════
elif "Preços" in pagina:
    st.markdown("## 💲 Preços e Serviços")
    st.caption("Alterações aqui refletem imediatamente nos novos agendamentos.")
    st.divider()

    df_srv = get_precos_df(); df_tax = get_taxas_df()
    PRECOS = dict(zip(df_srv["nome"], df_srv["valor"])) if not df_srv.empty else {}
    TAXAS  = dict(zip(df_tax["nome"], df_tax["valor"])) if not df_tax.empty else {}

    aba_srv, aba_tax, aba_novo = st.tabs(["✂️ Serviços","🚐 Taxas de Transporte","➕ Adicionar Novo"])

    with aba_srv:
        st.markdown("### Tabela de Serviços"); st.divider()
        for _, row in df_srv.iterrows():
            nome=row["nome"]; pv=float(row["valor"]); desc=str(row.get("descricao","") or "")
            st.markdown(f"<div class='preco-card'><span style='font-weight:700'>✂️ {nome}</span> &nbsp;<span style='color:#64748b;font-size:.85rem'>Atual: R$ {pv:.2f}</span>{'<br><span style=\"font-size:.82rem;color:#94a3b8;font-style:italic\">' + desc + '</span>' if desc else ''}</div>", unsafe_allow_html=True)
            ec1,ec2,ec3 = st.columns([2,3,1])
            nv = ec1.number_input("Valor (R$)", min_value=0.0, value=pv, step=5.0, format="%.2f", key=f"srv_val_{nome}")
            nd = ec2.text_input("Descrição", value=desc, placeholder="Breve descrição...", key=f"srv_desc_{nome}")
            ec3.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
            if ec3.button("💾", key=f"save_srv_{nome}", help=f"Salvar {nome}"):
                sb_patch("precos", f"nome=eq.{nome}", {"valor":nv,"descricao":nd})
                st.success(f"✅ {nome} → R$ {nv:.2f}"); st.rerun()
            st.divider()
        with st.expander("🗑️ Remover um serviço"):
            srv_rem = st.selectbox("Selecione", list(PRECOS.keys()), key="rem_srv")
            if st.button("🗑️ Confirmar Remoção", type="primary", key="btn_rem_srv"):
                if len(PRECOS)<=1: st.error("Deve existir ao menos 1 serviço.")
                else: sb_delete("precos",f"nome=eq.{srv_rem}"); st.success(f"'{srv_rem}' removido."); st.rerun()

    with aba_tax:
        st.markdown("### Taxas de Transporte"); st.divider()
        for _, row in df_tax.iterrows():
            nome=row["nome"]; tv=float(row["valor"]); desc=str(row.get("descricao","") or "")
            st.markdown(f"<div class='preco-card'><span style='font-weight:700'>🚐 {nome}</span> &nbsp;<span style='color:#64748b;font-size:.85rem'>Atual: R$ {tv:.2f}</span>{'<br><span style=\"font-size:.82rem;color:#94a3b8;font-style:italic\">' + desc + '</span>' if desc else ''}</div>", unsafe_allow_html=True)
            tc1,tc2,tc3 = st.columns([2,3,1])
            nt = tc1.number_input("Taxa (R$)", min_value=0.0, value=tv, step=5.0, format="%.2f", key=f"tax_val_{nome}")
            nd = tc2.text_input("Descrição", value=desc, placeholder="Ex: Buscamos e entregamos...", key=f"tax_desc_{nome}")
            tc3.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
            if tc3.button("💾", key=f"save_tax_{nome}", help=f"Salvar {nome}"):
                sb_patch("precos", f"nome=eq.{nome}", {"valor":nt,"descricao":nd})
                st.success(f"✅ {nome} → R$ {nt:.2f}"); st.rerun()
            st.divider()
        with st.expander("🗑️ Remover opção de transporte"):
            tax_rem = st.selectbox("Selecione", list(TAXAS.keys()), key="rem_tax")
            if st.button("🗑️ Confirmar Remoção", type="primary", key="btn_rem_tax"):
                if tax_rem=="Sem Transporte": st.error("'Sem Transporte' não pode ser removido.")
                elif len(TAXAS)<=1: st.error("Deve existir ao menos 1 opção.")
                else: sb_delete("precos",f"nome=eq.{tax_rem}"); st.success(f"'{tax_rem}' removido."); st.rerun()

    with aba_novo:
        st.markdown("### Adicionar Novo Item"); st.divider()
        tipo_novo = st.radio("Tipo", ["✂️ Novo Serviço","🚐 Nova Opção de Transporte"], horizontal=True)
        with st.form("form_novo_item", clear_on_submit=True):
            nn1,nn2 = st.columns(2)
            novo_nome  = nn1.text_input("Nome *", placeholder="Ex: Tosa Express...")
            novo_valor = nn2.number_input("Valor (R$) *", min_value=0.0, step=5.0, format="%.2f")
            nova_desc  = st.text_input("Descrição", placeholder="Breve descrição...")
            if st.form_submit_button("✅ Adicionar", type="primary"):
                nome_fmt = novo_nome.strip().title()
                if not nome_fmt: st.error("Digite um nome.")
                else:
                    tipo_db = "servico" if "Serviço" in tipo_novo else "logistica"
                    sb_post("precos", {"tipo":tipo_db,"nome":nome_fmt,"valor":novo_valor,"descricao":nova_desc.strip()})
                    st.success(f"✅ '{nome_fmt}' adicionado — R$ {novo_valor:.2f}!"); st.rerun()
        st.divider()
        st.markdown("### 📋 Tabela Atual")
        col_s, col_t = st.columns(2)
        with col_s:
            st.markdown("**✂️ Serviços**")
            if not df_srv.empty:
                st.dataframe(df_srv[["nome","valor","descricao"]].rename(columns={"nome":"Serviço","valor":"Valor (R$)","descricao":"Descrição"}), use_container_width=True, hide_index=True)
        with col_t:
            st.markdown("**🚐 Transportes**")
            if not df_tax.empty:
                st.dataframe(df_tax[["nome","valor","descricao"]].rename(columns={"nome":"Opção","valor":"Taxa (R$)","descricao":"Descrição"}), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  7. USUÁRIOS (somente admin)
# ══════════════════════════════════════════════════════════════════════════════
elif "Usuários" in pagina:
    if not is_admin:
        st.error("⛔ Acesso restrito a administradores."); st.stop()

    st.markdown("## 🔐 Gestão de Usuários")
    st.caption("Somente administradores têm acesso a esta tela.")
    st.divider()

    aba_lista, aba_novo_user = st.tabs(["👥 Usuários Cadastrados","➕ Novo Usuário"])

    with aba_lista:
        df_users = sb_get("usuarios", order="id")
        if df_users.empty:
            st.info("Nenhum usuário cadastrado.")
        else:
            for _, u in df_users.iterrows():
                uid=int(u["id"]); ativo=bool(u["ativo"]); is_self=uid==int(usuario_atual["id"])
                ph2 = "<span class='badge-admin'>Admin</span>" if u["perfil"]=="admin" else "<span class='badge-func'>Funcionário</span>"
                cor_u = "#059669" if ativo else "#9CA3AF"
                st.markdown(f"""
                <div class='user-card'>
                    <span style='font-weight:700'>👤 {u['nome']}</span> &nbsp; {ph2}
                    {"&nbsp; <span style='font-size:.75rem;color:#0ea5e9'>(você)</span>" if is_self else ""}
                    <br><span style='font-size:.85rem;color:#64748b'>Login: <b>{u['login']}</b> &nbsp;·&nbsp; <span style='color:{cor_u}'>{'● Ativo' if ativo else '● Inativo'}</span></span>
                </div>""", unsafe_allow_html=True)

                col_ed, col_pw, col_tog = st.columns([2,2,1])
                with col_ed:
                    with st.expander("✏️ Editar"):
                        with st.form(f"form_eu_{uid}", clear_on_submit=False):
                            new_nome   = st.text_input("Nome",  value=u["nome"],  key=f"un_{uid}")
                            new_login  = st.text_input("Login", value=u["login"], key=f"ul_{uid}")
                            new_perfil = st.selectbox("Perfil", ["admin","funcionario"],
                                                       index=0 if u["perfil"]=="admin" else 1, key=f"up_{uid}",
                                                       format_func=lambda x: "Admin" if x=="admin" else "Funcionário")
                            if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                                nn=new_nome.strip(); nl=new_login.strip().lower()
                                if nn and nl:
                                    sb_patch("usuarios", f"id=eq.{uid}", {"nome":nn,"login":nl,"perfil":new_perfil})
                                    if is_self:
                                        st.session_state["usuario"]["nome"]=nn
                                        st.session_state["usuario"]["perfil"]=new_perfil
                                    st.success("✅ Atualizado!"); st.rerun()
                                else: st.error("Nome e login são obrigatórios.")

                with col_pw:
                    with st.expander("🔑 Trocar senha"):
                        with st.form(f"form_pw_{uid}", clear_on_submit=True):
                            nova_pw = st.text_input("Nova senha *",    type="password", key=f"pw_{uid}")
                            conf_pw = st.text_input("Confirmar senha *", type="password", key=f"cpw_{uid}")
                            if st.form_submit_button("🔑 Alterar", type="primary", use_container_width=True):
                                if len(nova_pw)<6: st.error("Mínimo 6 caracteres.")
                                elif nova_pw!=conf_pw: st.error("Senhas não coincidem.")
                                else:
                                    sb_patch("usuarios", f"id=eq.{uid}", {"senha_hash":_hash(nova_pw)})
                                    st.success("✅ Senha alterada!")

                with col_tog:
                    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
                    if not is_self:
                        if st.button("⏸ Desativar" if ativo else "▶ Ativar", key=f"tog_{uid}"):
                            sb_patch("usuarios", f"id=eq.{uid}", {"ativo": 0 if ativo else 1})
                            st.rerun()
                    else:
                        st.caption("(você)")
                st.divider()

    with aba_novo_user:
        st.markdown("### Criar Novo Usuário"); st.divider()
        with st.form("form_novo_user", clear_on_submit=True):
            nu1,nu2   = st.columns(2)
            nu_nome   = nu1.text_input("Nome completo *")
            nu_login  = nu2.text_input("Login *", placeholder="ex: joao.silva")
            nu_perfil = st.selectbox("Perfil *", ["funcionario","admin"],
                                     format_func=lambda x: "Funcionário" if x=="funcionario" else "Admin")
            nu_senha  = st.text_input("Senha *",           type="password")
            nu_conf   = st.text_input("Confirmar senha *", type="password")
            st.markdown("<div style='background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;font-size:.85rem;color:#92400e;margin:8px 0'>⚠️ <b>Funcionário</b> — agenda, atualiza status e vê clientes.<br>&nbsp;&nbsp;&nbsp;<b>Admin</b> — acesso total incluindo preços e usuários.</div>", unsafe_allow_html=True)
            if st.form_submit_button("✅ Criar Usuário", type="primary"):
                nn=nu_nome.strip(); nl=nu_login.strip().lower().replace(" ","_")
                if not nn or not nl: st.error("Nome e login são obrigatórios.")
                elif len(nu_senha)<6: st.error("Senha deve ter ao menos 6 caracteres.")
                elif nu_senha!=nu_conf: st.error("Senhas não coincidem.")
                else:
                    exist = sb_get("usuarios", f"login=eq.{nl}")
                    if not exist.empty:
                        st.error(f"❌ Login '{nl}' já está em uso.")
                    else:
                        sb_post("usuarios", {"nome":nn,"login":nl,"senha_hash":_hash(nu_senha),"perfil":nu_perfil,"ativo":1})
                        st.success(f"✅ {nn} ({nl}) criado!"); st.rerun()
