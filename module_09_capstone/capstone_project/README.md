# AI Content Factory — Capstone Project

Give it one topic. It researches the topic, then writes content for 4 platforms.

This is a **standalone project** — it reads its own `.env` file (no shared config needed).

## What it makes

| File | Platform | Length |
|------|----------|--------|
| `blog_post.md` | Blog | ~800 words |
| `twitter_thread.md` | Twitter/X | 8-10 tweets |
| `linkedin_post.md` | LinkedIn | ~1200 chars |
| `email_newsletter.md` | Email | short |

## How it works

```
Topic
  → Stage 1: Researcher → Analyst → knowledge package
  → Stage 2: 4 Writers → Reviewer → Publisher → output files
```

## Setup

1. Add your API key in `.env` (Groq, OpenRouter, or Cerebras).
2. Pick a provider with `DEFAULT_PROVIDER`.

```env
DEFAULT_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

## Run

Run from inside this folder:

```bash
python main.py --topic "The Rise of Multi-Agent AI Systems"
python main.py --topic "Python for Data Science" --voice casual
python main.py --topic "Building RAG Systems" --voice technical --provider openrouter
```

Options:
- `--topic`    topic to write about
- `--voice`    professional | casual | technical
- `--provider` groq | openrouter | cerebras (default: from `.env`)

## Output

Files are saved to `output/<topic>_<timestamp>/`.
