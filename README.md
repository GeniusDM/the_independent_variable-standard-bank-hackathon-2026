# Syn Bank Share of Wallet Intelligence Engine

## Standard Bank × Data School Hackathon 2026 | Team: The Independent Variable

Estimates the total addressable banking wallet for corporate clients, quantifies Syn Bank's current share across product pillars, ranks growth opportunities, and delivers GenAI-powered executive briefing notes.

---

## Project Overview

Corporate clients typically maintain relationships with multiple financial institutions, making it difficult for banks to understand how much business they currently capture and where growth opportunities exist.

This project combines synthetic internal banking data with external financial information to:

- Estimate each client's total banking wallet
- Calculate Syn Bank's current Share of Wallet
- Identify product and revenue gaps
- Prioritize high-value clients
- Generate AI-powered client briefings and recommendations

## Data Sources

The solution integrates multiple datasets provided during the hackathon.

### Internal Data

- Syn Bank Transactional Data
- Syn Bank SWIFT Payment Data
- Syn Bank Trade Finance Data

### External Data

Where appropriate, publicly available corporate information was incorporated, including:

- Annual financial statements
- Company financial disclosures

## Methodology

See [docs/methodology.md](docs/methodology.md) for wallet sizing logic, benchmark ratios, and assumptions.

## Dashboard

The dashboard provides multiple business views, including:

- **Portfolio Overview** — macro KPI cards (total wallet, average share %, total ZAR gap, number of clients), sector breakdown bar chart, and a ranked client table sortable by opportunity score
- **Opportunity Heatmap** — interactive matrix of all 50 clients vs. the four product pillars (Transactional, FX, Trade Finance, Lending), colour-coded by ZAR gap size to surface where competitors are winning
- **Client Deep-Dive** — individual client profile with pillar-level wallet vs. Syn Bank share bars, transaction timeline, and a one-click GenAI briefing note card
- **AI Copilot** — natural language query bar (e.g. _"Show me mining clients with FX gap above R5M"_) that filters the dataset and returns a plain-English narrative alongside the matching results

## Languages and Tech Stack

<div align="left">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="50" alt="Python"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" height="50" alt="Pandas"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" height="50" alt="FastAPI"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" height="50" alt="Next.js"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" height="50" alt="TypeScript"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" height="50" alt="Tailwind CSS"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" height="50" alt="GitHub"/>
</div>

## Repository Structure

```
the_independent_variable-standard-bank-hackathon-2026/
├── README.md
├── start.py                     # starts backend + frontend together
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── benchmarks.yaml          # wallet sizing ratios
│   └── scoring_weights.yaml     # opportunity score weights
├── data/                        # local only, git-ignored
│   ├── raw/
│   ├── processed/
│   └── external/
├── frontend/                         # Next.js dashboard
│   ├── src/
│   │   ├── app/                      # App Router pages
│   │   │   ├── page.tsx              # Portfolio Overview
│   │   │   ├── layout.tsx
│   │   │   ├── clients/
│   │   │   │   ├── page.tsx          # Client list
│   │   │   │   └── [id]/page.tsx     # Client Deep-Dive
│   │   │   ├── opportunities/
│   │   │   │   └── page.tsx          # Opportunity Heatmap
│   │   │   └── copilot/
│   │   │       └── page.tsx          # AI Copilot chat
│   │   ├── components/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── KpiCard.tsx
│   │   │   ├── ClientTable.tsx
│   │   │   ├── ClientBriefingCard.tsx
│   │   │   ├── OpportunityHeatmap.tsx
│   │   │   ├── SectorBreakdownChart.tsx
│   │   │   └── CopilotChat.tsx
│   │   ├── lib/
│   │   │   ├── api.ts                # fetch wrappers for FastAPI
│   │   │   └── mockData.ts           # offline fallback data
│   │   └── types/
│   │       └── index.ts              # shared TypeScript interfaces
│   ├── public/
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── backend/                          # FastAPI backend
│   ├── main.py
│   ├── routes/
│   │   ├── wallet.py
│   │   ├── opportunities.py
│   │   ├── briefings.py
│   │   └── copilot.py
│   └── schemas.py
├── models/
│   ├── wallet_engine.py              # wallet sizing formulas
│   ├── opportunity_engine.py         # opportunity scoring & ranking
│   └── explainability.py            # plain-English gap explanations
├── ai/
│   ├── retrieval.py                  # FAISS RAG over financial documents
│   ├── briefing.py                   # GenAI client briefing generator
│   ├── copilot.py                    # natural language query interface
│   └── llm.py                        # LLM provider abstraction
├── scripts/
│   ├── generate_briefings.py         # writes docs/ai_briefings.md
│   └── build_notebook.py
├── prompts/
│   ├── logs/                         # per-client briefing outputs
│   └── cache/                        # cached LLM responses
├── notebooks/
│   └── share_of_wallet_analysis.ipynb
├── docs/
│   ├── figures/                      # charts exported from notebook
│   ├── methodology.md
│   ├── ai_briefings.md
│   ├── executive_summary.pdf
│   └── presentation_deck.pptx
└── tests/
    ├── conftest.py
    ├── test_wallet_engine.py
    ├── test_opportunity_engine.py
    └── test_ai_outputs.py
```

