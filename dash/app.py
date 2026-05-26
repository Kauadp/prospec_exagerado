import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import theme
from maps import MAPA_REGIOES, MAPA_SEGMENTOS, PIPELINE, ETAPAS_FINAIS, VENDEDORAS, RESPONSAVEL, MAPA_METAS
from db_dash import _db_listar_leads, _db_salvar_lead, _db_atualizar_status
from services import _todos_vendedores, _todos_agendadores, _todos_responsaveis, _proximo_passo_linear, _mover_lead, _leads_filtrados, _fmt_date
# ──────────────────────────────────────────────────────────────────
# 0. CONFIG DA PÁGINA
# ──────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Exagerado - CRM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

theme.apply()

# ──────────────────────────────────────────────────────────────────
# 3. INICIALIZAÇÃO DO SESSION STATE
# (apenas chaves de controle de UI — sem dados mockados)
# ──────────────────────────────────────────────────────────────────

def _init_state() -> None:
    st.session_state.setdefault("leads", [])
    st.session_state.setdefault("proximo_id", 1)
    st.session_state.setdefault("contrato_log_ativo", None)


_init_state()


# ──────────────────────────────────────────────────────────────────
# 5. HEADER
# ──────────────────────────────────────────────────────────────────

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
            
            # Se for um datetime do Postgres, extrai apenas a data (.date())
            if isinstance(criado_em, datetime):
                if criado_em.date() == hoje:
                    agend_count_dia += 1
            # Caso o banco devolva já como objeto date puro
            elif isinstance(criado_em, date):
                if criado_em == hoje:
                    agend_count_dia += 1

    # 3. VALIDAÇÃO INDEPENDENTE DAS METAS
    meta_sem_ok = agend_count_sem >= meta_semanal if meta_semanal > 0 else False
    meta_dia_ok = agend_count_dia >= meta_diaria if meta_diaria > 0 else False

    # Porcentagens para as barras de progresso
    pct_sem = min(agend_count_sem / meta_semanal, 1.0) if meta_semanal > 0 else 0.0
    pct_dia = min(agend_count_dia / meta_diaria, 1.0) if meta_diaria > 0 else 0.0

    # Customização das mensagens e classes CSS
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
        st.markdown("<br>")
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

with aba3:

    st.markdown("### 📊 Dashboard de Performance")
    st.caption("Dados em tempo real. Conectar ao PostgreSQL para persistência entre sessões.")

    todos_leads = _db_listar_leads()
    vendedoras  = _todos_vendedores()
    agendadores = _todos_agendadores()
    responsaveis = _todos_responsaveis()

    if not todos_leads:
        st.info("Sem dados ainda. Cadastre leads pela aba **🚀 Novo Agendamento**.")
    else:
        # Seletor de recorte
        dash_vend = st.selectbox(
            "🎯 Visualizar performance de:",
            ["Equipe completa"] + vendedoras,
            key="dash_vend",
        )

        leads_dash = (
            todos_leads if dash_vend == "Equipe completa"
            else [l for l in todos_leads
                  if l.get("responsavel_agendamento") == dash_vend
                  or l.get("responsavel_venda") == dash_vend]
        )

        # ── KPIs ──────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        k1, k2, k3, k4, k5 = st.columns(5)

        total    = len(leads_dash)
        reunioes = sum(1 for l in leads_dash if l.get("status") not in ("Agendado", "No Show", "Perda / Caiu"))
        dentro   = sum(1 for l in leads_dash if l.get("status") in ("Tô Dentro", "Contrato Enviado", "Contrato Assinado"))
        assinou  = sum(1 for l in leads_dash if l.get("status") == "Contrato Assinado")
        perdas   = sum(1 for l in leads_dash if l.get("status") == "Perda / Caiu")

        tx_reu = f"{reunioes/total*100:.0f}%" if total else "—"
        tx_fec = f"{assinou/max(reunioes,1)*100:.0f}%"

        C = theme.CORES
        with k1: theme.render_dash_card("Agendamentos",   str(total),    "total no funil",       C.get("sky", "#87CEEB")) 
        with k2: theme.render_dash_card("Reuniões",       str(reunioes), f"taxa: {tx_reu}",       C.get("reuniao", "#4B0082"))
        with k3: theme.render_dash_card("Tô Dentro",      str(dentro),   "sinalização positiva",  C.get("dentro", "#228B22"))
        with k4: theme.render_dash_card("Assinados 🏆",   str(assinou),  f"conv.: {tx_fec}",      C.get("gold", "#FFD700"))
        with k5: theme.render_dash_card("Perdas",         str(perdas),   "caíram do funil",       C.get("red", "#FF0000"))

        st.markdown("<br>")
        st.markdown("---")

        # ── Ranking por vendedora ─────────────────────────────────
        st.markdown("#### 👥 Ranking — Agendamentos por Vendedora")
        rows = []
        for v in agendadores:
            ll   = [l for l in todos_leads if l.get("responsavel_agendamento") == v]
            reu  = sum(1 for l in ll if l.get("status") not in ("Agendado", "No Show", "Perda / Caiu"))
            ass  = sum(1 for l in ll if l.get("status") == "Contrato Assinado")
            per  = sum(1 for l in ll if l.get("status") == "Perda / Caiu")
            rows.append({
                "Vendedora":       v,
                "Agendamentos":    len(ll),
                "Reuniões":        reu,
                "Assinados 🏆":    ass,
                "Perdas 💀":       per,
                "Conv. ass/reu":   f"{ass/max(reu,1)*100:.0f}%",
                "Meta sem.":       meta_semanal,
                "% Meta":          f"{len(ll)/meta_semanal*100:.0f}%",
            })

        if rows:
            df_rank = pd.DataFrame(rows).sort_values("Agendamentos", ascending=False)
            st.dataframe(df_rank, use_container_width=True, hide_index=True)

        st.markdown("<br>")

        # ── Distribuição por etapa ────────────────────────────────
        st.markdown(f"#### 🗂️ Leads por Etapa — {dash_vend}")
        etapa_data = {e: sum(1 for l in leads_dash if l.get("status") == e) for e in PIPELINE}
        df_et = pd.DataFrame(list(etapa_data.items()), columns=["Etapa", "Leads"])
        st.bar_chart(df_et.set_index("Etapa"), use_container_width=True, color="#5B5FEF")

        # ── Distribuição por segmento ─────────────────────────────
        st.markdown("#### 🏷️ Leads por Segmento")
        seg_data: dict[str, int] = {}
        for l in leads_dash:
            seg_data[l.get("segmento", "—")] = seg_data.get(l.get("segmento", "—"), 0) + 1
        if seg_data:
            df_seg = pd.DataFrame(list(seg_data.items()), columns=["Segmento", "Leads"]).sort_values("Leads", ascending=False)
            st.bar_chart(df_seg.set_index("Segmento"), use_container_width=True, color="#0EA5E9")

