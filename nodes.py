"""
The four LangGraph nodes that make up the agent pipeline:

  1. persona_detection_node  – classifies user persona
  2. context_retrieval_node  – RAG retrieval from FAISS KB
  3. response_generation_node – generates tone-adapted reply via Groq LLM
  4. escalation_check_node   – decides whether to escalate to human agent
"""
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

from agent_state import AgentState
from vector_store import retrieve

load_dotenv()

# ─── LLM initialisation ────────────────────────────────────────────────────
def _get_llm(model: str = "llama3-8b-8192") -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Create a .env file with GROQ_API_KEY=<your_key>."
        )
    return ChatGroq(api_key=api_key, model_name=model, temperature=0.3)


# ─── Persona templates ─────────────────────────────────────────────────────
TONE_MAP = {
    "technical_expert": (
        "You are talking to a technical expert. Use precise technical language, "
        "include relevant API details, error codes, and implementation specifics. "
        "Skip basic explanations. Keep the response concise and information-dense."
    ),
    "frustrated_user": (
        "You are talking to a frustrated or upset customer. Be empathetic, calm, and reassuring. "
        "Acknowledge their frustration first, then provide a clear step-by-step solution. "
        "Avoid jargon. Use simple, friendly language and express genuine concern for their issue."
    ),
    "business_executive": (
        "You are talking to a business executive. Be professional, brief, and outcome-focused. "
        "Highlight business impact, SLAs, cost implications, and strategic benefits. "
        "Avoid technical minutiae. Lead with the bottom-line answer."
    ),
}

ESCALATION_KEYWORDS = [
    "unacceptable", "lawsuit", "legal action", "cancel my account",
    "this is ridiculous", "refund immediately", "terrible", "horrible",
    "worst", "fraud", "scam", "never using again", "demand", "attorney",
    "charge back", "chargeback", "bbb", "better business bureau",
]


# ══════════════════════════════════════════════════════════════════════════════
# NODE 1 – Persona Detection
# ══════════════════════════════════════════════════════════════════════════════
def persona_detection_node(state: AgentState) -> AgentState:
    """
    Uses a zero-shot LLM prompt to classify the user into one of three personas:
      - technical_expert
      - frustrated_user
      - business_executive
    """
    llm = _get_llm()
    user_msg = state["user_message"]

    system_prompt = (
        "You are an expert at analyzing customer messages and detecting user personas.\n"
        "Classify the following customer message into EXACTLY ONE of these three personas:\n"
        "  - technical_expert   : uses technical jargon, asks about APIs/code/configs, calm and analytical\n"
        "  - frustrated_user    : shows frustration, anger, urgency, uses emotional language\n"
        "  - business_executive : asks about ROI, pricing, SLAs, business impact, high-level outcomes\n\n"
        "Respond with ONLY the persona label — nothing else."
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ])

    raw = response.content.strip().lower().replace(" ", "_")
    persona = raw if raw in TONE_MAP else "frustrated_user"

    print(f"[PersonaDetection] Detected persona: {persona}")

    return {
        **state,
        "persona": persona,
        "tone_instruction": TONE_MAP[persona],
    }


# ══════════════════════════════════════════════════════════════════════════════
# NODE 2 – Context Retrieval (RAG)
# ══════════════════════════════════════════════════════════════════════════════
def context_retrieval_node(state: AgentState) -> AgentState:
    """
    Queries the FAISS vector store and retrieves the top-3 relevant KB articles.
    """
    user_msg = state["user_message"]
    docs = retrieve(user_msg, k=3)

    print(f"[ContextRetrieval] Retrieved {len(docs)} KB snippet(s).")

    return {
        **state,
        "retrieved_context": docs,
    }


# ══════════════════════════════════════════════════════════════════════════════
# NODE 3 – Response Generation
# ══════════════════════════════════════════════════════════════════════════════
def response_generation_node(state: AgentState) -> AgentState:
    """
    Generates a persona-adapted response using:
      - retrieved KB context (RAG)
      - tone instruction for the detected persona
      - full conversation history
    """
    llm = _get_llm()

    context_text = "\n\n---\n\n".join(state["retrieved_context"]) if state["retrieved_context"] else "N/A"
    tone = state["tone_instruction"]

    system_prompt = (
        f"You are a helpful, professional customer support agent.\n\n"
        f"TONE INSTRUCTION:\n{tone}\n\n"
        f"KNOWLEDGE BASE CONTEXT (use this to answer):\n{context_text}\n\n"
        f"Instructions:\n"
        f"- Answer the customer's question using the context above.\n"
        f"- If the context does not fully address the question, say so honestly and offer next steps.\n"
        f"- Do NOT make up information not in the context.\n"
        f"- Match the tone instruction strictly."
    )

    messages = [SystemMessage(content=system_prompt)]

    # Inject prior conversation turns
    for turn in state.get("chat_history", []):
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            from langchain.schema import AIMessage
            messages.append(AIMessage(content=turn["content"]))

    messages.append(HumanMessage(content=state["user_message"]))

    response = llm.invoke(messages)
    reply = response.content.strip()

    print(f"[ResponseGeneration] Generated response ({len(reply)} chars).")

    return {
        **state,
        "response": reply,
    }


# ══════════════════════════════════════════════════════════════════════════════
# NODE 4 – Escalation Check
# ══════════════════════════════════════════════════════════════════════════════
def escalation_check_node(state: AgentState) -> AgentState:
    """
    Scans the user message for high-risk keywords that warrant human escalation.
    If triggered, appends a human-handoff note to the response.
    """
    msg_lower = state["user_message"].lower()

    triggered = [kw for kw in ESCALATION_KEYWORDS if kw in msg_lower]
    should_escalate = bool(triggered)
    escalation_reason = f"Escalation keywords detected: {triggered}" if triggered else ""

    if should_escalate:
        handoff_note = (
            "\n\n---\n"
            "⚠️ **This conversation has been flagged for human review.**\n"
            "A support specialist will follow up within 1 business hour. "
            "Your case reference number will be sent to your registered email.\n\n"
            f"*Reason: {escalation_reason}*"
        )
        final_response = state["response"] + handoff_note
        print(f"[EscalationCheck] ESCALATED — {escalation_reason}")
    else:
        final_response = state["response"]
        print("[EscalationCheck] No escalation required.")

    return {
        **state,
        "should_escalate": should_escalate,
        "escalation_reason": escalation_reason,
        "response": final_response,
    }
