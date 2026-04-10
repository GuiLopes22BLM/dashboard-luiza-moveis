import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

VENDEDORES = ["Ana Silva", "Carlos Lima", "Beatriz Costa", "Rafael Santos", "Juliana Mendes"]

PRODUCTS = [
    "Sofá 3 Lugares Veludo",
    "Mesa de Jantar 6 Cadeiras",
    "Rack TV 60 Polegadas",
    "Cama Box Queen",
    "Guarda-Roupa 6 Portas",
    "Poltrona Reclinável",
    "Estante Multifuncional",
]

PRICES = {
    "Sofá 3 Lugares Veludo":     2400,
    "Mesa de Jantar 6 Cadeiras": 3500,
    "Rack TV 60 Polegadas":       890,
    "Cama Box Queen":            1800,
    "Guarda-Roupa 6 Portas":     2800,
    "Poltrona Reclinável":       1200,
    "Estante Multifuncional":     760,
}

CAMPAIGNS = ["Campanha Março | Awareness", "Campanha Março | Conversão"]


@st.cache_data
def load_mock_data():
    """
    DataFrame cruzado Meta Ads × Bling — uma linha por (anúncio × dia).

    Colunas Meta : campaign_name, adset_name, ad_name, date,
                   impressions, clicks, leads, spend, cpc, ctr, cpm
    Colunas Bling: order_id, order_date, product_name, quantity,
                   unit_price, total_price, order_status, vendedor
    Cruzamento   : matched, roas, cpl
    """
    random.seed(42)
    np.random.seed(42)

    adsets = {p: "Conjunto - " + p.split()[0] for p in PRODUCTS}
    rows = []
    base = date(2026, 3, 1)

    for day_offset in range(24):
        d = base + timedelta(days=day_offset)
        for product in PRODUCTS:
            spend       = round(random.uniform(30, 200), 2)
            impressions = random.randint(1000, 10000)
            clicks      = random.randint(50, 500)
            leads       = random.randint(2, 20)
            qty         = random.randint(0, 3)
            price       = PRICES[product]
            total       = qty * price

            rows.append({
                # ── Meta Ads ────────────────────────────────────────────────
                "campaign_name": random.choice(CAMPAIGNS),
                "adset_name":    adsets[product],
                "ad_name":       product,
                "date":          d,
                "impressions":   impressions,
                "clicks":        clicks,
                "leads":         leads,
                "spend":         spend,
                "cpc":           round(spend / clicks, 2)            if clicks      else 0.0,
                "ctr":           round(clicks / impressions * 100, 2) if impressions else 0.0,
                "cpm":           round(spend / impressions * 1000, 2) if impressions else 0.0,
                # ── Bling ───────────────────────────────────────────────────
                "order_id":      "ORD-" + str(day_offset * 10 + PRODUCTS.index(product)),
                "order_date":    d,
                "product_name":  product,
                "quantity":      qty,
                "unit_price":    price,
                "total_price":   total,
                "order_status":  "Pago",
                "vendedor":      random.choice(VENDEDORES) if qty > 0 else "",
                # ── Cruzamento ──────────────────────────────────────────────
                "matched":       qty > 0,
                "roas":          round(total / spend, 2) if spend else 0.0,
                "cpl":           round(spend / leads, 2) if leads else 0.0,
            })

    return pd.DataFrame(rows)
