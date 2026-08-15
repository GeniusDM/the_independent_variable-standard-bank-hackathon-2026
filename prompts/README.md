# Prompts Directory

This directory contains all GenAI prompt templates and sample output logs.
Required as a hackathon deliverable: **evidence of Generative AI integration**.

## Files

| File | Description |
|------|-------------|
| `briefing_prompt.md` | System + user prompt template for client briefing generation |
| `copilot_prompt.md` | System prompt for natural language query parsing |
| `sample_outputs/` | Sample LLM outputs for at least 3 clients (required deliverable) |

## Logging

All production briefing calls are logged to `prompts/logs/` (git-ignored).
Each log entry records: `client_id`, `prompt_tokens`, `completion_tokens`, `model`, `timestamp`, `output`.
