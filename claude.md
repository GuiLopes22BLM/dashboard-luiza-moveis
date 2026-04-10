# Briefing do Projeto: Dashboard Luiza Móveis

## 1. Visão Geral
Você atuará como um Engenheiro de Dados e Desenvolvedor Python Sênior. O objetivo é construir um Dashboard interno para a "Luiza Móveis" analisar a eficiência de suas campanhas de tráfego pago. A loja vende fisicamente via WhatsApp e registra os pedidos manualmente no ERP Bling. 

O desafio principal é a Atribuição: cruzar dados de custo do Meta Ads com faturamento real do Bling, sem o uso de UTMs dinâmicas, baseando-se em datas e produtos.

## 2. Stack Tecnológico
- Linguagem: Python
- Interface: Streamlit
- Manipulação de Dados: Pandas
- Gráficos: Plotly
- Integrações: `requests` (para API do Bling) e leitura de CSV/Planilha (para dados do Meta via Stract).

## 3. Arquitetura e Regras de Negócio
- A estrutura do Meta é: Campanha -> Conjuntos (Categorias) -> Anúncios (Produto específico).
- Os dados do Meta devem ser analisados a nível de Anúncio (Ad).
- Do Bling, extrairemos Pedidos de Venda (status "Pago") e seus itens.
- A mesclagem será feita por **Nome do Anúncio (Meta) <-> Nome do Produto (Bling)**.

## 4. Instruções de Execução (Fase 1 - Setup e UI Mockada)
Não crie conexões reais com APIs ainda. Crie apenas o esqueleto do sistema:
1. Crie o arquivo `requirements.txt` com as libs necessárias.
2. Crie `app.py` com a interface do Streamlit (Sidebar com filtros de data e produto).
3. Crie os Cards de KPIs no topo: Investimento (Meta), Leads (Meta), CPL, Faturamento (Bling), Ticket Médio e ROAS.
4. Crie 2 gráficos usando Plotly (Evolução diária e Vendas por produto).
5. Utilize `pandas` para criar um DataFrame fictício (mock) com a estrutura das colunas que usaremos no futuro, para que o dashboard já renderize visualmente.
