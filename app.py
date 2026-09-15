import base64
import re
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import (
    current_user_email,
    current_user_id,
    get_supabase_client,
    get_supabase_settings,
    is_logged_in,
    login,
    logout,
    send_password_reset,
    signup,
)
from database import (
    add_savings_movement,
    add_transaction,
    create_savings_goal,
    delete_savings_goal,
    delete_transaction,
    get_savings_goals,
    get_savings_history,
    get_transactions,
)

st.set_page_config(
    page_title="FinTrack",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CATEGORIES = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Educação",
    "Lazer",
    "Compras",
    "Contas",
    "Salário",
    "Investimentos",
    "Outros",
]


def brl(value):
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def load_logo_base64():
    logo_path = Path(__file__).parent / "assets" / "fintrack-logo.svg"
    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def page_header(title, subtitle):
    st.markdown(f"## {title}")
    st.caption(subtitle)


st.markdown(
    """
    <style>
    :root {
        --bg: #F5F6F8;
        --surface: #FFFFFF;
        --text: #172033;
        --muted: #667085;
        --border: #E4E7EC;
        --primary: #172033;
        --positive: #16855C;
        --negative: #BB3E4B;
    }

    .stApp { background: var(--bg); color: var(--text); }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stHeader"] { background: rgba(245,246,248,.96); }

    .block-container {
        max-width: 1220px;
        padding-top: 3.5rem !important;
        padding-bottom: 3rem;
    }

    .ft-brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px 18px;
        box-shadow: 0 8px 24px rgba(16,24,40,.05);
        margin-bottom: 16px;
    }

    .ft-brand-left {
        display: flex;
        align-items: center;
        gap: 13px;
        min-width: 0;
    }

    .ft-logo {
        width: 48px;
        height: 48px;
        flex: 0 0 auto;
    }

    .ft-name {
        color: var(--text);
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: -.035em;
        line-height: 1;
    }

    .ft-tag {
        color: var(--muted);
        font-size: .86rem;
        margin-top: 6px;
    }

    .ft-user {
        color: #344054;
        background: #F8FAFC;
        border: 1px solid #D9DEE7;
        border-radius: 999px;
        padding: 8px 12px;
        font-size: .78rem;
        font-weight: 700;
        max-width: 320px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        box-shadow: 0 5px 16px rgba(16,24,40,.035);
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 14px;
        min-height: 110px;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 800 !important;
        letter-spacing: -.03em;
    }

    div[data-testid="stMetricLabel"] p,
    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 14px;
    }

    button[data-baseweb="tab"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 11px !important;
        min-height: 43px;
        padding: 0 15px !important;
        color: #475467 !important;
        font-weight: 700 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary) !important;
        border-color: var(--primary) !important;
        color: #FFFFFF !important;
    }

    button[data-baseweb="tab"] p { color: inherit !important; }

    .stButton > button, .stFormSubmitButton > button {
        border-radius: 11px !important;
        min-height: 44px;
        font-weight: 700 !important;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: #344054 !important;
        font-weight: 650 !important;
    }

    .auth-page {
        position: relative;
        min-height: 72vh;
        overflow: hidden;
        border-radius: 28px;
        padding: 8px 8px 26px;
        margin-top: -8px;
    }

    .auth-page::before,
    .auth-page::after {
        content: "";
        position: absolute;
        border-radius: 999px;
        pointer-events: none;
        z-index: 0;
    }

    .auth-page::before {
        width: 340px;
        height: 340px;
        right: -170px;
        top: 190px;
        background: linear-gradient(135deg, rgba(219,231,247,.46), rgba(239,244,251,.08));
        transform: rotate(-18deg);
    }

    .auth-page::after {
        width: 300px;
        height: 300px;
        left: -170px;
        bottom: -145px;
        background: linear-gradient(135deg, rgba(222,233,248,.44), rgba(244,247,251,.08));
    }

    .auth-topbar {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 8px 2px 24px;
    }

    .auth-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.45rem;
        font-weight: 850;
        color: var(--text);
        letter-spacing: -.035em;
    }

    .auth-brand img {
        width: 46px;
        height: 46px;
    }

    .auth-topmeta {
        color: var(--muted);
        font-size: .84rem;
        font-weight: 650;
    }

    .auth-wrap {
        position: relative;
        z-index: 1;
        max-width: 610px;
        margin: 1.4rem auto 0;
    }

    .auth-card {
        background: rgba(255,255,255,.97);
        border: 1px solid #E1E6EF;
        border-radius: 24px;
        padding: 32px 30px 28px;
        text-align: center;
        box-shadow: 0 22px 55px rgba(23,32,51,.09);
        margin-bottom: 22px;
    }

    .auth-logo {
        width: 72px;
        height: 72px;
        margin-bottom: 14px;
        filter: drop-shadow(0 8px 14px rgba(23,32,51,.10));
    }

    .auth-title {
        font-size: 2rem;
        font-weight: 850;
        color: var(--text);
        letter-spacing: -.04em;
        line-height: 1.1;
    }

    .auth-subtitle {
        color: var(--muted);
        margin: 10px auto 0;
        line-height: 1.55;
        max-width: 470px;
        font-size: .98rem;
    }

    .auth-features {
        position: relative;
        z-index: 1;
        max-width: 760px;
        margin: 24px auto 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        color: #667085;
        font-size: .82rem;
        font-weight: 650;
    }

    .auth-feature {
        padding: 0 22px;
        white-space: nowrap;
    }

    .auth-feature + .auth-feature {
        border-left: 1px solid #D9DEE7;
    }

    .auth-feature strong {
        color: #344054;
        margin-right: 6px;
    }

    .auth-panel-note {
        text-align: center;
        color: #98A2B3;
        font-size: .8rem;
        margin: 8px 0 4px;
    }

    .logout-footer {
        margin-top: 34px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
    }

    @media (max-width: 760px) {
        .block-container { padding: 3.2rem .8rem 2rem !important; }

        .ft-brand {
            padding: 12px;
            border-radius: 15px;
        }

        .ft-logo { width: 42px; height: 42px; }
        .ft-name { font-size: 1.18rem; }
        .ft-tag { font-size: .8rem; }

        .ft-user {
            max-width: 42vw;
            font-size: .72rem;
        }

        .auth-page {
            min-height: auto;
            padding: 2px 0 14px;
            overflow: visible;
        }

        .auth-topbar {
            padding: 2px 2px 16px;
        }

        .auth-brand {
            font-size: 1.2rem;
            gap: 9px;
        }

        .auth-brand img {
            width: 40px;
            height: 40px;
        }

        .auth-topmeta { display: none; }

        .auth-wrap {
            margin-top: .45rem;
            max-width: 100%;
        }

        .auth-card {
            padding: 25px 18px 22px;
            border-radius: 20px;
            margin-bottom: 16px;
        }

        .auth-logo {
            width: 62px;
            height: 62px;
        }

        .auth-title {
            font-size: 1.65rem;
        }

        .auth-subtitle {
            font-size: .91rem;
        }

        .auth-features {
            flex-direction: column;
            align-items: stretch;
            gap: 9px;
            margin: 18px auto 4px;
            text-align: center;
        }

        .auth-feature {
            padding: 0;
        }

        .auth-feature + .auth-feature {
            border-left: 0;
        }

        input, textarea, select { font-size: 16px !important; }
        .stButton > button, .stFormSubmitButton > button { width: 100%; }
    }

    @media (max-width: 560px) {
        .ft-brand {
            flex-direction: column;
            align-items: stretch;
        }

        .ft-user {
            width: 100%;
            max-width: none;
            text-align: center;
            border-radius: 10px;
        }

        .ft-tag { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_b64 = load_logo_base64()
supabase_url, supabase_key = get_supabase_settings()

if not supabase_url or not supabase_key:
    st.markdown(
        f"""
        <div class="auth-wrap">
            <div class="auth-card">
                <img class="auth-logo" src="data:image/svg+xml;base64,{logo_b64}">
                <div class="auth-title">FinTrack ainda não está conectado ao Supabase</div>
                <div class="auth-subtitle">
                    Configure os Secrets do Streamlit com a URL e a Publishable key do projeto Supabase.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        '[supabase]\\nurl = "https://SEU-PROJETO.supabase.co"\\npublishable_key = "sb_publishable_..."',
        language="toml",
    )
    st.stop()

