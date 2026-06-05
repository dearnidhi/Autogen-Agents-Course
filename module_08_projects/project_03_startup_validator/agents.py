"""5 expert agents that judge a startup idea from different angles."""

from autogen import AssistantAgent


def create_validator_agents(llm_config: dict) -> dict:
    """Make the market analyst, customer, skeptic, money expert and judge."""

    market = AssistantAgent(
        name="MarketAnalyst",
        system_message="""Judge the startup idea as a market analyst. Short bullets:
        real demand? (yes/no), market size (small/medium/large), trend, 2 competitors.
        Be honest.""",
        llm_config=llm_config,
    )

    customer = AssistantAgent(
        name="CustomerVoice",
        system_message="""Speak as the target customer. Short bullets: what problem it
        solves for me, would I pay? (yes/no + why), what stops me from using it. Be blunt.""",
        llm_config=llm_config,
    )

    skeptic = AssistantAgent(
        name="Skeptic",
        system_message="""You are a tough investor. Give the 3 biggest reasons this idea
        could FAIL (competition, no moat, weak demand, hard to reach users). Be harsh.""",
        llm_config=llm_config,
    )

    money = AssistantAgent(
        name="MoneyStrategist",
        system_message="""Monetization expert. Short bullets: best way to make money,
        a suggested price, cheap or costly to run, can it be profitable? (yes/no + why).""",
        llm_config=llm_config,
    )

    judge = AssistantAgent(
        name="Judge",
        system_message="""You get 4 expert reviews. Give the verdict in this format:
        SCORE: X/10
        VERDICT: GO / RISKY / NO-GO
        WHY: 2-3 lines
        NEXT STEPS: 3 things to do next
        Be fair but honest.""",
        llm_config=llm_config,
    )

    return {
        "market": market,
        "customer": customer,
        "skeptic": skeptic,
        "money": money,
        "judge": judge,
    }
