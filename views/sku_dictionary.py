"""
Dicionário de SKUs — lê o cache do Bling em disco e exibe uma tabela
de consulta rápida com Nome do Produto e SKU (código) para a equipe de tráfego.
"""
import json
import os

import pandas as pd
import streamlit as st

_CACHE_FILE = "data/bling_cache.json"


def _load_sku_table() -> pd.DataFrame:
    """
    Varre data/bling_cache.json e extrai, de todos os itens de todos os pedidos,
    os campos 'descricao' (nome) e 'codigo' (SKU).
    Retorna DataFrame deduplicado e ordenado alfabeticamente.
    """
    if not os.path.exists(_CACHE_FILE):
        return pd.DataFrame(columns=["Produto", "SKU"])

    with open(_CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)

    rows = []
    for pedido in cache.values():
        for item in pedido.get("itens") or []:
            nome = (item.get("descricao") or "").strip()
            sku  = str(item.get("codigo") or "").strip()
            if nome:
                rows.append({"Produto": nome, "SKU": sku})

    if not rows:
        return pd.DataFrame(columns=["Produto", "SKU"])

    df = (
        pd.DataFrame(rows)
        .drop_duplicates(subset=["Produto", "SKU"])
        .sort_values("Produto", key=lambda s: s.str.lower())
        .reset_index(drop=True)
    )
    return df


def show():
    st.markdown("## Dicionário de SKUs 📖")
    st.caption("Referência de produtos cadastrados no Bling")
    st.markdown("")

    st.info(
        "Use o campo de busca abaixo para encontrar o produto desejado. "
        "Copie o **SKU** e use-o no nome do Anúncio ou Conjunto no Meta Ads "
        "para garantir o match correto no Dashboard.",
        icon="💡",
    )

    df = _load_sku_table()

    if df.empty:
        st.warning(
            "Nenhum produto encontrado. O cache do Bling ainda não foi gerado. "
            "Acesse qualquer outra aba para disparar o carregamento.",
            icon="⚠️",
        )
        return

    # ── Filtro por texto ───────────────────────────────────────────────────────
    busca = st.text_input(
        "🔍 Buscar produto",
        placeholder="Digite parte do nome ou SKU...",
        label_visibility="collapsed",
    )

    if busca.strip():
        mask = (
            df["Produto"].str.contains(busca.strip(), case=False, na=False)
            | df["SKU"].str.contains(busca.strip(), case=False, na=False)
        )
        df_view = df[mask].reset_index(drop=True)
    else:
        df_view = df

    st.caption(f"{len(df_view)} produto(s) encontrado(s) de {len(df)} no total")

    st.dataframe(
        df_view,
        use_container_width=True,
        hide_index=True,
        height=min(600, 35 + len(df_view) * 35),
    )