supabase = get_supabase_client()

if not is_logged_in():
    auth_html = (
        f'<div class="auth-page">'
        f'<div class="auth-topbar">'
        f'<div class="auth-brand">'
        f'<img src="data:image/svg+xml;base64,{logo_b64}">'
        f'<span>FinTrack</span>'
        f'</div>'
        f'<div class="auth-topmeta">Controle financeiro pessoal</div>'
        f'</div>'
        f'<div class="auth-wrap">'
        f'<div class="auth-card">'
        f'<img class="auth-logo" src="data:image/svg+xml;base64,{logo_b64}">'
        f'<div class="auth-title">Acesse o FinTrack</div>'
        f'<div class="auth-subtitle">'
        f'Entre para acompanhar suas despesas, receitas e metas em um só lugar, '
        f'de forma simples e organizada.'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(auth_html, unsafe_allow_html=True)

    auth_left, auth_center, auth_right = st.columns([1.15, 1.7, 1.15])

    with auth_center:
        with st.container(border=True):
            login_tab, signup_tab = st.tabs(["Entrar", "Criar conta"])

            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("E-mail", placeholder="voce@email.com")
                    password = st.text_input("Senha", type="password", placeholder="Sua senha")
                    submitted = st.form_submit_button(
                        "Entrar  →", type="primary", use_container_width=True
                    )

                    if submitted:
                        if not email.strip() or not password:
                            st.error("Informe e-mail e senha.")
                        else:
                            try:
                                if login(email, password):
                                    st.rerun()
                            except Exception:
                                st.error(
                                    "Não foi possível entrar. Verifique seus dados e confirme seu e-mail."
                                )

                with st.expander("Esqueceu sua senha?"):
                    reset_email = st.text_input(
                        "E-mail para recuperação", key="reset_email"
                    )
                    if st.button("Enviar recuperação", use_container_width=True):
                        if not reset_email.strip():
                            st.warning("Informe seu e-mail.")
                        else:
                            try:
                                send_password_reset(reset_email)
                                st.success(
                                    "Se a conta existir, as instruções serão enviadas por e-mail."
                                )
                            except Exception:
                                st.error("Não foi possível solicitar a recuperação.")

            with signup_tab:
                with st.form("signup_form"):
                    email = st.text_input(
                        "E-mail", placeholder="voce@email.com", key="signup_email"
                    )
                    password = st.text_input(
                        "Senha",
                        type="password",
                        key="signup_password",
                        placeholder="Crie uma senha forte",
                    )
                    password2 = st.text_input(
                        "Confirmar senha",
                        type="password",
                        key="signup_password2",
                        placeholder="Digite a senha novamente",
                    )
                    submitted = st.form_submit_button(
                        "Criar conta", type="primary", use_container_width=True
                    )

                    if submitted:
                        if not email.strip():
                            st.error("Informe seu e-mail.")
                        elif len(password) < 12:
                            st.error("A senha deve ter pelo menos 12 caracteres.")
                        elif not re.search(r"[a-z]", password):
                            st.error("A senha deve conter pelo menos uma letra minúscula.")
                        elif not re.search(r"[A-Z]", password):
                            st.error("A senha deve conter pelo menos uma letra maiúscula.")
                        elif not re.search(r"\d", password):
                            st.error("A senha deve conter pelo menos um número.")
                        elif not re.search(r"[^A-Za-z0-9]", password):
                            st.error("A senha deve conter pelo menos um símbolo.")
                        elif password != password2:
                            st.error("As senhas não coincidem.")
                        else:
                            try:
                                result = signup(email, password)
                                if result == "logged_in":
                                    st.rerun()
                                else:
                                    st.success(
                                        "Conta criada. Confirme o e-mail e depois faça login."
                                    )
                            except Exception:
                                st.error(
                                    "Não foi possível criar a conta. O e-mail pode já estar cadastrado."
                                )

            st.markdown(
                '<div class="auth-panel-note">Seus dados ficam associados somente à sua conta.</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="auth-features">
            <div class="auth-feature"><strong>▥</strong> Organize suas finanças</div>
            <div class="auth-feature"><strong>◎</strong> Acompanhe suas metas</div>
            <div class="auth-feature"><strong>◇</strong> Mantenha seus dados sincronizados</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()

user_id = current_user_id()
user_email = current_user_email()

st.markdown(
    f"""
    <div class="ft-brand">
        <div class="ft-brand-left">
            <img class="ft-logo" src="data:image/svg+xml;base64,{logo_b64}">
            <div>
                <div class="ft-name">FinTrack</div>
                <div class="ft-tag">Controle financeiro pessoal</div>
            </div>
        </div>
        <div class="ft-user">{user_email}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Seus dados ficam sincronizados com sua conta.")

df = get_transactions(supabase, user_id)
goals = get_savings_goals(supabase, user_id)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    total_income = float(df.loc[df["type"] == "Receita", "amount"].sum())
    total_expense = float(df.loc[df["type"] == "Despesa", "amount"].sum())
else:
    total_income = 0.0
    total_expense = 0.0

balance = total_income - total_expense
total_saved = float(goals["current_amount"].sum()) if not goals.empty else 0.0

tab_overview, tab_transactions, tab_goals = st.tabs(
    ["Visão geral", "Transações", "Metas e cofrinhos"]
)

with tab_overview:
    page_header("Visão geral", "Saldo, gastos e metas reunidos em um único painel.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Saldo disponível", brl(balance))
    m2.metric("Receitas", brl(total_income))
    m3.metric("Despesas", brl(total_expense))
    m4.metric("Guardado em metas", brl(total_saved))

    if df.empty:
        with st.container(border=True):
            st.subheader("Comece pela primeira transação")
            st.caption("Cadastre uma receita ou despesa na aba Transações.")
    else:
        c1, c2 = st.columns(2, gap="large")

        with c1:
            with st.container(border=True):
                st.subheader("Despesas por categoria")
                expenses = df[df["type"] == "Despesa"].copy()
                if expenses.empty:
                    st.info("Nenhuma despesa registrada.")
                else:
                    grouped = expenses.groupby("category", as_index=False)["amount"].sum()
                    fig = px.pie(grouped, names="category", values="amount", hole=.58)
                    fig.update_layout(
                        height=340,
                        margin=dict(l=8, r=8, t=8, b=8),
                        paper_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", y=-.08),
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with c2:
            with st.container(border=True):
                st.subheader("Fluxo mensal")
                monthly = df.copy()
                monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
                summary = monthly.groupby(["month", "type"], as_index=False)["amount"].sum()
                fig = px.bar(
                    summary,
                    x="month",
                    y="amount",
                    color="type",
                    barmode="group",
                    color_discrete_map={"Receita": "#16855C", "Despesa": "#BB3E4B"},
                    labels={"month": "Mês", "amount": "Valor", "type": ""},
                )
                fig.update_layout(
                    height=340,
                    margin=dict(l=8, r=8, t=8, b=8),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#EAECF0"),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab_transactions:
    page_header("Transações", "Registre e consulte suas receitas e despesas.")

    left, right = st.columns([1.1, .9], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Nova transação")
            with st.form("transaction_form", clear_on_submit=True):
                a, b = st.columns(2)
                with a:
                    description = st.text_input("Descrição", placeholder="Ex.: Supermercado")
                    amount = st.number_input("Valor (R$)", min_value=0.01, step=1.0, format="%.2f")
                with b:
                    tx_type = st.selectbox("Tipo", ["Despesa", "Receita"])
                    category = st.selectbox("Categoria", CATEGORIES)

                tx_date = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
                submitted = st.form_submit_button("Adicionar transação", type="primary", use_container_width=True)

                if submitted:
                    if not description.strip():
                        st.error("Informe uma descrição.")
                    else:
                        add_transaction(
                            supabase,
                            user_id,
                            description.strip(),
                            float(amount),
                            tx_type,
                            category,
                            tx_date.isoformat(),
                        )
                        st.success("Transação adicionada.")
                        st.rerun()

    with right:
        with st.container(border=True):
            st.subheader("Filtros")
            if df.empty:
                filtered = df.copy()
                st.info("Adicione uma transação para habilitar os filtros.")
            else:
                selected_type = st.selectbox("Tipo", ["Todos", "Receita", "Despesa"], key="f_type")
                categories = ["Todas"] + sorted(df["category"].dropna().unique().tolist())
                selected_category = st.selectbox("Categoria", categories, key="f_category")
                months = ["Todos"] + sorted(df["date"].dt.strftime("%m/%Y").unique().tolist(), reverse=True)
                selected_month = st.selectbox("Mês", months, key="f_month")

                filtered = df.copy()
                if selected_type != "Todos":
                    filtered = filtered[filtered["type"] == selected_type]
                if selected_category != "Todas":
                    filtered = filtered[filtered["category"] == selected_category]
                if selected_month != "Todos":
                    filtered = filtered[filtered["date"].dt.strftime("%m/%Y") == selected_month]

                st.caption(f"{len(filtered)} registro(s) encontrado(s).")

    with st.container(border=True):
        st.subheader("Histórico")
        if df.empty:
            st.info("Nenhuma transação cadastrada.")
        else:
            table = filtered.copy()
            table["Data"] = table["date"].dt.strftime("%d/%m/%Y")
            table["Valor"] = table.apply(
                lambda row: ("+ " if row["type"] == "Receita" else "- ") + brl(row["amount"]),
                axis=1,
            )
            table = table.rename(
                columns={"description": "Descrição", "type": "Tipo", "category": "Categoria"}
            )
            st.dataframe(
                table[["Data", "Descrição", "Tipo", "Categoria", "Valor"]],
                use_container_width=True,
                hide_index=True,
            )

    if not df.empty:
        with st.expander("Excluir transação"):
            options = {
                f"{row.id} — {row.date.strftime('%d/%m/%Y')} — {row.description} — {brl(row.amount)}": row.id
                for row in df.itertuples()
            }
            chosen = st.selectbox("Selecione a transação", list(options.keys()))
            if st.button("Excluir transação", use_container_width=True):
                delete_transaction(supabase, user_id, options[chosen])
                st.success("Transação excluída.")
                st.rerun()

with tab_goals:
    page_header("Metas e cofrinhos", "Planeje objetivos e acompanhe o dinheiro reservado.")

    create_col, summary_col = st.columns([1.05, .95], gap="large")

    with create_col:
        with st.container(border=True):
            st.subheader("Criar nova meta")
            use_deadline = st.toggle("Adicionar prazo", key="goal_use_deadline")

            with st.form("goal_form", clear_on_submit=True):
                goal_name = st.text_input("Nome da meta", placeholder="Ex.: Viagem")
                goal_target = st.number_input(
                    "Valor da meta (R$)", min_value=1.0, step=50.0, format="%.2f"
                )

                deadline = None
                if use_deadline:
                    deadline = st.date_input(
                        "Data limite",
                        value=date.today(),
                        min_value=date.today(),
                        format="DD/MM/YYYY",
                    ).isoformat()

                submitted = st.form_submit_button("Criar meta", type="primary", use_container_width=True)

                if submitted:
                    if not goal_name.strip():
                        st.error("Informe o nome da meta.")
                    else:
                        create_savings_goal(
                            supabase,
                            user_id,
                            goal_name.strip(),
                            float(goal_target),
                            deadline,
                        )
                        st.success("Meta criada.")
                        st.rerun()

    with summary_col:
        with st.container(border=True):
            st.subheader("Resumo das metas")
            if goals.empty:
                st.info("Nenhuma meta criada ainda.")
            else:
                total_target = float(goals["target_amount"].sum())
                progress = 0 if total_target <= 0 else min(total_saved / total_target, 1)
                completed = int((goals["current_amount"] >= goals["target_amount"]).sum())

                a, b = st.columns(2)
                a.metric("Total guardado", brl(total_saved))
                b.metric("Concluídas", completed)
                st.progress(progress)
                st.caption(f"{progress * 100:.0f}% de {brl(total_target)}")

    with st.container(border=True):
        st.subheader("Seus cofrinhos")

        if goals.empty:
            st.info("Crie sua primeira meta para começar.")
        else:
            for goal in goals.itertuples():
                pct = 0 if goal.target_amount <= 0 else float(goal.current_amount) / float(goal.target_amount)
                remaining = max(float(goal.target_amount) - float(goal.current_amount), 0)

                with st.container(border=True):
                    st.markdown(f"**{goal.name}**")
                    a, b, c = st.columns(3)
                    a.metric("Guardado", brl(goal.current_amount))
                    b.metric("Meta", brl(goal.target_amount))
                    c.metric("Falta", brl(remaining))
                    st.progress(min(max(pct, 0), 1))
                    if goal.deadline:
                        deadline_text = pd.to_datetime(goal.deadline).strftime("%d/%m/%Y")
                        st.caption(f"{pct * 100:.0f}% concluído · Prazo: {deadline_text}")
                    else:
                        st.caption(f"{pct * 100:.0f}% concluído · Sem prazo definido")

    if not goals.empty:
        goal_options = {
            f"{row.name} — {brl(row.current_amount)} / {brl(row.target_amount)}": row.id
            for row in goals.itertuples()
        }

        action_col, history_col = st.columns(2, gap="large")

        with action_col:
            with st.container(border=True):
                st.subheader("Movimentar cofrinho")
                selected_label = st.selectbox("Meta", list(goal_options.keys()), key="selected_goal")
                selected_goal_id = goal_options[selected_label]

                with st.form("movement_form", clear_on_submit=True):
                    movement_type = st.radio("Movimentação", ["Depósito", "Retirada"], horizontal=True)
                    movement_amount = st.number_input(
                        "Valor (R$)", min_value=0.01, step=10.0, format="%.2f"
                    )
                    movement_date = st.date_input(
                        "Data", value=date.today(), format="DD/MM/YYYY", key="movement_date"
                    )
                    submitted = st.form_submit_button(
                        "Confirmar movimentação", type="primary", use_container_width=True
                    )

                    if submitted:
                        try:
                            add_savings_movement(
                                supabase,
                                user_id,
                                selected_goal_id,
                                float(movement_amount),
                                movement_type,
                                movement_date.isoformat(),
                            )
                            st.success("Movimentação registrada.")
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))

        with history_col:
            with st.container(border=True):
                st.subheader("Histórico da meta")
                history = get_savings_history(supabase, user_id, selected_goal_id)

                if history.empty:
                    st.info("Nenhuma movimentação registrada.")
                else:
                    history["date"] = pd.to_datetime(history["date"])
                    history["Data"] = history["date"].dt.strftime("%d/%m/%Y")
                    history["Valor"] = history.apply(
                        lambda row: ("+ " if row["movement_type"] == "Depósito" else "- ")
                        + brl(row["amount"]),
                        axis=1,
                    )
                    history = history.rename(columns={"movement_type": "Movimentação"})
                    st.dataframe(
                        history[["Data", "Movimentação", "Valor"]],
                        use_container_width=True,
                        hide_index=True,
                    )

        with st.expander("Excluir uma meta"):
            delete_options = {
                f"{row.name} — {brl(row.current_amount)} guardados": row.id
                for row in goals.itertuples()
            }
            chosen_goal = st.selectbox("Selecione a meta", list(delete_options.keys()), key="delete_goal")
            if st.button("Excluir meta", use_container_width=True):
                delete_savings_goal(supabase, user_id, delete_options[chosen_goal])
                st.success("Meta excluída.")
                st.rerun()

st.markdown('<div class="logout-footer"></div>', unsafe_allow_html=True)
footer_left, footer_right = st.columns([4, 1])
with footer_left:
    st.caption("FinTrack · Controle financeiro pessoal")
    st.caption(f"Conectado como {user_email}")
with footer_right:
    if st.button("Sair", key="logout_footer", use_container_width=True):
        logout()
        st.rerun()
