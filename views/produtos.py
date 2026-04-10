import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.loader import build_roas_by_family

NOXER_BLUE  = "#005CFE"
GRID_COLOR  = "rgba(229,231,235,0.45)"
TRANSPARENT = "rgba(0,0,0,0)"


def _base_layout(**kwargs):
    base = dict(
        paper_bgcolor=TRANSPARENT,
        plot_bgcolor=TRANSPARENT,
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=11, color="#9CA3AF")),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                   tickfont=dict(size=11, color="#9CA3AF")),
    )
    base.update(kwargs)
    return base


# ── View principal ─────────────────────────────────────────────────────────────

def show(df):
    st.markdown("## Produtos")
    st.caption("Análise de saída, faturamento e rentabilidade por produto")
    st.markdown("")

    df_bling = df[df["campaign_name"] == "Bling Direto"].copy()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_revenue   = pd.to_numeric(df_bling["total_price"], errors="coerce").fillna(0).sum()
    total_units     = int(pd.to_numeric(df_bling["quantity"], errors="coerce").fillna(0).sum())
    prods_com_venda = int(df_bling[df_bling["quantity"] > 0]["product_name"].nunique())
    n_pedidos       = df_bling["order_id"].nunique()
    avg_ticket      = total_revenue / n_pedidos if n_pedidos else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Produtos com Vendas", str(prods_com_venda))
    c2.metric("Unidades Vendidas",   "{:,}".format(total_units))
    c3.metric("Faturamento Total",   "R$ {:,.0f}".format(total_revenue))
    c4.metric("Ticket Médio Geral",  "R$ {:,.0f}".format(avg_ticket))

    st.markdown("---")

    if df_bling.empty:
        st.info("Nenhum dado de produto encontrado. Verifique a conexão com o Bling.")
        return

    prod = build_roas_by_family(df)

    if prod.empty:
        st.info("Nenhum produto com dados suficientes para exibir.")
        return

    # ══════════════════════════════════════════════════════════════════════════
    # 1ª CAMADA — Gráfico de barras horizontais (Top 10)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### Top 10 Produtos por Faturamento")

    top10 = prod.head(10).sort_values("faturamento", ascending=True)

    fig = go.Figure(go.Bar(
        x=top10["faturamento"],
        y=top10["produto"],
        orientation="h",
        marker=dict(
            color=top10["roas"],
            colorscale=[[0, "#DBEAFE"], [0.4, "#93C5FD"], [0.7, "#3B82F6"], [1, NOXER_BLUE]],
            showscale=True,
            colorbar=dict(
                title="ROAS",
                len=0.75,
                thickness=12,
                tickfont=dict(size=10, color="#9CA3AF"),
            ),
        ),
        text=top10["faturamento"].apply("R$ {:,.0f}".format),
        textposition="outside",
        textfont=dict(size=11, color="#374151"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Faturamento: R$ %{x:,.0f}<br>"
            "ROAS: %{marker.color:.2f}x"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        **_base_layout(
            height=max(320, len(top10) * 40),
            margin=dict(l=20, r=80, t=30, b=20),
            xaxis=dict(
                showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                tickfont=dict(size=10, color="#9CA3AF"),
                tickprefix="R$ ", tickformat=",.0f",
            ),
            yaxis=dict(
                showgrid=False, zeroline=False,
                tickfont=dict(size=12, color="#374151"),
            ),
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ══════════════════════════════════════════════════════════════════════════
    # 2ª CAMADA — Tabela Mestra (valores numéricos + formatação visual)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### Tabela de Performance por Produto")

    tbl = prod[[
        "produto", "investimento", "leads", "cpl",
        "unidades", "tx_conversao", "faturamento", "ticket_medio", "roas",
    ]].reset_index(drop=True).copy()

    # Todos os tipos numéricos garantidos como float64 para ordenação correta
    for c in ["investimento", "leads", "cpl", "unidades",
              "tx_conversao", "faturamento", "ticket_medio", "roas"]:
        tbl[c] = pd.to_numeric(tbl[c], errors="coerce").fillna(0.0)

    tbl = tbl.rename(columns={
        "produto":      "Produto",
        "investimento": "Investimento",
        "leads":        "Leads",
        "cpl":          "CPL",
        "unidades":     "Vendas",
        "tx_conversao": "Tx. Conversão",
        "faturamento":  "Faturamento",
        "ticket_medio": "Ticket Médio",
        "roas":         "ROAS",
    })

    for col in ["Investimento", "Leads", "CPL", "Vendas",
                "Tx. Conversão", "Faturamento", "Ticket Médio", "ROAS"]:
        tbl[col] = tbl[col].astype(float).fillna(0.0)
    fmt = {
        "Investimento":  "R$ {:,.0f}",
        "Leads":         "{:,.0f}",
        "CPL":           "R$ {:,.2f}",
        "Vendas":        "{:,.0f}",
        "Tx. Conversão": "{:.1f}%",
        "Faturamento":   "R$ {:,.0f}",
        "Ticket Médio":  "R$ {:,.0f}",
        "ROAS":          "{:.2f}x",
    }
    st.dataframe(tbl.style.format(fmt), use_container_width=True, hide_index=True)
