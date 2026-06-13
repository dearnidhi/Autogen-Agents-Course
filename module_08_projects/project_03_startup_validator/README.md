# 🚀 AI Startup Idea Validator

Youtube video:- https://youtu.be/X_eOCZ33eyU

Describe a startup idea. **4 AI experts** judge it from different angles, then a
**Judge** gives a score (/10), a GO / RISKY / NO-GO verdict, and next steps.

## The experts
1. **MarketAnalyst** — is there real demand and competition?
2. **CustomerVoice** — would a real user pay for this?
3. **Skeptic** — the 3 biggest reasons it could fail
4. **MoneyStrategist** — how it makes money and if it can be profitable
5. **Judge** — final score + verdict + next steps

## Run

UI (recommended):
```bash
streamlit run app.py
```

Command line:
```bash
python validator.py --idea "An app that matches old clothes with local thrift buyers."
```

## Setup
Put your free Groq key in `.env` (already there):
```
GROQ_API_KEY=your_key_here
```
Get a free key at https://console.groq.com/keys

Self-contained — its own `llm.py` and `.env`, no shared folders.