## Setup

Requires Python 3.11+ and Node 18+.

```bash
git clone https://github.com/GeniusDM/the_independent_variable-standard-bank-hackathon-2026.git
cd the_independent_variable-standard-bank-hackathon-2026
cp .env.example .env   # add your API keys
```

**1. Python environment**

```bash
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

pip install -r requirements.txt
```

> **Windows note.** If the repo sits under a long path (e.g. inside a synced
> OneDrive folder), installing JupyterLab fails with
> `[WinError 206] The filename or extension is too long` — its nested
> `share/jupyter/labextensions/@jupyter-widgets/...` paths overrun the 260-character
> limit. Create the environment somewhere short instead, and keep it out of the
> synced folder so the file watcher can't lock packages mid-install:
>
> ```bat
> python -m venv %USERPROFILE%\.venvs\synbank
> %USERPROFILE%\.venvs\synbank\Scripts\activate
> pip install -r requirements.txt
> ```

**2. Node packages**

```bash
cd frontend && npm install && cd ..
```

**3. Hackathon data**

Copy the three supplied CSVs into `data/raw/` (the directory is git-ignored — the
files total ~429MB and must never be committed):

```
data/raw/transactional_banking.csv
data/raw/cross_border_payments.csv
data/raw/trade_finance.csv
```

## Running

**Start everything (recommended)**

`start.py` launches the FastAPI backend and the Next.js frontend together in one terminal, prefixing each process's output with a coloured `[backend]` / `[frontend]` label. `Ctrl+C` shuts both down cleanly.

```bash
python start.py
```

Then open <http://localhost:3000>. The first request builds the wallet model from
the raw CSVs and takes roughly 10 seconds; afterwards results are cached.

Optional flags if you only need one side:

```bash
python start.py --backend
python start.py --frontend
```

**Individually**

```bash
# API backend — http://localhost:8000
uvicorn backend.main:app --reload

# Frontend dashboard — http://localhost:3000
cd frontend && npm run dev
```

**Notebook**

The full analysis — ingestion, transformation, modelling, visualisation — runs top to
bottom against the raw CSVs. No API key is required; the GenAI section reads from
`prompts/cache/`.

```bash
jupyter notebook notebooks/share_of_wallet_analysis.ipynb

# or execute it headlessly
jupyter nbconvert --to notebook --execute --inplace \
    notebooks/share_of_wallet_analysis.ipynb
```

**AI client briefings**

```bash
python scripts/generate_briefings.py          # writes docs/ai_briefings.md
```

**Tests**

```bash
pytest tests/
```

## Demo Setup (Vercel + ngrok)

For live judging, the frontend is deployed on Vercel and the backend runs locally tunnelled via ngrok.

**On your laptop:**

```bash
# 1. Start the backend
python3 start.py --backend

# 2. In a separate terminal, start ngrok
ngrok http 8000
```

**On Vercel:**

- Set `NEXT_PUBLIC_API_BASE_URL` to your ngrok URL (e.g. `https://abc123.ngrok-free.app`)
- Redeploy

**On your laptop, allow the Vercel domain through CORS:**

Replace `https://your-project.vercel.app` in `backend/main.py` with your actual Vercel URL, then:

```bash
python3 start.py --backend
```

Judges scan the QR code → Vercel frontend → ngrok tunnel → local FastAPI backend → real data.

---

## Contact Us

**Daniel Genius Mataranyinka**

[![Email](https://img.shields.io/badge/Email-26653990@sun.ac.za-blue?style=flat&logo=gmail)](mailto:26653990@sun.ac.za)
[![GitHub](https://img.shields.io/badge/GitHub-GeniusDM-black?style=flat&logo=github)](https://github.com/GeniusDM)

**Herton Cabral Mabongue**

[![Email](https://img.shields.io/badge/Email-27190552@sun.ac.za-blue?style=flat&logo=gmail)](mailto:27190552@sun.ac.za)
[![GitHub](https://img.shields.io/badge/GitHub-HertonMabongue-black?style=flat&logo=github)](https://github.com/HertonMabongue)
