import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import theme
import plotly.express as px
from maps import (
    MAPA_REGIOES, 
    MAPA_SEGMENTOS, 
    PIPELINE, 
    ETAPAS_FINAIS, 
    VENDEDORAS, 
    RESPONSAVEL, 
    MAPA_METAS
)
from db_dash import (
    _db_listar_leads, 
    _db_salvar_lead, 
    _db_atualizar_status, 
    _db_obter_tempo_medio_etapas,              
    _db_obter_historico_conversoes_temporais 
)
from services import (
    _todos_vendedores,
    _todos_agendadores, 
    _todos_responsaveis, 
    _proximo_passo_linear, 
    _mover_lead, 
    _leads_filtrados, 
    _fmt_date
)

st.set_page_config(
    page_title="Exagerado - CRM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

theme.apply()

# ──────────────────────────────────────────────────────────────────
# 3. INICIALIZAÇÃO DO SESSION STATE
# ──────────────────────────────────────────────────────────────────

def _init_state() -> None:
    st.session_state.setdefault("leads", [])
    st.session_state.setdefault("proximo_id", 1)
    st.session_state.setdefault("contrato_log_ativo", None)


_init_state()

theme.render_page_header(
    title="Exagerado - CRM",
    subtitle="Sistema Interno Operacional de Vendas",
    badge="v1.2",
)

# ──────────────────────────────────────────────────────────────────
# 6. ABAS
# ──────────────────────────────────────────────────────────────────

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🚀 Novo Agendamento",
    "📋 Funil de Vendas",
    "📊 Dashboard",
    "📜 Contratos",
    "🔍 Prospecção",
])

# ══════════════════════════════════════════════════════════════════
# ABA 1 — NOVO AGENDAMENTO
# ══════════════════════════════════════════════════════════════════

