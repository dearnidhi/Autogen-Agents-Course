# 🎬 YouTube Creator Toolkit

Give it one video topic. 4 AI agents make a full content kit:
**title ideas, a complete script, an SEO description, tags, hashtags, and thumbnail text.**

## Agents
1. **Strategist** — picks the angle, audience, and hook
2. **TitleWriter** — 5 catchy titles
3. **ScriptWriter** — a full spoken-style script
4. **SEOWriter** — description, tags, hashtags, thumbnail text

## Run

UI (recommended):
```bash
streamlit run app.py
```

Command line:
```bash
python youtube_toolkit.py --topic "How to learn Python in 2025" --tone funny
```

## Setup
Put your free Groq key in `.env` (already there):
```
DEFAULT_PROVIDER=groq
GROQ_API_KEY=your_key_here
```
Get a free key at https://console.groq.com/keys

This project is **self-contained** — it has its own `llm.py` and `.env`, no shared folders needed.
