"""
Defines the shared state schema for the LangGraph agent pipeline.
Every node reads from and writes to this TypedDict.
"""
from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    # Raw user message
    user_message: str

    # Detected persona: "technical_expert" | "frustrated_user" | "business_executive"
    persona: str

    # Retrieved knowledge-base snippets
    retrieved_context: List[str]

    # Tone/style instruction injected into the prompt
    tone_instruction: str

    # Final generated response
    response: str

    # Whether the conversation should be escalated to a human
    should_escalate: bool

    # Escalation reason (if applicable)
    escalation_reason: str

    # Full conversation history (list of {"role": ..., "content": ...})
    chat_history: List[dict]
