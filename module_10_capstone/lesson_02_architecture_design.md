# Lesson 02: Architecture Design

## The Content Factory Architecture in Detail

### System Components

```
capstone_project/
├── main.py                    ← Entry point. Orchestrates the two pipelines.
├── agents/
│   ├── orchestrator.py        ← Controls the research pipeline
│   ├── researcher.py          ← Gathers facts and angles on the topic
│   ├── analyst.py             ← Synthesizes research into a knowledge package
│   ├── writer.py              ← 4 writer agents (Blog, Twitter, LinkedIn, Email)
│   ├── reviewer.py            ← Brand voice reviewer
│   └── publisher.py           ← Formats and saves all outputs
├── tools/
│   ├── web_search.py          ← Simulated web search tool
│   ├── file_manager.py        ← Save/load output files
│   ├── data_processor.py      ← Token counting, text statistics
│   └── formatter.py           ← Platform-specific formatting rules
├── workflows/
│   ├── research_pipeline.py   ← Stage 1: Research GroupChat
│   └── content_pipeline.py    ← Stage 2: Content GroupChat
└── output/                    ← Generated content saved here
```

---

## Data Flow

### Stage 1: Research Pipeline

```python
# Input
topic = "The Rise of Multi-Agent AI Systems"

# Research pipeline produces:
knowledge_package = {
    "topic": topic,
    "key_facts": [...],
    "statistics": [...],
    "expert_quotes": [...],
    "angles": [...],  # Different perspectives to write from
    "target_keywords": [...],
    "summary": "..."  # 2-paragraph synthesis
}
```

### Stage 2: Content Pipeline

```python
# Each writer receives:
{
    "knowledge_package": knowledge_package,
    "voice": "professional",  # or casual/technical
    "platform": "blog"  # or twitter/linkedin/email
}

# Each writer produces:
{
    "platform": "blog",
    "content": "# Title\n\n...",
    "word_count": 847,
    "status": "DRAFT_COMPLETE"
}
```

---

## Agent Design Philosophy

### Research Agents — Be a Reporter
```
Orchestrator: "Find me everything about this topic"
Researcher: "Here are 10 facts, 3 statistics, 2 expert angles"
Analyst: "Here's what matters and why, formatted for writers"
```

### Content Agents — Be a Platform Native
Each writer knows the platform deeply:
- **BlogWriter**: SEO structure, headers, internal links, 800 words
- **TwitterWriter**: Hook, value, CTA, 280 chars per tweet, 8-10 tweets
- **LinkedInWriter**: Professional insight, no hashtag spam, 1300 chars
- **EmailWriter**: Subject line, preview text, scannable, personal tone

### Brand Reviewer — Be the Editor-in-Chief
```
"Does this match the [voice] brand? Too formal? Too casual?
 Check: consistency across pieces, no contradictions, tone match"
```

---

## Why GroupChat for Stage 2?

We could use sequential `initiate_chat()` chains. But GroupChat gives us:
1. **Parallel awareness**: All writers see each other's drafts (consistency)
2. **Brand reviewer**: Can comment on any piece mid-pipeline
3. **Natural ordering**: `speaker_selection_method="round_robin"` enforces sequence

Alternative: Sequential chains with carryover. Choose based on whether
writers need to see each other's work (GroupChat) or work independently (sequential).

---

## Production Considerations

### Rate Limiting
4 writers + reviewer = 5+ LLM calls per run.
At Groq's 30 RPM limit, space calls 2 seconds apart.
See `module_09_advanced/03_rate_limit_handling.py`.

### Token Budget
A typical content factory run uses:
- Research: ~2000 tokens (input + output)
- 4 content pieces: ~1000 tokens each
- Review pass: ~500 tokens
- **Total: ~6500 tokens per run**

### Caching Research
If running multiple voice variants on the same topic,
cache the knowledge_package and skip Stage 1.
