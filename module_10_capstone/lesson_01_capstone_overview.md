# Lesson 01: Capstone Project Overview — AI Content Factory

## What You'll Build

The **AI Content Factory** is a multi-agent system that takes a single topic
and produces a complete content package in multiple formats:

| Output | Format | Audience |
|--------|--------|----------|
| Blog Post | 800-word markdown article | General readers |
| Twitter Thread | 8-10 punchy tweets | Social media |
| LinkedIn Post | Professional post with insights | Business professionals |
| Email Newsletter | 300-word subscriber email | Existing audience |

This is a real-world production pattern used by content marketing teams.

---

## Why This is the Perfect Capstone

This project integrates **every concept from the course**:

| Module | Concept Used |
|--------|-------------|
| 01 | AssistantAgent, UserProxyAgent, termination |
| 02 | Multiple provider support (Groq, Gemini, OpenRouter) |
| 03 | Sequential pipeline with carryover |
| 04 | Tool use (web_search, file_manager, formatter) |
| 05 | Code execution for formatting/processing |
| 06 | GroupChat with specialist agents |
| 07 | Research grounding with context injection |
| 08 | Production-quality project structure |
| 09 | Logging, cost tracking, custom agents |

---

## Architecture

```
Topic Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  Research Pipeline                   │
│  Orchestrator → Researcher → Analyst                │
│  (Builds knowledge base from topic)                 │
└─────────────────────────────────────────────────────┘
    │ (knowledge package passed as context)
    ▼
┌─────────────────────────────────────────────────────┐
│                 Content Pipeline                     │
│  BlogWriter → TwitterWriter → LinkedInWriter →      │
│  EmailWriter → BrandReviewer → Publisher            │
└─────────────────────────────────────────────────────┘
    │
    ▼
Output: 4 files saved to output/{topic}/
```

---

## Key Design Decisions

### 1. Two-Stage Pipeline
The factory uses two separate GroupChats:
- **Stage 1 (Research)**: Gathers information, facts, angles
- **Stage 2 (Content)**: Writes for each platform using the research

Why separate? Each stage needs different agents and different termination logic.

### 2. Context Carryover
The research results are explicitly passed as context to the content pipeline.
This ensures all 4 content pieces use consistent facts and messaging.

### 3. Brand Voice Parameter
The `--voice` parameter (professional/casual/technical) adjusts every agent's
system message. This makes the factory adaptable to different brands.

### 4. Publisher Agent
The Publisher agent doesn't write content — it formats and saves each piece
to a file, then returns a summary of what was produced. This is the "last mile"
in content production pipelines.

---

## Running the Capstone

```bash
# Default: professional voice, Groq provider
python module_10_capstone/capstone_project/main.py \
    --topic "The Rise of Multi-Agent AI Systems"

# Custom voice and provider
python module_10_capstone/capstone_project/main.py \
    --topic "Python for Data Science in 2025" \
    --voice casual \
    --provider gemini

# Check output
ls module_10_capstone/capstone_project/output/
```

---

## What Success Looks Like

After running the capstone, you should have:

```
output/
└── rise_of_multi_agent_ai_systems_20250215_143022/
    ├── blog_post.md
    ├── twitter_thread.md
    ├── linkedin_post.md
    ├── email_newsletter.md
    └── production_summary.md
```

Each file should be ready to publish with minimal editing.
