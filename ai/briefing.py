"""
briefing.py
Generates structured executive briefing notes for Syn Bank coverage bankers
using a RAG-augmented LLM call.
"""
import os
from openai import OpenAI
from models.explainability import explain_client
from ai.retrieval import retrieve
import pandas as pd

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a senior Syn Bank coverage banker analyst.
Write concise, commercially sharp briefing notes for internal use.
Use South African corporate banking context. Be specific, not generic.
Output format:
## Client Briefing: {client_name}
**Sector**: | **Syn Bank Share**: | **Total Wallet (ZAR)**:
### Key Signals
### Biggest Gaps & Opportunities
### Recommended Meeting Agenda (3 points)
### Risk Flags
"""


def generate_briefing(row: pd.Series) -> str:
    explanation = explain_client(row)
    context_docs = retrieve(f"{row.get('client_name', '')} {row['sector']} South Africa banking")
    context = "\n---\n".join(context_docs[:3])

    user_prompt = f"""
Client data summary:
{explanation}

Relevant external context:
{context}

Generate the briefing note now.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=600,
    )
    return response.choices[0].message.content


def generate_portfolio_briefings(scored_df: pd.DataFrame, top_n: int = 3) -> dict:
    """Returns {client_id: briefing_text} for top_n clients."""
    briefings = {}
    for _, row in scored_df.head(top_n).iterrows():
        briefings[row["client_id"]] = generate_briefing(row)
    return briefings
