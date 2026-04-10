import plotly.graph_objects as go
import streamlit as st

NOXER_BLUE  = "#005CFE"
AMBER       = "#F59E0B"
SKY         = "#0EA5E9"
GRID_COLOR  = "rgba(229,231,235,0.45)"
TRANSPARENT = "rgba(0,0,0,0)"

_FMT = {
    "Gasto":     "R$ {:,.2f}",
    "Impressões":"{:,.0f}",
    "Clicks":    "{:,.0f}",
    "Leads":     "{:,.0f}",
    "CPL":       "R$ {:,.2f}",
    "CTR":       "{:.2f}%",
    "CPC":       "R$ {:,.2f}",
    "CPM":       "R$ {:,.2f}",
}


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


def _agg_metrics(df, group_cols):
    """Agrupa, soma valores brutos e recalcula métricas derivadas como float64."""
    agg = (
        df.groupby(group_cols)
        .agg(spend=("spend", "sum"), impressions=("impressions", "sum"),
             clicks=("clicks", "sum"), leads=("leads", "sum"))
        .reset_index()
        .sort_values("spend", ascending=False)
    )
    # Garante float64 puro antes de qualquer divisão
    for col in ["spend", "impressions", "clicks", "leads"]:
        agg[col] = agg[col].astype(float).fillna(0.0)

    leads_s = agg["leads"].replace(0.0, float("nan"))
    imp_s   = agg["impressions"].replace(0.0, float("nan"))
    clk_s   = agg["clicks"].replace(0.0, float("nan"))

    agg["CPL"] = (agg["spend"] / leads_s).fillna(0.0).round(2)
    agg["CTR"] = (agg["clicks"] / imp_s * 100).fillna(0.0).round(2)
    agg["CPC"] = (agg["spend"] / clk_s).fillna(0.0).round(2)
    agg["CPM"] = (agg["spend"] / imp_s * 1000).fillna(0.0).round(2)

    return agg.rename(columns={
        "spend":       "Gasto",
        "impressions": "Impressões",
        "clicks":      "Clicks",
        "leads":       "Leads",
    })