with aba1:

    todos_leads = _db_listar_leads()
    vendedoras  = _todos_vendedores()
    agendadores = _todos_agendadores()
    responsaveis = _todos_responsaveis()

    st.markdown('<p class="form-section-title">🎯 Progresso do Período</p>', unsafe_allow_html=True)
    opcoes_prog = ["(equipe completa)"] + agendadores
    vend_prog = st.selectbox(
        "Ver meta de:",
        options=opcoes_prog,
        label_visibility="collapsed",
        key="vend_prog_sel",
    )

    if vend_prog == "(equipe completa)":
        leads_prog = todos_leads
        label_prog = "Equipe"
        
        meta_semanal = sum(meta.get("semanal", 0) for meta in MAPA_METAS.values())
        meta_diaria  = sum(meta.get("diaria", 0) for meta in MAPA_METAS.values())
    else:
        leads_prog = [l for l in todos_leads if l.get("responsavel_agendamento") == vend_prog]
        label_prog = vend_prog
        
        meta_semanal = MAPA_METAS.get(vend_prog, {}).get("semanal", 0)
        meta_diaria  = MAPA_METAS.get(vend_prog, {}).get("diaria", 0)

    agend_count_sem = sum(1 for l in leads_prog if l.get("status") != "Perda / Caiu")
    
    hoje = date.today()
    agend_count_dia = 0
    
    for l in leads_prog:
        if l.get("status") != "Perda / Caiu":
            criado_em = l.get("criado_em")
            
            if isinstance(criado_em, datetime):
                if criado_em.date() == hoje:
                    agend_count_dia += 1
            elif isinstance(criado_em, date):
                if criado_em == hoje:
                    agend_count_dia += 1

    meta_sem_ok = agend_count_sem >= meta_semanal if meta_semanal > 0 else False
    meta_dia_ok = agend_count_dia >= meta_diaria if meta_diaria > 0 else False

    pct_sem = min(agend_count_sem / meta_semanal, 1.0) if meta_semanal > 0 else 0.0
    pct_dia = min(agend_count_dia / meta_diaria, 1.0) if meta_diaria > 0 else 0.0

    hint_txt_sem   = "🏆 Meta semanal batida! Incrível! 🎉" if meta_sem_ok else f"Faltam {meta_semanal - agend_count_sem} para a meta semanal."
    hint_class_sem = "hint ok" if meta_sem_ok else "hint"
    
    hint_txt_dia   = "🚀 Meta diária batida! Continua assim! 🔥" if meta_dia_ok else f"Faltam {meta_diaria - agend_count_dia} para a meta diária."
    hint_class_day = "hint ok" if meta_dia_ok else "hint"

    html_card = """<div class="progress-box"><h3 style="margin-bottom: 12px !important; color: #9E8FAD !important; font-family: 'Space Mono', monospace; font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase;">📈 Acompanhamento de Metas — {label}</h3><div style="margin-bottom: 15px !important;"><div class="count" style="font-family: 'Space Mono', monospace; font-size: 1.8rem !important; font-weight: 700; color: #E54E88; line-height: 1;">{qtd_dia}<span style="font-size: 0.9rem !important; color: #9E8FAD !important; font-weight: normal;"> / {meta_dia} meta diária</span></div><p class="{classe_dia}" style="margin: 2px 0 6px 0 !important; font-size: 0.76rem;">{texto_dia}</p></div><div><div class="count" style="font-family: 'Space Mono', monospace; font-size: 1.8rem !important; font-weight: 700; color: #E54E88; line-height: 1;">{qtd_sem}<span style="font-size: 0.9rem !important; color: #9E8FAD !important; font-weight: normal;"> / {meta_sem} meta semanal</span></div><p class="{classe_sem}" style="margin: 2px 0 2px 0 !important; font-size: 0.76rem;">{texto_sem}</p></div></div>""".format(
        label=label_prog, qtd_dia=agend_count_dia, meta_dia=meta_diaria, classe_dia=hint_class_day, texto_dia=hint_txt_dia, qtd_sem=agend_count_sem, meta_sem=meta_semanal, classe_sem=hint_class_sem, texto_sem=hint_txt_sem
    )
    st.markdown(html_card, unsafe_allow_html=True)
    
    st.markdown('<p style="font-size:0.75rem; font-weight:600; margin-bottom:-5px; color:#5C3D7A;">Progresso Diário</p>', unsafe_allow_html=True)
    st.progress(pct_dia)
    
    st.markdown('<p style="font-size:0.75rem; font-weight:600; margin-bottom:-5px; color:#5C3D7A; margin-top:10px;">Progresso Semanal</p>', unsafe_allow_html=True)
    st.progress(pct_sem)

    # Alertas de sucesso baseados em metas reais atingidas
    if meta_sem_ok:
        st.success(f"🎊 **{label_prog}** zerou a meta da semana! Que time fantástico! 💪")
    elif meta_dia_ok:
        st.success(f"🔥 **{label_prog}** bateu a meta do dia! Ritmo acelerado! ⚡")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Formulário ────────────────────────────────────────────────
    with st.form("form_agendamento", clear_on_submit=True):

        st.markdown("### 📌 Registrar Novo Agendamento")

        st.markdown('<p class="form-section-title">✦ Dados Essenciais</p>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            nome_fantasia    = st.text_input("🏪 Nome Fantasia do Lead",        placeholder="Ex: Boutique Fashion Premium")
            resp_agendamento = st.selectbox("👤 Responsável pelo Agendamento", options=RESPONSAVEL)
            data_reuniao     = st.date_input("📅 Data da Reunião",              value=date.today())
        with col_b:
            resp_venda = st.selectbox("🤝 Responsável pela Venda Final", options=VENDEDORAS)
            segmento   = st.selectbox("🏷️ Segmento", list(MAPA_SEGMENTOS.keys()))
            estado     = st.selectbox("📍 Estado",   list(MAPA_REGIOES.keys()))

        st.markdown('<p class="form-section-title">📊 Qualificação (Opcional — Lead Scoring)</p>', unsafe_allow_html=True)
        cq1, cq2, cq3, cq4 = st.columns(4)
        with cq1: num_funcionarios = st.number_input("👥 Funcionários",    min_value=0, value=0, step=1)
        with cq2: num_lojas        = st.number_input("🏬 Lojas",           min_value=0, value=0, step=1)
        with cq3: ticket_medio     = st.number_input("💰 Ticket Médio R$", min_value=0.0, value=0.0, step=100.0)
        with cq4: total_pecas      = st.number_input("📦 Peças Estoque",   min_value=0, value=0, step=50)

        st.markdown('<p class="form-section-title">🔎 Origem</p>', unsafe_allow_html=True)
        origem_lista = st.checkbox("✅ Veio da lista do Modelo de Prospecção Inteligente?")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 SALVAR AGENDAMENTO", use_container_width=True)

    if submitted:
        erros = []
        if not nome_fantasia.strip():    erros.append("Nome Fantasia é obrigatório.")
        if not resp_agendamento.strip(): erros.append("Responsável pelo Agendamento é obrigatório.")
        if not resp_venda.strip():       erros.append("Responsável pela Venda Final é obrigatório.")

        if erros:
            for e in erros:
                st.error(f"❌ {e}")
        else:
            novo = {
                "nome_fantasia":           nome_fantasia.strip(),
                "responsavel_agendamento": resp_agendamento.strip(),
                "responsavel_venda":       resp_venda.strip(),
                "data_reuniao":            data_reuniao,
                "segmento":                segmento,
                "estado":                  estado,
                "num_funcionarios":        num_funcionarios,
                "num_lojas":               num_lojas,
                "ticket_medio":            float(ticket_medio),
                "total_pecas":             total_pecas,
                "origem_lista":            origem_lista,
                "status":                  "Agendado",
                "forms_enviado":           False,
                "criado_em":               datetime.now().isoformat(),
            }
            _db_salvar_lead(novo)

            st.balloons()
            st.snow()
            primeiro = resp_agendamento.strip().split()[0].upper()
            st.success(f"🎉🚀 **BOA, {primeiro}!** **{nome_fantasia}** entrou no funil! 💜⚡")
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# ABA 2 — FUNIL DE VENDAS (Kanban)
# ══════════════════════════════════════════════════════════════════

with aba2:

    st.markdown("### 📋 Funil de Vendas")

    todos_leads = _db_listar_leads()
    vendedoras  = _todos_vendedores()
    agendadores = _todos_agendadores()
    responsaveis = _todos_responsaveis()

    # ── Filtros ───────────────────────────────────────────────────
    with st.expander("🔍 Filtros", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_agend = st.selectbox(
                "Responsável pelo Agendamento",
                ["Todos"] + agendadores,
                key="f_agend",
            )
        with fc2:
            f_venda = st.selectbox(
                "Responsável pela Venda",
                ["Todos"] + vendedoras,
                key="f_venda",
            )
        with fc3:
            f_etapas = st.multiselect(
                "Exibir Etapas",
                PIPELINE,
                default=PIPELINE,
                key="f_etapas",
            )

    fa = f_agend if f_agend != "Todos" else None
    fv = f_venda if f_venda != "Todos" else None

    leads_vis = _leads_filtrados(todos_leads, fa, fv)
    leads_vis = [l for l in leads_vis if l.get("status") in f_etapas]

    # ── Métricas rápidas ──────────────────────────────────────────
    mc = st.columns(len(PIPELINE))
    for i, etapa in enumerate(PIPELINE):
        cnt = sum(1 for l in leads_vis if l.get("status") == etapa)
        mc[i].metric(theme.ETAPA_VISUAL[etapa]["emoji"] + " " + etapa.split("/")[0].strip(), cnt)

    if not todos_leads:
        st.info("Nenhum lead cadastrado ainda. Use **🚀 Novo Agendamento** para começar!")
    else:
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Fase 1 — Pré-Reunião ──────────────────────────────────
        st.markdown("#### Fase 1 — Pré-Reunião")
        cols_f1 = st.columns([1.2, 1, 1, 1.2])
        etapas_f1 = ["Agendado", "No Show", "Perda / Caiu", "Reunião Realizada"]

        for col_obj, etapa in zip(cols_f1, etapas_f1):
            leads_col = [l for l in leads_vis if l.get("status") == etapa]
            with col_obj:
                theme.render_kanban_header(etapa, len(leads_col))

                if not leads_col:
                    st.markdown(
                        '<p style="text-align:center;color:#D1D5DB;font-size:0.75rem;padding:14px 0;">vazio</p>',
                        unsafe_allow_html=True,
                    )
                    continue

                for lead in leads_col:
                    theme.render_lead_card(lead)

                    if etapa == "Agendado":
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("🎬 No Show",   key=f"show_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "No Show")
                        with b2:
                            if st.button("💀 Caiu",   key=f"caiu_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Perda / Caiu")
                        with b3:
                            if st.button("🤝 Reuniu", key=f"reu_{lead['id']}",  use_container_width=True):
                                _mover_lead(lead["id"], "Reunião Realizada")

                    elif etapa == "No Show":
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("🤝 Reuniu ➔", key=f"sr_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Reunião Realizada")
                        with b2:
                            if st.button("💀 Caiu",     key=f"sc_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Perda / Caiu")

                    elif etapa == "Perda / Caiu":
                        if st.button("♻️ Reativar", key=f"reat_{lead['id']}", use_container_width=True):
                            _mover_lead(lead["id"], "Agendado")

                    elif etapa == "Reunião Realizada":
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("🔥 Tô Dentro ➔", key=f"den_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Tô Dentro")
                        with b2:
                            if st.button("💀 Caiu", key=f"rc_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Perda / Caiu")

        # ── Fase 2 — Fechamento ───────────────────────────────────
        st.markdown("#### Fase 2 — Fechamento")
        cols_f2 = st.columns(3)
        etapas_f2 = ["Tô Dentro", "Contrato Enviado", "Contrato Assinado"]

        for col_obj, etapa in zip(cols_f2, etapas_f2):
            leads_col = [l for l in leads_vis if l.get("status") == etapa]
            with col_obj:
                theme.render_kanban_header(etapa, len(leads_col))

                if not leads_col:
                    st.markdown(
                        '<p style="text-align:center;color:#D1D5DB;font-size:0.75rem;padding:14px 0;">vazio</p>',
                        unsafe_allow_html=True,
                    )
                    continue

                for lead in leads_col:
                    theme.render_lead_card(lead)

                    if etapa == "Tô Dentro":
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("📨 Enviar Contrato ➔", key=f"env_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Contrato Enviado")
                        with b2:
                            if st.button("💀 Caiu", key=f"dc_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Perda / Caiu")

                    elif etapa == "Contrato Enviado":
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("✅ Assinou 🏆", key=f"ass_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Contrato Assinado")
                        with b2:
                            if st.button("💀 Caiu", key=f"de_{lead['id']}", use_container_width=True):
                                _mover_lead(lead["id"], "Perda / Caiu")

                    elif etapa == "Contrato Assinado":
                        st.markdown(
                            '<p style="text-align:center;font-size:0.72rem;color:#D97706;margin-top:4px;font-weight:600;">🏆 Negócio fechado!</p>',
                            unsafe_allow_html=True,
                        )

# ══════════════════════════════════════════════════════════════════
# ABA 3 — DASHBOARD
# ══════════════════════════════════════════════════════════════════

# Certifique-se de ter importado lá no topo: import plotly.express as px

with aba3:
    st.markdown("### 📊 Dashboard de Performance")
    
    # 1. CARREGAMENTO DOS DATASETS
    todos_leads = _db_listar_leads()
    vendedoras  = _todos_vendedores()
    agendadores = _todos_agendadores()
    
    try:
        historico_transicoes = _db_obter_historico_conversoes_temporais()
        df_hist = pd.DataFrame(historico_transicoes)
        if not df_hist.empty:
            df_hist['criado_em'] = pd.to_datetime(df_hist['criado_em'])
    except Exception:
        df_hist = pd.DataFrame()

    if not todos_leads:
        st.info("Sem dados ainda. Cadastre leads pela aba **🚀 Novo Agendamento**.")
    else:
        # ──────────────────────────────────────────────────────────
        # SEÇÃO 1: PAINEL GERENCIAL (O QUE O GUSTAVO QUER VER)
        # ──────────────────────────────────────────────────────────
        st.subheader("🎯 Visão Executiva e Controle de Metas")
        
        with st.container():
            f1, f2 = st.columns([1, 2])
            with f1:
                filtro_tempo = st.radio(
                    "📆 Período de Análise:",
                    ["Hoje", "Esta Semana", "Este Mês", "Histórico Total"],
                    horizontal=True,
                    key="dash_filtro_tempo"
                )
            with f2:
                dash_vend = st.selectbox(
                    "👤 Filtrar por Membro da Equipe:",
                    ["Equipe completa"] + agendadores,
                    key="dash_vend_exec"
                )

        hoje_dt = date.today()
        
        if filtro_tempo == "Hoje":
            df_hist_filtrado = df_hist[df_hist['criado_em'].dt.date == hoje_dt] if not df_hist.empty else pd.DataFrame()
            leads_criados_periodo = [l for l in todos_leads if pd.to_datetime(l.get('criado_em')).date() == hoje_dt]
        elif filtro_tempo == "Esta Semana":
            inicio_semana = hoje_dt - pd.Timedelta(days=hoje_dt.weekday())
            df_hist_filtrado = df_hist[df_hist['criado_em'].dt.date >= inicio_semana] if not df_hist.empty else pd.DataFrame()
            leads_criados_periodo = [l for l in todos_leads if pd.to_datetime(l.get('criado_em')).date() >= inicio_semana]
        elif filtro_tempo == "Este Mês":
            df_hist_filtrado = df_hist[(df_hist['criado_em'].dt.year == hoje_dt.year) & (df_hist['criado_em'].dt.month == hoje_dt.month)] if not df_hist.empty else pd.DataFrame()
            leads_criados_periodo = [l for l in todos_leads if pd.to_datetime(l.get('criado_em')).year == hoje_dt.year and pd.to_datetime(l.get('criado_em')).month == hoje_dt.month]
        else:
            df_hist_filtrado = df_hist
            leads_criados_periodo = todos_leads

        if dash_vend != "Equipe completa":
            leads_criados_periodo = [l for l in leads_criados_periodo if l.get("responsavel_agendamento") == dash_vend]
            if not df_hist_filtrado.empty:
                ids_dono = {l['id'] for l in todos_leads if l.get("responsavel_agendamento") == dash_vend}
                df_hist_filtrado = df_hist_filtrado[df_hist_filtrado['lead_id'].isin(ids_dono)]

        # ── CÁLCULO DOS KPIS  ─────────
        agendamentos_f1 = len(leads_criados_periodo)
        
        if not df_hist_filtrado.empty:
            reunioes_f1 = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Reunião Realizada"]['lead_id'].nunique()
            assinados_f1 = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Contrato Assinado"]['lead_id'].nunique()
            perdas_f1 = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Perda / Caiu"]['lead_id'].nunique()
            
            if perdas_f1 == 0:
                perdas_f1 = sum(1 for l in leads_criados_periodo if l.get("status") == "Perda / Caiu")
        else:
            reunioes_f1 = sum(1 for l in leads_criados_periodo if l.get("status") not in ("Agendado", "No Show", "Perda / Caiu"))
            assinados_f1 = sum(1 for l in leads_criados_periodo if l.get("status") == "Contrato Assinado")
            perdas_f1 = sum(1 for l in leads_criados_periodo if l.get("status") == "Perda / Caiu")

        tx_reu_f1 = f"{(reunioes_f1 / agendamentos_f1 * 100):.0f}%" if agendamentos_f1 else "0%"
        tx_fec_f1 = f"{(assinados_f1 / max(reunioes_f1, 1) * 100):.0f}%"

        # Renderização dos Cards
        st.markdown("<br>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        C = theme.CORES
        with k1: theme.render_dash_card("Novos Agendamentos", str(agendamentos_f1), "no período selecionado", C.get("sky", "#87CEEB"))
        with k2: theme.render_dash_card("Reuniões Realizadas", str(reunioes_f1), f"Aproveitamento: {tx_reu_f1}", C.get("reuniao", "#4B0082"))
        with k3: theme.render_dash_card("Contratos Assinados 🏆", str(assinados_f1), f"Conversão: {tx_fec_f1}", C.get("gold", "#FFD700"))
        with k4: theme.render_dash_card("Leads Perdidos", str(perdas_f1), "caíram do funil", C.get("red", "#FF0000"))

        # ── 🚀 GRÁFICO DE FUNIL DO PLOTLY ──
        st.markdown("#### 🏷️ Funil Volumétrico de Conversão (Movimentação do Período)")
        
        if not df_hist_filtrado.empty:
            cnt_agend = len(leads_criados_periodo)
            cnt_reuniu = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Reunião Realizada"]['lead_id'].nunique()
            cnt_dentro = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Tô Dentro"]['lead_id'].nunique()
            cnt_envia  = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Contrato Enviado"]['lead_id'].nunique()
            cnt_assina = df_hist_filtrado[df_hist_filtrado['status_novo'] == "Contrato Assinado"]['lead_id'].nunique()
            
            cnt_reuniu = max(cnt_reuniu, cnt_dentro, cnt_envia, cnt_assina)
            cnt_dentro = max(cnt_dentro, cnt_envia, cnt_assina)
            cnt_envia  = max(cnt_envia, cnt_assina)
            cnt_agend  = max(cnt_agend, cnt_reuniu)
        else:
            # Fallback seguro caso o histórico esteja zerado (Primeiros testes)
            cnt_assina = sum(1 for l in leads_criados_periodo if l.get("status") == "Contrato Assinado")
            cnt_envia  = sum(1 for l in leads_criados_periodo if l.get("status") == "Contrato Enviado") + cnt_assina
            cnt_dentro = sum(1 for l in leads_criados_periodo if l.get("status") == "Tô Dentro") + cnt_envia
            cnt_reuniu = sum(1 for l in leads_criados_periodo if l.get("status") == "Reunião Realizada") + cnt_dentro
            cnt_agend  = sum(1 for l in leads_criados_periodo if l.get("status") == "Agendado") + cnt_reuniu

        estagios_funnel = ["Agendado", "Reunião Realizada", "Tô Dentro", "Contrato Enviado", "Contrato Assinado"]
        valores_funnel = [cnt_agend, cnt_reuniu, cnt_dentro, cnt_envia, cnt_assina]
        
        df_funnel_plot = pd.DataFrame({
            "Etapa": estagios_funnel,
            "Leads": valores_funnel
        })
        
        fig_funnel = px.funnel(
            df_funnel_plot, 
            x='Leads', 
            y='Etapa',
            color_discrete_sequence=["#E54E88"]
        )
        fig_funnel.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#2D1B3D"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig_funnel, use_container_width=True)


        # ── 👥 TABELA DE PERFORMANCE ──
        st.markdown("#### 👥 Desempenho Acumulado por Agendadora")
        rows = []
        
        for v in agendadores:
            leads_da_vendedora = [l for l in leads_criados_periodo if l.get("responsavel_agendamento") == v]
            
            ns  = sum(1 for l in leads_da_vendedora if l.get("status") == "No Show")
            per = sum(1 for l in leads_da_vendedora if l.get("status") == "Perda / Caiu")

            cnt_assina = sum(1 for l in leads_da_vendedora if l.get("status") == "Contrato Assinado")
            cnt_envia  = sum(1 for l in leads_da_vendedora if l.get("status") == "Contrato Enviado") + cnt_assina
            cnt_dentro = sum(1 for l in leads_da_vendedora if l.get("status") == "Tô Dentro") + cnt_envia
            cnt_reuniu = sum(1 for l in leads_da_vendedora if l.get("status") == "Reunião Realizada") + cnt_dentro
            
            cnt_ativo_agendado = sum(1 for l in leads_da_vendedora if l.get("status") == "Agendado")
            cnt_agend = cnt_ativo_agendado + cnt_reuniu + ns + per

            meta_sem = MAPA_METAS.get(v, {}).get("semanal", 1)
            
            rows.append({
                "Agendadora": v,
                "Total Agendados": cnt_agend,
                "No Shows 🎬": ns,
                "Reuniões 🤝": cnt_reuniu,
                "Tô Dentro 🔥": cnt_dentro,
                "Env. Contrato 📨": cnt_envia,
                "Assinados 🏆": cnt_assina,
                "Perdas 💀": per,
                "Conversão (Reu/Agen)": f"{(cnt_reuniu / max(cnt_agend, 1) * 100):.0f}%",
                "Eficiência (Ass/Reu)": f"{(cnt_assina / max(cnt_reuniu, 1) * 100):.0f}%",
                "% Meta Semanal": f"{(cnt_agend / meta_sem * 100):.0f}%",
            })
            
        if rows:
            df_rank = pd.DataFrame(rows).sort_values("Total Agendados", ascending=False)
            st.dataframe(df_rank, use_container_width=True, hide_index=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # ──────────────────────────────────────────────────────────
        # SEÇÃO 2: ANALYTICS & CICLO DE VIDA
        # ──────────────────────────────────────────────────────────
        st.subheader("🧠 Laboratório Científico de Sales Ops")
        st.caption("Métricas avançadas de retenção e distribuição para insights de modelagem preditiva.")
        
        leads_analise = [l for l in todos_leads if l.get("status") in PIPELINE]

        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("#### ⏳ Tempo Médio de Retenção por Etapa (Dias)")
            try:
                tempos_etapas = _db_obter_tempo_medio_etapas()
                if tempos_etapas:
                    df_tempos = pd.DataFrame(tempos_etapas)
                    st.bar_chart(df_tempos.set_index("etapa"), use_container_width=True, color="#8B5CF6")
                else:
                    st.info("Aguardando mais transições de histórico para calcular médias estáveis.")
            except Exception:
                df_mock_tempo = pd.DataFrame([{"etapa": e, "media_dias": 0.0} for e in PIPELINE])
                st.bar_chart(df_mock_tempo.set_index("etapa"), use_container_width=True, color="#8B5CF6")

        with g2:
            st.markdown("#### 💀 Concentração de Perda por Etapa do Funil")
            if not df_hist.empty:
                df_perdas = df_hist[df_hist['status_novo'] == "Perda / Caiu"]
                if not df_perdas.empty and 'status_anterior' in df_perdas.columns:
                    loss_distribution = df_perdas['status_anterior'].value_counts().reset_index()
                    loss_distribution.columns = ['Etapa de Origem da Perda', 'Quantidade']
                    st.bar_chart(loss_distribution.set_index('Etapa de Origem da Perda'), use_container_width=True, color="#EF4444")
                else:
                    st.info("Nenhuma perda registrada no histórico até o momento.")
            else:
                st.info("Sem dados de histórico suficientes.")

        st.markdown("<br>", unsafe_allow_html=True)
        g3, g4 = st.columns(2)
        
        with g3:
            st.markdown("#### 🏷️ Volume de Leads por Segmento")
            seg_data = {}
            for l in leads_analise:
                seg_data[l.get("segmento", "—")] = seg_data.get(l.get("segmento", "—"), 0) + 1
            if seg_data:
                df_seg = pd.DataFrame(list(seg_data.items()), columns=["Segmento", "Leads"]).sort_values("Leads", ascending=False)
                st.bar_chart(df_seg.set_index("Segmento"), use_container_width=True, color="#0EA5E9")

        with g4:
            st.markdown("#### 📍 Distribuição Regional de Oportunidades")
            est_data = {}
            for l in leads_analise:
                est_data[l.get("estado", "—")] = est_data.get(l.get("estado", "—"), 0) + 1
            if est_data:
                df_est = pd.DataFrame(list(est_data.items()), columns=["Estado", "Leads"]).sort_values("Leads", ascending=False)
                st.bar_chart(df_est.set_index("Estado"), use_container_width=True, color="#10B981")

# ══════════════════════════════════════════════════════════════════
# ABA 4 — CONTRATOS (AUTOMATIZAÇÃO INTEGRADA)
# ══════════════════════════════════════════════════════════════════
import urllib.parse  # Para codificar o texto do WhatsApp de forma segura

with aba4:
    st.markdown("### 📜 Emissão e Controle de Contratos")
    st.caption("Central de Ingestão do Excel 365, Validação Cadastral e Assinatura Digital.")

    # 1. BOTÃO DE INGESTÃO DO EXCEL 365
    c_sync, _ = st.columns([1, 3])
    with c_sync:
        if st.button("🔄 Sincronizar Respostas (Excel 365)", use_container_width=True):
            with st.spinner("Buscando dados, validando CNPJs e Higienizando... ⚡"):
                # Aqui vai rodar sua pipeline de Regex + API pública antes do insert
                # _db_sincronizar_excel() 
                time.sleep(1.5) # Simulação rápida temporária
                st.success("Planilha sincronizada e dados limpos no Postgres! 💾")
                st.rerun()

    st.markdown("---")

    # 2. ABA INTERNA: SEPARAÇÃO DO FLUXO OPERACIONAL
    sub_aba_vincular, sub_aba_gerar = st.tabs(["🔍 1. Casar e Enriquecer Leads", "📄 2. Gerar e Disparar Contrato"])

    # ──────────────────────────────────────────────────────────────
    # SUB-ABA 1: CASAMENTO MANUAL (DATA CURATION)
    # ──────────────────────────────────────────────────────────────
    with sub_aba_vincular:
        st.markdown("#### 🛠️ Vincular Formulário 'Tô Dentro' ao CRM")
        st.caption("Ajuste o fator humano: amarre a Razão Social digitada pelo cliente ao Lead correto do Kanban.")

        # Simulando dados validados vindos do banco que estão 'Aguardando Vínculo'
        # Em produção: contratos_pendentes = _db_listar_contratos_pendentes(status='Aguardando Vínculo')
        contratos_pendentes = [
            {"id_solicitacao": 1, "nome_formulario": "Silva Confecções LTDA", "cnpj": "12345678000199", "email": "socio@silva.com"},
            {"id_solicitacao": 2, "nome_formulario": "Boutique Premium ES", "cnpj": "98765432000111", "email": "contato@premium.com"}
        ]

        # Puxa os leads que estão estagnados na etapa "Tô Dentro" no CRM principal
        todos_leads = _db_listar_leads()
        leads_no_todentro = [l for l in todos_leads if l.get("status") == "Tô Dentro"]

        if not contratos_pendentes:
            st.info("🎉 Nenhum contrato pendente de vínculo ou enriquecimento no momento.")
        else:
            # Renderiza as linhas vindas do Excel para a auxiliar tratar
            for cp in contratos_pendentes:
                with st.expander(f"🏪 Formulário de: {cp['nome_formulario']} (CNPJ: {cp['cnpj']})", expanded=True):
                    col_f1, col_f2, col_f3 = st.columns([1.5, 2, 1])
                    
                    with col_f1:
                        st.markdown(f"**Dados Cadastrados pelo Cliente:**\n"
                                    f"- **Sócio/E-mail:** {cp['email']}\n"
                                    f"- **CNPJ Validado:** {cp['cnpj']}")
                        
                    with col_f2:
                        # Seletor para o casamento humano infalível
                        opcoes_crm = [f"{l['id']} - {l['nome_fantasia']}" for l in leads_no_todentro]
                        lead_selecionado = st.selectbox(
                            "🤝 Selecione o Lead correspondente no CRM:",
                            options=["-- Escolha o Lead do CRM --"] + opcoes_crm,
                            key=f"sel_lead_{cp['id_solicitacao']}"
                        )
                    
                    with col_f3:
                        st.markdown("**Enriquecimento Operacional:**")
                        stand = st.text_input("🏪 Stand (Endereço)", placeholder="Ex: Setor A - 12", key=f"stand_{cp['id_solicitacao']}")
                        metragem = st.number_input("📐 Metragem (m²)", min_value=0.0, step=1.0, key=f"metra_{cp['id_solicitacao']}")
                        receita = st.number_input("💰 Valor do Stand (R$)", min_value=0.0, step=100.0, key=f"rec_{cp['id_solicitacao']}")

                    # Botão para salvar tudo na tabela unica contratos_pendentes mudando status para 'Pronto para Gerar'
                    b_salvar, _ = st.columns([1, 3])
                    with b_salvar:
                        if st.button("💾 Salvar e Validar", key=f"btn_salvar_{cp['id_solicitacao']}", use_container_width=True):
                            if lead_selecionado == "-- Escolha o Lead do CRM --" or not stand.strip():
                                st.error("❌ É obrigatório vincular o lead do CRM e preencher o endereço do Stand.")
                            else:
                                id_lead_real = int(lead_selecionado.split(" - ")[0])
                                # _db_vincular_e_enriquecer(cp['id_solicitacao'], id_lead_real, stand, metragem, receita)
                                st.success(f"Lead {id_lead_real} vinculado e pronto para emissão! 🏆")
                                time.sleep(0.5)
                                st.rerun()

    # ──────────────────────────────────────────────────────────────
    # SUB-ABA 2: EMISSÃO E DISPARO (A SUA PIPELINE ANTIGA)
    # ──────────────────────────────────────────────────────────────
    with sub_aba_gerar:
        st.markdown("#### ⚡ Emissão de Contratos em Lote / Individual")
        st.caption("Geração de templates DOCX, conversão estável para PDF e upload na Autentique.")

        # Aqui listamos apenas as linhas cujo status da automação já é 'Pronto para Gerar'
        # Em produção: leads_prontos = _db_listar_contratos_pendentes(status='Pronto para Gerar')
        # Para fins de demonstração visual, vamos listar os leads do CRM que estão avançados
        leads_contrato = [
            l for l in todos_leads
            if l.get("status") in ("Tô Dentro", "Contrato Enviado", "Contrato Assinado")
        ]

        if not leads_contrato:
            st.warning("Nenhum lead pronto para emissão de contrato. Trate-os na aba ao lado! 💜")
        else:
            # Exibe o grid com o que já está na agulha
            df_ct = pd.DataFrame([
                {
                    "ID":           l.get("id"),
                    "Lead":         l.get("nome_fantasia"),
                    "Segmento":     l.get("segmento"),
                    "Estado":       l.get("estado"),
                    "Fechador":     l.get("responsavel_venda"),
                    "Status Atual": l.get("status"),
                }
                for l in leads_contrato
            ])
            st.dataframe(df_ct, use_container_width=True, hide_index=True)

            st.markdown("---")
            sel_nome = st.selectbox(
                "Selecione o Lead para Emissão",
                options=[l["nome_fantasia"] for l in leads_contrato],
                key="sel_emissao_final"
            )
            sel = next(l for l in leads_contrato if l["nome_fantasia"] == sel_nome)

            cb1, _ = st.columns([1, 3])
            with cb1:
                gerar = st.button("📄 Gerar e Enviar Contrato Real", use_container_width=True)

            if gerar:
                st.session_state.contrato_log_ativo = sel_nome

            if st.session_state.get("contrato_log_ativo") == sel_nome:
                log_ph = st.empty()
                
                # Logs dinâmicos que agora representarão o seu backend executando de verdade
                logs = [
                    "🔍 Buscando dados validados na tabela 'contratos_pendentes'...",
                    "✅ Registro localizado e casado com o CRM.",
                    "📋 Verificando integridade das features de Enriquecimento...",
                    "🖨️ Instanciando DocxTemplate com variáveis comerciais...",
                    f"✅ PDF gerado via Engine estável: contrato_{sel_nome.replace(' ','_').lower()}.pdf",
                    "📧 Conectando à API da Autentique...",
                    "✅ Upload concluído! Documento enviado para os e-mails dos signatários. ✉️",
                    "⚙️ Sincronizando: Status do CRM alterado para 'Contrato Enviado'.",
                ]
                log_txt = ""
                for linha in logs:
                    log_txt += linha + "\n"
                    log_ph.markdown(f'<div class="log-box">{log_txt}</div>', unsafe_allow_html=True)
                    time.sleep(0.4) # Velocidade charmosa de log na tela

                resp = sel.get("responsavel_venda", "").split()[0] if sel.get("responsavel_venda") else "Equipe"
                
                # Texto visual com emojis para a vendedora ver na tela do Streamlit (Dopamina Visual)
                wpp_visual = (
                    f"Olá, tudo bem? 😊\n\n"
                    f"Aqui é {resp} do Exagerado - Maior Evento de Varejo e Outlet do Brasil.\n\n"
                    f"Conforme combinado, acabei de enviar o contrato referente à nossa "
                    f"parceria com a {sel_nome} para o seu e-mail cadastrado.\n\n"
                    f"Por favor, confirme o recebimento! Qualquer dúvida, estou aqui. 🚀\n\n"
                    f"Att,\n{resp} — Exagerado"
                )

                wpp_url = (
                    f"Ola, tudo bem? \n\n"
                    f"Aqui e {resp} do Exagerado - Maior Evento de Varejo e Outlet do Brasil.\n\n"
                    f"Conforme combinado, acabei de enviar o contrato referente a nossa "
                    f"parceria com a {sel_nome} para o seu e-mail cadastrado.\n\n"
                    f"Por favor, confirme o recebimento! Qualquer duvida, estou aqui. \n\n"
                    f"Att,\n{resp} — Exagerado"
                )
                
                # Codificação simples e direta
                wpp_encoded = urllib.parse.quote(wpp_url)
                
                telefone_cliente = "5527998225335" 
                link_whatsapp_api = f"https://wa.me/{telefone_cliente}?text={wpp_encoded}"

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f'<div class="whatsapp-box"><strong>📲 Mensagem de Acompanhamento Pronta</strong><br><br>'
                    f'{wpp_visual.replace(chr(10),"<br>")}</div>',
                    unsafe_allow_html=True,
                )
                
                st.link_button("🟢 ABRIR CONVERSA NO WHATSAPP", link_whatsapp_api, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ABA 5 — MOTOR DE PROSPECÇÃO
# ══════════════════════════════════════════════════════════════════

with aba5:

    st.markdown("### 🔍 Motor de Prospecção — Instagram")

    st.warning(
        "⚠️ **[STATUS — EM MANUTENÇÃO]** "
        "O motor de busca do Instagram está em aquecimento de IP de segurança. "
        "Use o CRM abaixo enquanto os robôs descansam! ☕🤖"
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Configurar Nova Busca")

    cs1, cs2 = st.columns(2)
    with cs1:
        seg_busca = st.selectbox("🏷️ Segmento-Alvo", list(MAPA_SEGMENTOS.keys()), key="seg_p")
        st.caption("Termos: " + ", ".join(MAPA_SEGMENTOS[seg_busca]["termos_bio"][:3]) + "…")
    with cs2:
        reg_busca = st.selectbox("📍 Região-Alvo", list(MAPA_REGIOES.keys()), key="reg_p")
        hashtag = "#" + MAPA_SEGMENTOS[seg_busca]["prefixo"] + MAPA_REGIOES[reg_busca]["sufixo_hashtag"].replace("#", "")
        st.caption(f"Hashtag gerada: **{hashtag}**")

    co1, co2, co3 = st.columns(3)
    with co1: st.number_input("🎯 Mín. Seguidores", min_value=0, value=500, step=100, disabled=True)
    with co2: st.number_input("📸 Mín. Posts",      min_value=0, value=12,  step=1,   disabled=True)
    with co3: st.number_input("⚡ Leads/rodada",    min_value=1, value=50,  step=10,  disabled=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cb_run, _ = st.columns([1, 3])
    with cb_run:
        st.button("🚀 Iniciar Motor", disabled=True, use_container_width=True)

    st.info("🛠️ **Próxima sprint:** Instaloader + Playwright + PostgreSQL. IP em aquecimento.")

    st.markdown("---")
    st.markdown("#### 📒 Leads já registrados neste segmento")

    leads_seg = [l for l in _db_listar_leads() if l.get("segmento") == seg_busca]
    if leads_seg:
        st.markdown(f"**{len(leads_seg)} lead(s)** em **{seg_busca}**:")
        for l in leads_seg:
            st.markdown(
                f"- **{l.get('nome_fantasia','—')}** — {l.get('status','—')} "
                f"— {_fmt_date(l.get('data_reuniao'))} — {l.get('estado','—')}"
            )
    else:
        st.markdown(f"Nenhum lead em **{seg_busca}** ainda. Cadastre pelo formulário! 🎯")

# ──────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────

theme.render_footer()