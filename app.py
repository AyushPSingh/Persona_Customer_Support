"""
Streamlit UI for the Persona-Adaptive Customer Support Agent.
Clean, functional interface — no extra-fancy styling.
"""
import streamlit as st
from agent import run_agent

# ─── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Persona-Adaptive Customer Support",
    page_icon="🤖",
    layout="centered",
)

# ─── Minimal custom CSS ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Slightly tighter chat bubbles */
    .stChatMessage { border-radius: 8px; }

    /* Persona badge colours */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .badge-technical  { background:#dbeafe; color:#1e40af; }
    .badge-frustrated { background:#fee2e2; color:#991b1b; }
    .badge-executive  { background:#d1fae5; color:#065f46; }
    .badge-escalated  { background:#fef3c7; color:#92400e; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ───────────────────────────────────────────────────────────────
st.title("🤖 Persona-Adaptive Customer Support")
st.caption(
    "Powered by **LangGraph · LangChain · Groq (Llama3)**. "
    "Detects your persona and adapts its tone automatically."
)
st.divider()

# ─── Sidebar: info + reset ────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
This agent:
- 🔍 **Detects** your persona (Technical Expert, Frustrated User, Business Executive)
- 📚 **Retrieves** relevant knowledge-base articles via RAG (FAISS)
- 🎭 **Adapts** its response tone to match your persona
- 🚨 **Escalates** to a human agent when high-risk phrases are detected

**Try asking:**
- *"How do I handle 429 rate-limit errors in my API calls?"* (Technical)
- *"I've been charged twice and no one is helping me!"* (Frustrated)
- *"What's the ROI of your Enterprise plan?"* (Executive)
        """
    )
    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.meta = []
        st.rerun()

    st.divider()
    st.subheader("📊 Session Stats")
    if "meta" in st.session_state and st.session_state.meta:
        turns = st.session_state.meta
        escalations = sum(1 for m in turns if m.get("escalated"))
        persona_counts = {}
        for m in turns:
            p = m.get("persona", "unknown")
            persona_counts[p] = persona_counts.get(p, 0) + 1

        st.metric("Total Turns", len(turns))
        st.metric("Escalations", escalations)
        st.write("**Personas detected:**")
        for persona, count in persona_counts.items():
            st.write(f"- {persona.replace('_', ' ').title()}: {count}")
    else:
        st.write("*No conversation yet.*")

# ─── Session state ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role", "content"}

if "meta" not in st.session_state:
    st.session_state.meta = []      # {"persona", "escalated"} per assistant turn

# ─── Render existing chat ─────────────────────────────────────────────────
meta_idx = 0
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and meta_idx < len(st.session_state.meta):
            m = st.session_state.meta[meta_idx]
            persona = m.get("persona", "")
            escalated = m.get("escalated", False)
            _badge_class = {
                "technical_expert": "badge-technical",
                "frustrated_user": "badge-frustrated",
                "business_executive": "badge-executive",
            }.get(persona, "badge-frustrated")
            _label = persona.replace("_", " ").title()
            html = f'<span class="badge {_badge_class}">👤 {_label}</span>'
            if escalated:
                html += ' &nbsp;<span class="badge badge-escalated">🚨 Escalated</span>'
            st.markdown(html, unsafe_allow_html=True)
            meta_idx += 1
        st.markdown(msg["content"])

# ─── Chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your support question here…"):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build chat history (exclude the message we just added)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                result = run_agent(prompt, history)
                persona = result.get("persona", "unknown")
                escalated = result.get("should_escalate", False)
                response = result.get("response", "I'm sorry, something went wrong.")

                # Persona + escalation badges
                _badge_class = {
                    "technical_expert": "badge-technical",
                    "frustrated_user": "badge-frustrated",
                    "business_executive": "badge-executive",
                }.get(persona, "badge-frustrated")
                _label = persona.replace("_", " ").title()
                html = f'<span class="badge {_badge_class}">👤 {_label}</span>'
                if escalated:
                    html += ' &nbsp;<span class="badge badge-escalated">🚨 Escalated</span>'
                st.markdown(html, unsafe_allow_html=True)

                st.markdown(response)

                # Debug expander (optional)
                with st.expander("🔍 Debug Info"):
                    st.write("**Tone instruction:**", result.get("tone_instruction", ""))
                    st.write("**Escalation reason:**", result.get("escalation_reason", "None"))
                    st.write("**KB snippets retrieved:**")
                    for i, snippet in enumerate(result.get("retrieved_context", []), 1):
                        st.text_area(f"Snippet {i}", snippet, height=80, key=f"snip_{len(st.session_state.messages)}_{i}")

            except Exception as e:
                response = f"⚠️ Error: {e}"
                st.error(response)
                persona = "unknown"
                escalated = False

    # Persist
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.meta.append({"persona": persona, "escalated": escalated})
