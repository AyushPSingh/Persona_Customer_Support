"""
Assembles the LangGraph state machine and exposes a single entry-point:
    run_agent(user_message, chat_history) -> dict
"""
from langgraph.graph import StateGraph, END

from agent_state import AgentState
from nodes import (
    persona_detection_node,
    context_retrieval_node,
    response_generation_node,
    escalation_check_node,
)


def build_graph() -> StateGraph:
    """
    Graph layout:
        persona_detection → context_retrieval → response_generation → escalation_check → END
    """
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("persona_detection", persona_detection_node)
    graph.add_node("context_retrieval", context_retrieval_node)
    graph.add_node("response_generation", response_generation_node)
    graph.add_node("escalation_check", escalation_check_node)

    # Wire edges (linear pipeline)
    graph.set_entry_point("persona_detection")
    graph.add_edge("persona_detection", "context_retrieval")
    graph.add_edge("context_retrieval", "response_generation")
    graph.add_edge("response_generation", "escalation_check")
    graph.add_edge("escalation_check", END)

    return graph.compile()


# Compiled graph singleton (built once per process)
_app = None


def _get_app():
    global _app
    if _app is None:
        _app = build_graph()
    return _app


def run_agent(user_message: str, chat_history: list | None = None) -> dict:
    """
    Run the full agent pipeline for a single user turn.

    Args:
        user_message:  The latest message from the user.
        chat_history:  List of {"role": "user"|"assistant", "content": str} dicts
                       representing prior turns.

    Returns:
        A dict with keys: persona, response, should_escalate, escalation_reason,
        retrieved_context, tone_instruction.
    """
    app = _get_app()

    initial_state: AgentState = {
        "user_message": user_message,
        "persona": "",
        "retrieved_context": [],
        "tone_instruction": "",
        "response": "",
        "should_escalate": False,
        "escalation_reason": "",
        "chat_history": chat_history or [],
    }

    result = app.invoke(initial_state)
    return result


# ─── CLI smoke-test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_messages = [
        "How do I authenticate my API requests and what are the rate limits?",
        "I've been charged twice this month and nobody is helping me! This is unacceptable!",
        "What is the ROI on upgrading to Enterprise, and what SLA can you guarantee?",
    ]

    for msg in test_messages:
        print("\n" + "=" * 70)
        print(f"USER: {msg}")
        print("-" * 70)
        result = run_agent(msg)
        print(f"PERSONA : {result['persona']}")
        print(f"ESCALATE: {result['should_escalate']}")
        print(f"RESPONSE:\n{result['response']}")
