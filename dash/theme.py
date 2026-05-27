"""
theme.py
════════
Camada visual - Tema Meu Exagerado
Paleta: off-white #FAF9F7 · rosa #E54E88 · roxo #2D1B3D

"""

import streamlit as st
from datetime import date as _date

# ──────────────────────────────────────────────────────────────────
# PALETA
# ──────────────────────────────────────────────────────────────────

CORES = {
    "bg_main":    "#FAF9F7",
    "bg_card":    "#FFFFFF",
    "bg_subtle":  "#F3F0ED",
    "bg_input":   "#FFFFFF",
    "rosa":       "#E54E88",
    "rosa_light": "#FCEEF4",
    "rosa_hover": "#CC3D75",
    "roxo":       "#2D1B3D",
    "roxo_soft":  "#5C3D7A",
    "agendado":   "#3B82F6",
    "show":       "#8B5CF6",
    "perda":      "#EF4444",
    "reuniao":    "#F59E0B",
    "dentro":     "#E54E88",
    "contrato":   "#6366F1",
    "assinado":   "#D97706",
    "green":      "#059669",
    "red":        "#EF4444",
    "orange":     "#F59E0B",
    "gold":       "#D97706",
    "wpp":        "#25D366",
    "text":       "#2D1B3D",
    "text_sec":   "#4B3A5A",
    "muted":      "#9E8FAD",
    "border":     "#EAE4F0",
    "border_md":  "#D4C8E2",
}

ETAPA_VISUAL = {
    "Agendado":          {"emoji": "📅", "css": "col-agendado",  "cor": CORES["agendado"]},
    "No Show":              {"emoji": "🎬", "css": "col-show",      "cor": CORES["show"]},
    "Perda / Caiu":      {"emoji": "💀", "css": "col-perda",     "cor": CORES["perda"]},
    "Reunião Realizada": {"emoji": "🤝", "css": "col-reuniao",   "cor": CORES["reuniao"]},
    "Tô Dentro":         {"emoji": "🔥", "css": "col-dentro",    "cor": CORES["dentro"]},
    "Contrato Enviado":  {"emoji": "📨", "css": "col-contrato",  "cor": CORES["contrato"]},
    "Contrato Assinado": {"emoji": "🏆", "css": "col-assinado",  "cor": CORES["assinado"]},
}

