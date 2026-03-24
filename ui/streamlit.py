import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import uuid
import time

from app.graph.builder import build_graph
from app.agents.writer import writer_agent
from app.agents.refiner import refinement_agent
from app.graph.state import GraphState

from app.memory.session_store import save_session, load_sessions, delete_session

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="Synthra AI", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Synthra AI")
st.caption("🟢 Ready for research")
st.caption("Multi-Agent Autonomous Research System")

graph = build_graph()

# ---------------- MULTI SESSION INIT ----------------
if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

if "session_id" not in st.session_state or st.session_state.session_id not in st.session_state.sessions:
    new_id = str(uuid.uuid4())

    st.session_state.session_id = new_id
    st.session_state.sessions[new_id] = {
        "title": "New Research",
        "messages": [],
        "result": None,
        "stage": "input",
        "final_report": None
    }

# current session
session = st.session_state.sessions[st.session_state.session_id]

# ---------------- SIDEBAR ----------------
st.sidebar.title("🧠 Sessions")

# ➕ New Research (top priority button)
if st.sidebar.button("➕ New Research", use_container_width=True):
    new_id = str(uuid.uuid4())

    st.session_state.sessions[new_id] = {
        "title": "New Research",
        "messages": [],
        "result": None,
        "stage": "input",
        "final_report": None
    }

    st.session_state.session_id = new_id
    save_session(new_id, st.session_state.sessions[new_id])
    st.rerun()

st.sidebar.markdown("---")

# Session list
for sid, data in st.session_state.sessions.items():
    col1, col2 = st.sidebar.columns([3, 1])

    title = data.get("title", "New Research")

    if col1.button(title[:25], key=f"sel_{sid}"):
        st.session_state.session_id = sid
        st.rerun()

    if col2.button("❌", key=f"del_{sid}"):
        delete_session(sid)
        del st.session_state.sessions[sid]

        if st.session_state.session_id == sid:
            if st.session_state.sessions:
                st.session_state.session_id = list(st.session_state.sessions.keys())[0]
            else:
                new_id = str(uuid.uuid4())
                st.session_state.sessions[new_id] = {
                    "title": "New Research",
                    "messages": [],
                    "result": None,
                    "stage": "input",
                    "final_report": None
                }
                st.session_state.session_id = new_id

        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Session ID")
st.sidebar.code(st.session_state.session_id[:12])

# ---------------- CHAT HISTORY ----------------
for msg in session["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
if session["stage"] == "input" and not session["messages"]:
    st.markdown("""
    ### 👋 Welcome to Synthra AI

    Try queries like:

    - Impact of AI on jobs in India  
    - Future of AI in healthcare  
    - Compare AI adoption in India vs USA  

    ⚡ Features:
    - Multi-agent research system  
    - Critique & refinement loop  
    - Execution timeline  
    - Persistent sessions  
    """)

    st.markdown("---")

query = st.chat_input("Ask your research query...")

if query:
    session["messages"].append({"role": "user", "content": query})
    if session["title"] == "New Research":
        session["title"] = query[:40]
    save_session(st.session_state.session_id, session)


    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        progress = st.empty()

        progress.markdown("🧠 Planning...")
        progress.markdown("🌐 Searching...")
        progress.markdown("📊 Ranking sources...")
        progress.markdown("🧐 Critiquing...")

        result = graph.invoke({
            "query": query,
            "session_id": st.session_state.session_id
        })

        progress.markdown("✅ Research Ready")

    session["result"] = result
    session["stage"] = "review"

    save_session(st.session_state.session_id, session)

    st.rerun()

# ---------------- REVIEW ----------------
if session["stage"] == "review" and session["result"]:

    result = session["result"]

    with st.chat_message("assistant"):

        st.subheader("🧐 Critique")
        st.write(result["critique"])

        st.subheader("🌐 Sources")
        for s in result["ranked_sources"][:5]:
            st.markdown(f"- [{s['title']}]({s['url']})")
        with st.expander("📊 Agent Timeline"):
            for step in result.get("timeline", []):
                st.markdown(f"- {step}")

        col1, col2 = st.columns(2)

        # APPROVE
        if col1.button("✅ Approve"):
            with st.spinner("✍️ Generating report..."):
                state_obj = GraphState(**result)
                final = writer_agent(state_obj)

            session["final_report"] = final["final_report"]
            session["stage"] = "final"
            save_session(st.session_state.session_id, session)
            st.rerun()

        # REFINE
        if col2.button("🔁 Refine"):
            with st.spinner("🔁 Improving research..."):
                state_obj = GraphState(**result)

                refined = refinement_agent(state_obj)

                state_obj.query = refined["query"]
                state_obj.refinement_count = refined["refinement_count"]

                new_result = graph.invoke(state_obj.dict())

            session["result"] = new_result
            save_session(st.session_state.session_id, session)
            st.rerun()

# ---------------- STREAM FUNCTION ----------------
def stream_text(text, placeholder):
    words = text.split(" ")
    streamed = ""

    for word in words:
        streamed += word + " "
        placeholder.markdown(streamed)
        time.sleep(0.02)

    return streamed

# ---------------- FINAL ----------------
if session["stage"] == "final":

    report = session["final_report"]

    with st.chat_message("assistant"):

        st.subheader("📄 Final Report")
        st.markdown("---")

        # 🔥 Streaming output
        placeholder = st.empty()
        stream_text(report, placeholder)

        st.success("✅ Report Generated")

        # ---------------- TIMELINE ----------------
        if session.get("result") and session["result"].get("timeline"):
            with st.expander("📊 Execution Timeline"):
                for step in session["result"]["timeline"]:
                    st.markdown(f"- {step}")

        # ---------------- ACTION BUTTONS ----------------
        col1, col2 = st.columns(2)

        # 🔄 New Research
        if col1.button("🔄 New Research"):
            new_id = str(uuid.uuid4())

            st.session_state.sessions[new_id] = {
                "title": "New Research",
                "messages": [],
                "result": None,
                "stage": "input",
                "final_report": None
            }

            st.session_state.session_id = new_id

            save_session(new_id, st.session_state.sessions[new_id])

            st.rerun()

        # 🧠 Keep working on same topic (nice UX touch)
        if col2.button("➕ Continue Research"):
            session["stage"] = "input"
            st.rerun()