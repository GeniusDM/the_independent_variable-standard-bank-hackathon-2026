# Syn Bank Share of Wallet Intelligence Engine

**Standard Bank × Data School Hackathon 2026 | Team: The Independent Variable**

Estimates the total addressable banking wallet for 50 JSE-listed corporate clients, quantifies Syn Bank's current share across four product pillars, ranks growth opportunities, and delivers GenAI-powered executive briefing notes.

---

## Repository Structure

```
the_independent_variable-standard-bank-hackathon-2026/
├── README.md
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

**API backend**

```bash
uvicorn backend.main:app --reload
```

**Notebook**

```bash
jupyter notebook notebooks/share_of_wallet_analysis.ipynb
```

## Methodology

See [docs/methodology.md](docs/methodology.md) for wallet sizing logic, benchmark ratios, and assumptions.

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