_CSS = """
<style>
/* ════════════════════════════════════════════════
   FONTES
════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* ════════════════════════════════════════════════
   VARIÁVEIS GLOBAIS
════════════════════════════════════════════════ */
:root {
    --bg-main:    #FAF9F7;
    --bg-card:    #FFFFFF;
    --bg-subtle:  #F3F0ED;
    --bg-input:   #FFFFFF;
    --rosa:       #E54E88;
    --rosa-light: #FCEEF4;
    --rosa-hover: #CC3D75;
    --roxo:       #2D1B3D;
    --roxo-soft:  #5C3D7A;
    --text:       #2D1B3D;
    --text-sec:   #4B3A5A;
    --muted:      #9E8FAD;
    --border:     #EAE4F0;
    --border-md:  #D4C8E2;
    --green:      #059669;
    --red:        #EF4444;
    --orange:     #F59E0B;
    --gold:       #D97706;
    --wpp:        #25D366;
    --shadow-sm:  0 1px 3px rgba(45,27,61,.07), 0 1px 2px rgba(45,27,61,.04);
    --shadow-md:  0 4px 16px rgba(45,27,61,.10);
    --shadow-rosa:0 4px 16px rgba(229,78,136,.28);
}

/* ════════════════════════════════════════════════
   RESET GLOBAL — força fundo off-white em TODA
   a árvore de containers do Streamlit
════════════════════════════════════════════════ */
html, body { background-color: var(--bg-main) !important; }

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
section[data-testid="stSidebar"],
div[class*="main"],
div[class*="block-container"] {
    background-color: var(--bg-main) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Formulários têm fundo branco */
[data-testid="stForm"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ════════════════════════════════════════════════
   INPUTS — CORREÇÃO COMPLETA
   Cobre text_input, number_input, date_input,
   selectbox e seus estados internos
════════════════════════════════════════════════ */

/* Wrapper geral de qualquer input */
.stTextInput,
.stNumberInput,
.stDateInput,
.stSelectbox,
.stMultiSelect {
    color: var(--text) !important;
}

/* Todos os <input> e <textarea> */
input,
textarea,
input[type="text"],
input[type="number"],
input[type="date"],
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="textarea"] textarea {
    background-color: var(--bg-input) !important;
    background:       var(--bg-input) !important;
    color:            var(--text)     !important;
    border-color:     var(--border-md) !important;
    border-radius:    9px !important;
    font-family:      'Inter', sans-serif !important;
    font-size:        0.9rem !important;
    caret-color:      var(--rosa) !important;
    -webkit-text-fill-color: var(--text) !important;
}

/* Placeholder visível */
input::placeholder,
textarea::placeholder,
[data-baseweb="input"] input::placeholder {
    color: var(--muted) !important;
    opacity: 1 !important;
    -webkit-text-fill-color: var(--muted) !important;
}

/* Wrappers dos inputs (baseweb) */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"],
[data-baseweb="input"] > div,
[data-baseweb="base-input"] > div {
    background-color: var(--bg-input) !important;
    background:       var(--bg-input) !important;
    border-color:     var(--border-md) !important;
    border-radius:    9px !important;
}

/* Focus ring rosa */
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within {
    border-color: var(--rosa) !important;
    box-shadow: 0 0 0 3px rgba(229,78,136,.14) !important;
}

/* number_input — botões + e - */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"],
button[aria-label="increment"],
button[aria-label="decrement"] {
    background-color: var(--bg-subtle) !important;
    color:            var(--text-sec) !important;
    border-color:     var(--border-md) !important;
    border-radius:    6px !important;
}
[data-testid="stNumberInput"] button:hover,
button[aria-label="increment"]:hover,
button[aria-label="decrement"]:hover {
    background-color: var(--rosa-light) !important;
    color:            var(--rosa) !important;
}

/* date_input */
[data-testid="stDateInput"] input,
[data-baseweb="datepicker"] input,
input[type="date"] {
    background-color: var(--bg-input) !important;
    color:            var(--text)     !important;
    -webkit-text-fill-color: var(--text) !important;
    border-radius:    9px !important;
}

/* Selectbox container e dropdown */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {
    background-color: var(--bg-input) !important;
    border-color:     var(--border-md) !important;
    border-radius:    9px !important;
    color:            var(--text)      !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    color: var(--text) !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"],
[data-baseweb="menu"] ul {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-md) !important;
}
[data-baseweb="menu"] li,
[role="option"] {
    background-color: var(--bg-card) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}
[data-baseweb="menu"] li:hover,
[role="option"]:hover {
    background-color: var(--rosa-light) !important;
    color: var(--rosa) !important;
}

/* ════════════════════════════════════════════════
   PAGE HEADER
════════════════════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, #E54E88 0%, #C23A73 100%);
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 3px 16px rgba(229,78,136,.35);
}
.page-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem;
    font-weight: 700;
    color: #FFFFFF !important;
    margin: 0;
}
.page-header .subtitle {
    margin: 2px 0 0 0;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.75);
}
.page-header .badge {
    background: rgba(255,255,255,0.22);
    color: #fff;
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border: 1px solid rgba(255,255,255,0.38);
    align-self: flex-start;
    margin-top: 4px;
}

/* ════════════════════════════════════════════════
   TABS
════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    padding: 8px 18px !important;
    transition: all 0.18s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--rosa-light) !important;
    color: var(--rosa) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--rosa) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-rosa) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem !important; }

/* ════════════════════════════════════════════════
   KANBAN — HEADERS
════════════════════════════════════════════════ */
.kanban-header {
    text-align: center;
    padding: 8px 6px;
    border-radius: 9px;
    margin-bottom: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}
.col-agendado { background:#EFF6FF; border:1.5px solid #3B82F6; color:#1D4ED8 !important; }
.col-show     { background:#F5F3FF; border:1.5px solid #8B5CF6; color:#6D28D9 !important; }
.col-perda    { background:#FFF1F2; border:1.5px solid #EF4444; color:#B91C1C !important; }
.col-reuniao  { background:#FFFBEB; border:1.5px solid #F59E0B; color:#B45309 !important; }
.col-dentro   { background:#FCEEF4; border:1.5px solid #E54E88; color:#C23A73 !important; }
.col-contrato { background:#EEF2FF; border:1.5px solid #6366F1; color:#4338CA !important; }
.col-assinado { background:#FEF3C7; border:1.5px solid #D97706; color:#92400E !important; }

/* ════════════════════════════════════════════════
   KANBAN — CARDS
════════════════════════════════════════════════ */
.lead-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 13px 15px;
    margin-bottom: 9px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.18s, border-color 0.18s, transform 0.12s;
}
.lead-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--border-md);
    transform: translateY(-1px);
}
.lead-card-perda {
    border-color: #FECACA !important;
    background: #FFF8F8 !important;
    opacity: 0.78;
}
.lead-card-winner {
    border-color: #FDE68A !important;
    background: linear-gradient(135deg, #FFFEF5, #FFFBEB) !important;
    box-shadow: 0 0 0 1.5px #FDE68A, 0 4px 14px rgba(217,119,6,.14) !important;
}
.lead-card h4 {
    margin: 0 0 5px 0;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--roxo);
}
.lead-card .meta {
    font-size: 0.72rem;
    color: var(--muted);
    margin: 2px 0;
    line-height: 1.45;
}
.lead-card .meta b { color: var(--text-sec); font-weight: 500; }

/* ════════════════════════════════════════════════
   TAGS
════════════════════════════════════════════════ */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.62rem;
    font-weight: 600;
    margin-top: 5px;
    margin-right: 3px;
}
.tag-seg    { background:#F3EEFF; color:#5C3D7A; border:1px solid #D4C8E2; }
.tag-lista  { background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; }
.tag-dentro { background:var(--rosa-light); color:var(--rosa-hover); border:1px solid #F4A7C8; }

/* ════════════════════════════════════════════════
   PROGRESS BOX
════════════════════════════════════════════════ */
.progress-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--rosa);
    border-radius: 12px;
    padding: 1.1rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow-sm);
}
.progress-box h3 {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}
.progress-box .count {
    font-family: 'Space Mono', monospace;
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--rosa);
    line-height: 1;
}
.progress-box .count span { color: var(--muted); font-size: 0.9rem; }
.progress-box .hint { font-size: 0.76rem; color: var(--muted); margin: 5px 0 8px 0; }
.progress-box .hint.ok { color: var(--green); font-weight: 600; }

/* ════════════════════════════════════════════════
   FORM SECTION TITLE
════════════════════════════════════════════════ */
.form-section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--rosa);
    margin: 1.2rem 0 0.5rem 0;
    padding-bottom: 5px;
    border-bottom: 1.5px solid var(--border);
}

/* ════════════════════════════════════════════════
   LABELS DOS INPUTS (emojis + texto acima do campo)
════════════════════════════════════════════════ */
label[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"],
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stMultiSelect label,
.stCheckbox label {
    color: var(--text-sec) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ════════════════════════════════════════════════
   BOTÕES
════════════════════════════════════════════════ */
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--text-sec) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.16s ease !important;
}
.stButton > button:hover {
    background: var(--rosa-light) !important;
    color: var(--rosa) !important;
    border-color: var(--rosa) !important;
}
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #E54E88, #C23A73) !important;
    color: #fff !important;
    border: none !important;
    padding: 0.65rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-rosa) !important;
    font-family: 'Inter', sans-serif !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(229,78,136,.45) !important;
}

/* ════════════════════════════════════════════════
   BARRA DE PROGRESSO
════════════════════════════════════════════════ */
[data-testid="stProgressBar"] > div,
.stProgress > div > div > div > div,
div[role="progressbar"] > div {
    background: linear-gradient(90deg, var(--rosa), #C23A73) !important;
    border-radius: 99px !important;
}
.stProgress > div > div > div,
div[role="progressbar"] {
    background: var(--border) !important;
    border-radius: 99px !important;
}

/* ════════════════════════════════════════════════
   MÉTRICAS
════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    box-shadow: var(--shadow-sm) !important;
}

/* 1. Alvo na div de label por atributo (independente do hash do Emotion Cache) */
[data-testid="metric-container"] div[data-testid="stMetricLabel"] {
    color: #2D1B3D !important;
}

/* 2. XEQUE-MATE: Caça qualquer div interna do Emotion Cache que o Streamlit inventar ali dentro */
[data-testid="metric-container"] div[class^="st-emotion-cache-"] {
    color: #2D1B3D !important;
}

/* 3. Força as propriedades de texto no rótulo e em QUALQUER elemento filho dele */
[data-testid="metric-container"] [data-testid="stMetricLabel"],
[data-testid="metric-container"] [data-testid="stMetricLabel"] * {
    color: #2D1B3D !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Mantém o número funcionando em Rosa */
[data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricValue"] div,
[data-testid="metric-container"] [data-testid="stMetricValue"] * {
    color: var(--rosa) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}

/* ════════════════════════════════════════════════
   DASHBOARD CARDS
════════════════════════════════════════════════ */
.dash-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.18s;
}
.dash-card:hover { box-shadow: var(--shadow-md); }
.dash-card .label {
    font-size: 0.63rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.8px;
    font-family: 'Space Mono', monospace;
    margin-bottom: 5px;
}
.dash-card .value {
    font-size: 2.2rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    line-height: 1.05;
}
.dash-card .sub {
    font-size: 0.71rem;
    color: var(--muted);
    margin-top: 3px;
}

/* ════════════════════════════════════════════════
   CHECKBOX
════════════════════════════════════════════════ */
.stCheckbox label p {
    color: var(--text-sec) !important;
    font-size: 0.88rem !important;
}

/* ════════════════════════════════════════════════
   ALERTS
════════════════════════════════════════════════ */
[data-testid="stAlert"],
div[role="alert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}
/* warning */
[data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
.stWarning {
    background: #FFF9EC !important;
    border-left: 4px solid var(--orange) !important;
    color: #92400E !important;
}
/* info */
[data-testid="stAlert"][data-baseweb="notification"][kind="info"],
.stInfo {
    background: var(--rosa-light) !important;
    border-left: 4px solid var(--rosa) !important;
    color: var(--roxo-soft) !important;
}
/* success */
[data-testid="stAlert"][data-baseweb="notification"][kind="success"],
.stSuccess {
    background: #ECFDF5 !important;
    border-left: 4px solid var(--green) !important;
    color: #065F46 !important;
}
/* error */
[data-testid="stAlert"][data-baseweb="notification"][kind="error"],
.stError {
    background: #FFF1F2 !important;
    border-left: 4px solid var(--red) !important;
    color: #B91C1C !important;
}

/* ════════════════════════════════════════════════
   EXPANDER
════════════════════════════════════════════════ */
[data-testid="stExpander"],
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-sec) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
[data-testid="stExpander"] > div {
    background: var(--bg-card) !important;
}

/* ════════════════════════════════════════════════
   DATAFRAME / TABELAS
════════════════════════════════════════════════ */
.stDataFrame,
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--border) !important;
}

/* ════════════════════════════════════════════════
   LOG / CONTRATO
════════════════════════════════════════════════ */
.log-box {
    background: #F0FDF4;
    border: 1.5px solid #6EE7B7;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.73rem;
    color: #065F46;
    line-height: 1.9;
    white-space: pre-line;
}
.whatsapp-box {
    background: #F0FFF6;
    border: 1.5px solid #25D366;
    border-radius: 10px;
    padding: 1rem 1.3rem;
    font-size: 0.85rem;
    color: #14532D;
    line-height: 1.75;
    margin-top: 1rem;
}
.whatsapp-box strong { color: #16A34A; }

/* ════════════════════════════════════════════════
   MISC
════════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1.5px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* Texto geral que pode ficar claro */
p, span, li, td, th, div {
    color: inherit;
}

/* code blocks */
code, [data-testid="stCode"] {
    background: var(--bg-subtle) !important;
    color: var(--roxo) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* ════════════════════════════════════════════════
   FOOTER
════════════════════════════════════════════════ */
.footer {
    text-align: center;
    font-size: 0.67rem;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    padding: 12px 0 6px 0;
    margin-top: 2.5rem;
    border-top: 1px solid var(--border);
    letter-spacing: 0.5px;
}
</style>
"""

