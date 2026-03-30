# Frankie 2.0 — Warehouse Decision Engine

**Vinod Kunapuli | Supply Chain Command Center**

## What This Is
A live warehouse decision support tool built on mock Epicor Eclipse data, demonstrating enterprise-wide slotting optimization, OpCo benchmarking, and ROI modeling — powered by AI recommendations.

## Tabs
- **Slotting Engine** — Run optimization on 15 SKUs from mock Eclipse data. See recommended zone moves.
- **OpCo Benchmarking** — Compare Crawford Electric, North Coast Electric, and Viking Electric across 6 KPIs.
- **ROI Calculator** — Translate travel distance reduction into annual labor dollar savings with What-If sliders.
- **AI Advisor** — Each tab has a live AI consultant powered by Claude that analyzes mock data and responds in context.

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud (Free)
1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io
3. Connect repo → set `app.py` as main file
4. Add secret: `ANTHROPIC_API_KEY = "your-key-here"` in Settings → Secrets

## Tech Stack
- Streamlit (UI)
- Plotly (charts)
- Pandas + NumPy (data)
- Anthropic Claude API (AI advisor)
- Mock Epicor Eclipse data
