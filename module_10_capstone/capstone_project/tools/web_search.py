"""
Simulated web search tool for the Content Factory.

In production, replace with real APIs:
- Google Custom Search API
- Tavily AI Search
- Bing Search API
- SerpAPI
"""

from typing import Annotated
from autogen import register_function


# Simulated search results database
SEARCH_KNOWLEDGE = {
    "ai agents": {
        "facts": [
            "The AI agent market is projected to reach $47B by 2030",
            "Microsoft AutoGen has 25,000+ GitHub stars",
            "80% of Fortune 500 companies are piloting AI agents in 2024",
            "Multi-agent systems reduce task completion time by 40-60% in studies",
        ],
        "sources": ["TechCrunch", "Gartner", "McKinsey Digital Report 2024"],
    },
    "python": {
        "facts": [
            "Python is the #1 programming language on the TIOBE index",
            "Over 8 million Python developers worldwide",
            "Python powers 70% of AI/ML projects",
        ],
        "sources": ["TIOBE Index", "Stack Overflow Survey 2024"],
    },
    "default": {
        "facts": [
            "This topic is seeing rapid growth and adoption",
            "Industry experts predict significant changes in the next 2-3 years",
            "Early adopters are reporting 30-50% efficiency gains",
        ],
        "sources": ["Industry Reports", "Expert Analysis"],
    },
}


def simulated_web_search(
    query: Annotated[str, "Search query string"],
    max_results: Annotated[int, "Maximum number of results to return (1-5)"] = 3,
) -> str:
    """
    Simulates a web search and returns relevant facts.

    In production, replace this function body with a real search API call.
    The function signature (name, parameters, return type) stays the same.
    """
    query_lower = query.lower()

    # Find matching knowledge base
    results = SEARCH_KNOWLEDGE["default"]
    for keyword, data in SEARCH_KNOWLEDGE.items():
        if keyword in query_lower:
            results = data
            break

    facts = results["facts"][:max_results]
    sources = results["sources"]

    output = f"Search results for: '{query}'\n\n"
    for i, fact in enumerate(facts, 1):
        output += f"{i}. {fact}\n"
    output += f"\nSources: {', '.join(sources)}"

    return output


def get_trending_angles(
    topic: Annotated[str, "Topic to find trending angles for"],
) -> str:
    """Returns trending content angles for a given topic."""
    angles = [
        f"Contrarian take: Why {topic} might be overhyped",
        f"The practical guide: {topic} for non-experts",
        f"The data story: What the numbers say about {topic}",
        f"Future prediction: Where {topic} will be in 5 years",
        f"Behind the scenes: How leading companies use {topic}",
    ]
    return "\n".join(f"- {angle}" for angle in angles)


def register_search_tools(researcher_agent, executor_agent):
    """Registers search tools with the researcher agent."""
    register_function(
        simulated_web_search,
        caller=researcher_agent,
        executor=executor_agent,
        name="web_search",
        description="Search the web for facts and information about a topic",
    )

    register_function(
        get_trending_angles,
        caller=researcher_agent,
        executor=executor_agent,
        name="get_trending_angles",
        description="Get trending content angles for a topic to maximize engagement",
    )