def show(df):
    st.markdown("## Campanhas")
    st.caption("Otimização de Mídia Paga — Meta Ads")
    st.markdown("")

    # Remove fallback Bling — não existe no Meta Ads
    df = df[df["campaign_name"] != "Bling Direto"].copy()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_spend  = float(df["spend"].sum())
    total_leads  = float(df["leads"].sum())
    total_imp    = float(df["impressions"].sum())
    total_clicks = float(df["clicks"].sum())
    avg_cpl = total_spend / total_leads  if total_leads  else 0.0
    avg_cpc = total_spend / total_clicks if total_clicks else 0.0
    avg_ctr = total_clicks / total_imp * 100 if total_imp else 0.0
    avg_cpm = total_spend / total_imp * 1000 if total_imp else 0.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Gasto Total", "R$ {:,.0f}".format(total_spend))
    c2.metric("Leads",       "{:,.0f}".format(total_leads))
    c3.metric("CPL",         "R$ {:,.2f}".format(avg_cpl))
    c4.metric("CPC",         "R$ {:,.2f}".format(avg_cpc))
    c5.metric("CTR",         "{:.2f}%".format(avg_ctr))
    c6.metric("CPM",         "R$ {:,.2f}".format(avg_cpm))

    st.markdown("---")

    # ── Gráfico 1: Leads, Gasto e CPL Diário (full width) ────────────────────
    daily = (
        df.groupby("date")
        .agg(spend=("spend", "sum"), leads=("leads", "sum"))
        .reset_index()
        .sort_values("date")
    )
    daily["cpl"] = (daily["spend"] / daily["leads"].replace(0, float("nan"))).fillna(0.0)

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=daily["date"], y=daily["leads"],
        name="Leads",
        mode="lines+markers",
        line=dict(color=NOXER_BLUE, width=2.5, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor="rgba(0,92,254,0.06)",
        marker=dict(size=5),
        hovertemplate="%{x|%d/%m}: %{y:.0f} leads<extra></extra>",
        yaxis="y1",
    ))
    fig_daily.add_trace(go.Scatter(
        x=daily["date"], y=daily["spend"],
        name="Gasto",
        mode="lines",
        line=dict(color=AMBER, width=2, dash="dot", shape="spline", smoothing=0.8),
        hovertemplate="%{x|%d/%m}: R$ %{y:,.0f}<extra></extra>",
        yaxis="y2",
    ))
    fig_daily.add_trace(go.Scatter(
        x=daily["date"], y=daily["cpl"],
        name="CPL",
        mode="lines+markers",
        line=dict(color=SKY, width=2, shape="spline", smoothing=0.8),
        marker=dict(size=4),
        hovertemplate="%{x|%d/%m}: R$ %{y:.2f} CPL<extra></extra>",
        yaxis="y3",
    ))
    fig_daily.update_layout(
        **_base_layout(
            title=dict(text="Leads, Gasto e CPL Diário",
                       font=dict(size=14, color="#111827")),
            height=400,
            margin=dict(l=20, r=100, t=50, b=20),
            hovermode="x unified",
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right",
                        font=dict(size=12, color="#6B7280")),
            xaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(size=10, color="#9CA3AF")),
            yaxis=dict(title="Leads", showgrid=True, gridcolor=GRID_COLOR,
                       zeroline=False, tickfont=dict(size=10, color="#9CA3AF")),
            yaxis2=dict(title="Gasto (R$)", overlaying="y", side="right",
                        zeroline=False, showgrid=False,
                        tickfont=dict(size=10, color=AMBER), tickprefix="R$ "),
            yaxis3=dict(overlaying="y", side="right", anchor="free", position=1.0,
                        zeroline=False, showgrid=False, visible=False),
        )
    )
    st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})

    # ── Gráfico 2: CPL por Anúncio — apenas ads com spend > R$ 50 ─────────────
    st.markdown("#### CPL por Anúncio")

    ads = (
        df.groupby("ad_name")
        .agg(spend=("spend", "sum"), leads=("leads", "sum"))
        .reset_index()
    )
    ads_filtrado = ads[ads["spend"] > 50].copy()

    if ads_filtrado.empty:
        st.info("Nenhum anúncio atingiu R$ 50 de investimento no período selecionado.")
    else:
        ads_filtrado["cpl"] = (
            ads_filtrado["spend"] / ads_filtrado["leads"].replace(0, float("nan"))
        ).fillna(0.0).round(2)
        # Decrescente → Plotly renderiza de baixo pra cima → menor CPL no topo
        ads_filtrado = ads_filtrado.sort_values("cpl", ascending=False)

        fig_cpl = go.Figure(go.Bar(
            x=ads_filtrado["cpl"],
            y=ads_filtrado["ad_name"],
            orientation="h",
            marker_color=NOXER_BLUE,
            text=ads_filtrado["cpl"].apply("R$ {:.2f}".format),
            textposition="outside",
            textfont=dict(size=11, color="#374151"),
            hovertemplate="<b>%{y}</b><br>CPL: R$ %{x:.2f}<extra></extra>",
        ))
        fig_cpl.update_layout(
            **_base_layout(
                height=max(300, len(ads_filtrado) * 38),
                margin=dict(l=20, r=90, t=30, b=20),
                xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                           tickfont=dict(size=10, color="#9CA3AF"), tickprefix="R$ "),
                yaxis=dict(showgrid=False, zeroline=False,
                           tickfont=dict(size=11, color="#374151"), automargin=True),
            )
        )
        st.plotly_chart(fig_cpl, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── Tabela 1: por Campanha ────────────────────────────────────────────────
    st.markdown("#### Detalhamento por Campanha")
    t1 = _agg_metrics(df, ["campaign_name"]).rename(columns={"campaign_name": "Campanha"})
    cols1 = ["Campanha", "Gasto", "Impressões", "Clicks", "Leads", "CPL", "CTR", "CPC", "CPM"]
    st.dataframe(t1[cols1].style.format(_FMT), use_container_width=True, hide_index=True)

    # ── Tabela 2: por Campanha + Conjunto ─────────────────────────────────────
    st.markdown("#### Detalhamento por Campanha e Conjunto")
    t2 = _agg_metrics(df, ["campaign_name", "adset_name"]).rename(columns={
        "campaign_name": "Campanha", "adset_name": "Conjunto"
    })
    cols2 = ["Campanha", "Conjunto", "Gasto", "Impressões", "Clicks", "Leads", "CPL", "CTR", "CPC", "CPM"]
    st.dataframe(t2[cols2].style.format(_FMT), use_container_width=True, hide_index=True)

    # ── Tabela 3: por Campanha + Conjunto + Anúncio ───────────────────────────
    st.markdown("#### Detalhamento por Anúncio")
    t3 = _agg_metrics(df, ["campaign_name", "adset_name", "ad_name"]).rename(columns={
        "campaign_name": "Campanha", "adset_name": "Conjunto", "ad_name": "Anúncio"
    })
    cols3 = ["Campanha", "Conjunto", "Anúncio", "Gasto", "Impressões", "Clicks", "Leads", "CPL", "CTR", "CPC", "CPM"]
    st.dataframe(t3[cols3].style.format(_FMT), use_container_width=True, hide_index=True)
