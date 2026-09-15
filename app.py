import base64
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

    .auth-wrap {
        max-width: 520px;
        margin: 1rem auto 0;
    }

    .auth-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 28px rgba(16,24,40,.06);
        margin-bottom: 14px;
    }

    .auth-logo { width: 64px; height: 64px; margin-bottom: 12px; }
    .auth-title { font-size: 1.5rem; font-weight: 800; color: var(--text); }
    .auth-subtitle { color: var(--muted); margin-top: 7px; line-height: 1.5; }

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
    st.markdown(
        f"""
        <div class="auth-wrap">
            <div class="auth-card">
                <img class="auth-logo" src="data:image/svg+xml;base64,{logo_b64}">
                <div class="auth-title">Acesse o FinTrack</div>
                <div class="auth-subtitle">
                    Entre para acessar suas despesas, receitas e metas em qualquer dispositivo.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["Entrar", "Criar conta"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="voce@email.com")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if submitted:
                if not email.strip() or not password:
                    st.error("Informe e-mail e senha.")
                else:
                    try:
                        if login(email, password):
                            st.rerun()
                    except Exception:
                        st.error("Não foi possível entrar. Verifique seus dados e confirme seu e-mail.")

        with st.expander("Esqueci minha senha"):
            reset_email = st.text_input("E-mail para recuperação", key="reset_email")
            if st.button("Enviar recuperação", use_container_width=True):
                if not reset_email.strip():
                    st.warning("Informe seu e-mail.")
                else:
                    try:
                        send_password_reset(reset_email)
                        st.success("Se a conta existir, as instruções serão enviadas por e-mail.")
                    except Exception:
                        st.error("Não foi possível solicitar a recuperação.")

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("E-mail", placeholder="voce@email.com", key="signup_email")
            password = st.text_input("Senha", type="password", key="signup_password")
            password2 = st.text_input("Confirmar senha", type="password", key="signup_password2")
            submitted = st.form_submit_button("Criar conta", type="primary", use_container_width=True)

            if submitted:
                if not email.strip():
                    st.error("Informe seu e-mail.")
                elif len(password) < 8:
                    st.error("A senha deve ter pelo menos 8 caracteres.")
                elif password != password2:
                    st.error("As senhas não coincidem.")
                else:
                    try:
                        result = signup(email, password)
                        if result == "logged_in":
                            st.rerun()
                        else:
                            st.success("Conta criada. Confirme o e-mail e depois faça login.")
                    except Exception:
                        st.error("Não foi possível criar a conta. O e-mail pode já estar cadastrado.")

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

logout_left, logout_right = st.columns([6, 1])
with logout_left:
    st.caption("Seus dados ficam sincronizados com sua conta.")
with logout_right:
    if st.button("Sair", use_container_width=True):
        logout()
        st.rerun()

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

st.caption("FinTrack · Controle financeiro pessoal")