# ──────────────────────────────────────────────────────────────────
# API PÚBLICA
# ──────────────────────────────────────────────────────────────────

def apply() -> None:
    """
    Injeta CSS global + força tema claro via config.
    """
    st.markdown(
        """
        <style>
        /* Força o navegador a renderizar a árvore em modo claro, 
           exatamente como o botão de simulação do Firefox faz */
        :root {
            color-scheme: light !important;
        }
        html, body, .stApp {
            color-scheme: light !important;
        }
        @media (prefers-color-scheme: dark) {
            html, body, .stApp {
                color-scheme: light !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(_CSS, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, badge: str = "demo") -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1>⚡ {title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            <span class="badge">{badge}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kanban_header(etapa: str, contagem: int) -> None:
    v = ETAPA_VISUAL.get(etapa, {"emoji": "•", "css": "col-agendado"})
    st.markdown(
        f'<div class="kanban-header {v["css"]}">'
        f'{v["emoji"]} {etapa}'
        f'<span style="opacity:.5;color:#171515;font-size:0.88em;margin-left:4px;">({contagem})</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_lead_card(lead: dict) -> None:
    etapa   = lead.get("status", "")
    is_win  = etapa == "Contrato Assinado"
    is_loss = etapa == "Perda / Caiu"
    is_den  = etapa == "Tô Dentro"

    card_class = (
        "lead-card lead-card-winner" if is_win else
        "lead-card lead-card-perda"  if is_loss else
        "lead-card"
    )

    data_fmt = (
        lead["data_reuniao"].strftime("%d/%m/%Y")
        if isinstance(lead.get("data_reuniao"), _date)
        else str(lead.get("data_reuniao", "—"))
    )

    prefix    = "🏆 " if is_win else ("💀 " if is_loss else ("🔥 " if is_den else ""))
    tag_lista = '<span class="tag tag-lista">⚡ Lista</span>' if lead.get("origem_lista") else ""
    tag_forms = '<span class="tag tag-dentro">📋 Forms OK</span>' if lead.get("forms_enviado") else ""

    st.markdown(
        f"""
        <div class="{card_class}">
            <h4>{prefix}{lead.get('nome_fantasia', '—')}</h4>
            <p class="meta">📅 {data_fmt} &nbsp;|&nbsp; 📍 {lead.get('estado', '—')}</p>
            <p class="meta">👤 Agend.: <b>{lead.get('responsavel_agendamento', '—')}</b></p>
            <p class="meta">🤝 Fecha.: <b>{lead.get('responsavel_venda', '—')}</b></p>
            <span class="tag tag-seg">{lead.get('segmento', '—')}</span>
            {tag_lista}{tag_forms}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dash_card(label: str, value: str, sub: str = "", cor: str = "#E54E88") -> None:
    st.markdown(
        f"""
        <div class="dash-card">
            <div class="label">{label}</div>
            <div class="value" style="color:{cor};">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<div class="footer"> github.com/kauadp · linkedin.com/in/kauadp</div>',
        unsafe_allow_html=True,
    )