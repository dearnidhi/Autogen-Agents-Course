# AI Content Factory — AutoGen Capstone Project

The final project of the course. Takes one topic and produces a complete, publish-ready content package for 4 platforms simultaneously.

## What It Produces

| File | Platform | Format | Length |
|------|----------|--------|--------|
| `blog_post.md` | Blog/Website | Markdown article | ~800 words |
| `twitter_thread.md` | Twitter/X | Numbered thread | 8-10 tweets |
| `linkedin_post.md` | LinkedIn | Professional post | ~1200 chars |
| `email_newsletter.md` | Email | Newsletter | ~300 words |

## Architecture

```
Topic
  ↓
[Stage 1: Research Pipeline]
  Orchestrator → Researcher → Analyst
                                 ↓
                         Knowledge Package
                                 ↓
[Stage 2: Content Pipeline]
  BlogWriter → TwitterWriter → LinkedInWriter → EmailWriter
                                                      ↓
                                              BrandReviewer
                                                      ↓
                                               Publisher
                                                      ↓
                                          output/{topic}_{timestamp}/
```

## Usage

```bash
# Default: professional voice
python module_10_capstone/capstone_project/main.py \
    --topic "The Rise of Multi-Agent AI Systems"

# Casual blog voice (tech newsletter style)
python module_10_capstone/capstone_project/main.py \
    --topic "Why Python Will Dominate AI in 2025" \
    --voice casual

# Technical voice (practitioner audience)
python module_10_capstone/capstone_project/main.py \
    --topic "Implementing RAG with ChromaDB and AutoGen" \
    --voice technical \
    --provider gemini

# Skip research (reuse cached) — faster for testing
python module_10_capstone/capstone_project/main.py \
    --topic "AI Productivity Tools" \
    --skip-research
```

## Output Example

```
output/
└── the_rise_of_multi_agent_ai_systems_20250215_143022/
    ├── blog_post.md            # 847 words
    ├── twitter_thread.md       # 10 tweets
    ├── linkedin_post.md        # 1,312 characters
    ├── email_newsletter.md     # 312 words
    ├── knowledge_package.md    # Research used by all writers
    └── production_summary.json # Metadata and word counts
```

## AutoGen Concepts Demonstrated

| Concept | Where Used |
|---------|-----------|
| AssistantAgent | All 8 specialist agents |
| UserProxyAgent | Orchestrator, ContentAdmin |
| GroupChat | Both pipelines |
| round_robin speaker selection | Research + Content pipelines |
| Carryover (knowledge package) | Research → Content handoff |
| Termination messages | RESEARCH_PACKAGE_COMPLETE, FACTORY_COMPLETE |
| Multi-provider support | `--provider` flag |
| File tool integration | Publisher saves output files |
| Custom agent patterns | From Module 09 |
| Cost-aware design | Minimal rounds, focused prompts |

## Extension Ideas

- Add `--audience` parameter (beginners/experts/executives)
- Connect to real web search (Tavily, SerpAPI, Google CSE)
- Auto-schedule posts via Buffer or Hootsuite API
- Add image generation prompts (DALL-E / Midjourney) for each piece
- Build a Streamlit UI for non-technical users
- Add A/B variants: generate 2 versions of each piece
