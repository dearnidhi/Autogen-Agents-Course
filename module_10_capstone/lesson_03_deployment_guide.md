# Lesson 03: Deployment Guide

## From Local Script to Production Service

The Content Factory is currently a CLI tool. Here's how to deploy it as a production service.

---

## Option 1: Scheduled Job (Simplest)

Run the factory daily via cron or GitHub Actions:

```yaml
# .github/workflows/content_factory.yml
name: Daily Content Factory
on:
  schedule:
    - cron: '0 9 * * 1-5'  # 9 AM, Monday-Friday

jobs:
  generate-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Content Factory
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          python module_10_capstone/capstone_project/main.py \
            --topic "$(cat today_topic.txt)" \
            --voice professional
      - name: Upload output
        uses: actions/upload-artifact@v4
        with:
          name: content-output
          path: module_10_capstone/capstone_project/output/
```

---

## Option 2: FastAPI REST Service

Expose the factory as an HTTP API:

```python
# api.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid

app = FastAPI(title="AI Content Factory API")

class ContentRequest(BaseModel):
    topic: str
    voice: str = "professional"
    provider: str = "groq"

class ContentResponse(BaseModel):
    job_id: str
    status: str
    message: str

jobs = {}  # In production, use Redis

@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued"}

    # Run factory in background (non-blocking)
    background_tasks.add_task(run_factory_job, job_id, request)

    return ContentResponse(
        job_id=job_id,
        status="queued",
        message=f"Content generation started for: {request.topic}"
    )

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

async def run_factory_job(job_id: str, request: ContentRequest):
    from capstone_project.main import run_content_factory
    jobs[job_id] = {"status": "running"}
    try:
        result = run_content_factory(
            topic=request.topic,
            voice=request.voice,
            provider=request.provider,
        )
        jobs[job_id] = {"status": "complete", "output": result}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}
```

Run with: `uvicorn api:app --reload`

---

## Option 3: Streamlit Web UI

```python
# app.py
import streamlit as st

st.title("AI Content Factory")
st.write("Generate multi-platform content from a single topic")

with st.form("content_form"):
    topic = st.text_input("Topic", placeholder="The future of AI agents")
    voice = st.select_slider("Brand Voice", ["casual", "professional", "technical"])
    provider = st.selectbox("Provider", ["groq", "gemini", "openrouter"])
    submitted = st.form_submit_button("Generate Content")

if submitted and topic:
    with st.spinner("AI Content Factory is running..."):
        from capstone_project.main import run_content_factory
        result = run_content_factory(topic=topic, voice=voice, provider=provider)

    st.success("Content generated!")

    tabs = st.tabs(["Blog", "Twitter", "LinkedIn", "Email"])
    with tabs[0]:
        st.markdown(result.get("blog_post", ""))
    with tabs[1]:
        st.markdown(result.get("twitter_thread", ""))
    with tabs[2]:
        st.markdown(result.get("linkedin_post", ""))
    with tabs[3]:
        st.markdown(result.get("email_newsletter", ""))
```

Run with: `streamlit run app.py`

---

## Environment Variables for Production

```bash
# Required
GROQ_API_KEY=your_groq_key
DEFAULT_PROVIDER=groq

# Optional performance settings
AUTOGEN_MAX_RETRIES=5
AUTOGEN_REQUEST_TIMEOUT=60
LOG_LEVEL=INFO
OUTPUT_DIR=/app/output

# Budget enforcement
MAX_COST_PER_RUN=0.10  # $0.10 per run
```

---

## Monitoring in Production

Key metrics to track:
- **Success rate**: % of runs that complete without errors
- **Average latency**: End-to-end time per run
- **Token usage**: Track against rate limits
- **Cost per run**: Alert if trending up
- **Quality score**: Manual sampling + user feedback

Recommended stack: Prometheus + Grafana for metrics, Sentry for error tracking.

---

## Congratulations!

You've completed the AutoGen Course! You now know:

1. **Foundations**: AssistantAgent, UserProxyAgent, conversation patterns
2. **Providers**: Groq, Gemini, OpenRouter, HuggingFace (all free)
3. **Patterns**: Two-agent, sequential, nested, GroupChat, StateFlow
4. **Tools**: Function registration, web search, file operations
5. **Code execution**: LocalCommandLineCodeExecutor, safe sandboxing
6. **Memory**: TeachableAgent, ChromaDB RAG, persistent memory
7. **Projects**: 4 real-world portfolio projects
8. **Advanced**: Custom agents, rate limiting, cost tracking, logging
9. **Capstone**: End-to-end multi-agent content production system

**Next steps:**
- Add your projects to GitHub portfolio
- Read the AutoGen 0.4 migration guide (new async API)
- Join the AutoGen Discord for community support
- Build something unique and share it!
