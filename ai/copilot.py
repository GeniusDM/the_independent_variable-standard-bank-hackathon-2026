"""
copilot.py
Natural language copilot for Syn Bank bankers.
Translates plain-English queries into filtered DataFrame results + narrative answers.
Example: "Show me mining clients with high FX exposure but low Syn Bank share"
"""
import os
import json
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a data copilot for Syn Bank's coverage team.
You receive a banker's natural language question and a JSON schema of available columns.
Return ONLY a valid JSON object with:
{
  "filters": [{"column": "...", "operator": "...", "value": ...}],
  "sort_by": "column_name",
  "ascending": false,
  "limit": 10,
  "narrative": "One sentence explaining what this query returns."
}
Operators: >, <, >=, <=, ==, contains
"""


def parse_query(question: str, columns: list[str]) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Columns: {columns}\nQuestion: {question}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def run_query(question: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    parsed = parse_query(question, list(df.columns))
    result = df.copy()

    for f in parsed.get("filters", []):
        col, op, val = f["column"], f["operator"], f["value"]
        if col not in result.columns:
            continue
        if op == ">":   result = result[result[col] > val]
        elif op == "<": result = result[result[col] < val]
        elif op == ">=": result = result[result[col] >= val]
        elif op == "<=": result = result[result[col] <= val]
        elif op == "==": result = result[result[col] == val]
        elif op == "contains": result = result[result[col].astype(str).str.contains(val, case=False)]

    sort_col = parsed.get("sort_by")
    if sort_col and sort_col in result.columns:
        result = result.sort_values(sort_col, ascending=parsed.get("ascending", False))

    limit = parsed.get("limit", 10)
    return result.head(limit), parsed.get("narrative", "")