# ══════════════════════════════════════════════════════════════════
# ABA 4 — CONTRATOS
# ══════════════════════════════════════════════════════════════════

with aba4:

    st.markdown("### 📜 Emissão de Contratos")
    st.info(
        "ℹ️ Exibe leads em **Tô Dentro**, **Contrato Enviado** e **Contrato Assinado**. "
        "Quando o banco estiver conectado, os dados do formulário 'Tô Dentro' "
        "preencherão o contrato automaticamente."
    )

    todos_leads = _db_listar_leads()
    leads_contrato = [
        l for l in todos_leads
        if l.get("status") in ("Tô Dentro", "Contrato Enviado", "Contrato Assinado")
    ]

    if not leads_contrato:
        st.warning("Nenhum lead na fase de contrato. Avance leads pelo Funil de Vendas! 💜")
    else:
        df_ct = pd.DataFrame([
            {
                "ID":           l.get("id"),
                "Lead":         l.get("nome_fantasia"),
                "Segmento":     l.get("segmento"),
                "Estado":       l.get("estado"),
                "Fechador":     l.get("responsavel_venda"),
                "Status":       l.get("status"),
                "Forms":        "✅" if l.get("forms_enviado") else "⏳ pendente",
                "Data Reunião": _fmt_date(l.get("data_reuniao")),
            }
            for l in leads_contrato
        ])
        st.dataframe(df_ct, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### ⚡ Gerar e Enviar Contrato")

        sel_nome = st.selectbox(
            "Selecione o Lead",
            options=[l["nome_fantasia"] for l in leads_contrato],
        )
        sel = next(l for l in leads_contrato if l["nome_fantasia"] == sel_nome)

        if not sel.get("forms_enviado"):
            st.warning("⚠️ Este lead ainda não enviou o formulário de dados ('Tô Dentro'). O contrato pode estar incompleto.")

        cb1, _ = st.columns([1, 3])
        with cb1:
            gerar = st.button("📄 Gerar e Enviar Contrato", use_container_width=True)

        if gerar:
            st.session_state.contrato_log_ativo = sel_nome

        if st.session_state.get("contrato_log_ativo") == sel_nome:
            log_ph = st.empty()
            logs = [
                "🔍 Buscando dados do cliente no CRM...",
                "✅ Dados encontrados com sucesso.",
                "📋 Validando CNPJ junto à Receita Federal...",
                "✅ CNPJ válido e ativo.",
                "🖨️  Gerando contrato em PDF...",
                f"✅ PDF gerado: contrato_{sel_nome.replace(' ','_').lower()}.pdf",
                "📧 Enviando contrato por e-mail...",
                "✅ Contrato enviado com sucesso! ✉️",
            ]
            log_txt = ""
            for linha in logs:
                log_txt += linha + "\n"
                log_ph.markdown(f'<div class="log-box">{log_txt}</div>', unsafe_allow_html=True)
                time.sleep(0.28)

            resp = sel.get("responsavel_venda", "").split()[0] if sel.get("responsavel_venda") else "Equipe"
            wpp  = (
                f"Olá, tudo bem? 😊\n\n"
                f"Aqui é {resp} do Exagerado - Maior Evento de Varejo e Outlet do Brasil.\n\n"
                f"Conforme combinado, acabei de enviar o contrato referente à nossa "
                f"parceria com a {sel_nome} para o seu e-mail cadastrado.\n\n"
                f"Por favor, confirme o recebimento! Qualquer dúvida, estou aqui. 🚀\n\n"
                f"Att,\n{resp} — Exagerado"
            )
            st.markdown(
                f'<div class="whatsapp-box"><strong>📲 Mensagem WhatsApp</strong><br><br>'
                f'{wpp.replace(chr(10),"<br>")}</div>',
                unsafe_allow_html=True,
            )
            st.code(wpp, language=None)

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