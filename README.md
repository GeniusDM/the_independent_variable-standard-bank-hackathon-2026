# Syn Bank Share of Wallet Intelligence Engine

**Standard Bank × Data School Hackathon 2026 | Team: The Independent Variable**

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

Where appropriate, publicly available corporate information may be incorporated, including:

- Annual financial statements
- Investor Relations reports
- JSE SENS announcements
- National Treasury publications
- Company financial disclosures

## Methodology

See [docs/methodology.md](docs/methodology.md) for wallet sizing logic, benchmark ratios, and assumptions.

## Dashboard

The dashboard provides multiple business views, including:

- N/A

## Languages and Tech Stack

<div align="left">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="50" alt="Python"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" height="50" alt="Pandas"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" height="50" alt="NumPy"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg" height="50" alt="Scikit-Learn"/>
<img width="12"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/plotly/plotly-original.svg" height="50" alt="Plotly"/>
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
├── start.py                     # dev launcher — starts backend + frontend together
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── benchmarks.yaml          # wallet sizing ratios — single source of truth
│   └── scoring_weights.yaml     # opportunity score weights
├── data/                        # local only, git-ignored
│   ├── raw/
│   ├── processed/
│   └── external/
├── frontend/                    # Next.js executive dashboard
│   ├── pages/
│   ├── components/
│   └── assets/
├── backend/                     # FastAPI backend
│   ├── main.py
│   ├── routes/
│   └── schemas.py
├── models/
│   ├── wallet_engine.py         # wallet sizing formulas
│   ├── opportunity_engine.py    # opportunity scoring & ranking
│   └── explainability.py       # plain-English gap explanations
├── ai/
│   ├── retrieval.py             # FAISS RAG over financial documents
│   ├── briefing.py              # GenAI client briefing generator
│   └── copilot.py               # natural language query interface
├── prompts/                     # prompt templates + sample output logs
├── notebooks/
│   └── share_of_wallet_analysis.ipynb
├── docs/
│   ├── methodology.md
│   ├── executive_summary.pdf
│   └── presentation_deck.pptx
└── tests/
    ├── test_wallet_engine.py
    ├── test_opportunity_engine.py
    └── test_ai_outputs.py
```

## Setup

```bash
git clone https://github.com/<username>/the_independent_variable-standard-bank-hackathon-2026.git
cd the_independent_variable-standard-bank-hackathon-2026
cp .env.example .env   # add your API keys
```

## Prerequisites

Install the Python requirements before doing anything else:

```bash
pip install -r requirements.txt
```

Place the hackathon CSV files in `data/raw/`.

## Running

**Start everything (recommended)**

`start.py` launches the FastAPI backend and the Next.js frontend together in one terminal, prefixing each process's output with a coloured `[backend]` / `[frontend]` label. `Ctrl+C` shuts both down cleanly.

```bash
python3 start.py
```

Optional flags if you only need one side:

```bash
python3 start.py --backend
python3 start.py --frontend
```

**Individually**

```bash
# API backend — http://localhost:8000
uvicorn backend.main:app --reload

# Frontend dashboard — http://localhost:3000
cd frontend && npm run dev
```

**Notebook**

```bash
jupyter notebook notebooks/share_of_wallet_analysis.ipynb
```

**Tests**

```bash
pytest tests/
```

## Team

**Daniel Genius Mataranyinka**

[![Email](https://img.shields.io/badge/Email-26653990@sun.ac.za-blue?style=flat&logo=gmail)](mailto:26653990@sun.ac.za)
[![GitHub](https://img.shields.io/badge/GitHub-GeniusDM-black?style=flat&logo=github)](https://github.com/GeniusDM)

**Herton Cabral Mabongue**

[![Email](https://img.shields.io/badge/Email-27190552@sun.ac.za-blue?style=flat&logo=gmail)](mailto:27190552@sun.ac.za)
[![GitHub](https://img.shields.io/badge/GitHub-HertonMabongue-black?style=flat&logo=github)](https://github.com/HertonMabongue)
