import streamlit as st
from rag import Retriever
from agents import Orchestrator
from runner import run_code

st.set_page_config(page_title="AI Coding Learning Assistant", page_icon="🤖", layout="wide")

LANGS = {"Python": "python", "C": "c", "C++": "cpp", "Java": "java", "JavaScript": "javascript"}


@st.cache_resource
def load():
    r = Retriever("knowledge_base")
    return r, Orchestrator(r)


retriever, orch = load()

# ---------- Sidebar ----------
st.sidebar.title("🤖 Coding Assistant")
page = st.sidebar.radio("Choose a mode", ["💬 Tutor Chat", "🔍 Code Review", "🐞 Debugger", "📝 Quiz"])
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Knowledge Base (RAG)")
st.sidebar.caption(f"{len(retriever.chunks)} chunks indexed")
up = st.sidebar.file_uploader("Add your notes (.md / .txt)", type=["md", "txt"])
if up and st.sidebar.button("Add to knowledge base"):
    retriever.add_document(up.name, up.read().decode("utf-8", errors="ignore"))
    st.sidebar.success(f"Added {up.name}")


def show_sources(sources):
    if sources:
        with st.expander("📎 Sources used (RAG)"):
            for s in sources:
                st.markdown(f"**{s['source']}** (score {s['score']:.2f})")
                st.caption(s["text"][:300] + "...")


# ---------- Tutor Chat ----------
if page == "💬 Tutor Chat":
    st.header("💬 Ask anything about programming")
    st.caption("The Orchestrator agent routes your message to the Tutor, Reviewer or Debugger agent.")
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            if m.get("agent"):
                st.caption(f"🤝 {m['agent']}")
            st.markdown(m["content"])
    if prompt := st.chat_input("e.g. Explain recursion with an example"):
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = orch.handle(prompt, history)
                    st.caption(f"🤝 {res.agent}")
                    st.markdown(res.text)
                    show_sources(res.sources)
                    st.session_state.chat.append({"role": "assistant", "content": res.text, "agent": res.agent})
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------- Code Review ----------
elif page == "🔍 Code Review":
    st.header("🔍 Code Review")
    lang = st.selectbox("Programming language", list(LANGS))
    code = st.text_area("Paste your code", height=300)
    if st.button("Review my code", type="primary") and code.strip():
        with st.spinner("Reviewing..."):
            try:
                prompt = f"Language: {lang}\n```{LANGS[lang]}\n{code}\n```\n\nReview this {lang} code. Any code you write must be {lang}."
                res = orch.agents["reviewer"].run(prompt)
                st.markdown(res.text)
                show_sources(res.sources)
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Debugger ----------
elif page == "🐞 Debugger":
    st.header("🐞 Debugger (multi-agent pipeline)")
    lang = st.selectbox("Programming language", list(LANGS))
    code = st.text_area("Paste buggy code", height=260)
    err = st.text_area("Error message (optional)", height=80)
    c1, c2 = st.columns(2)
    run_first = c1.checkbox("Run the code first to capture the error", value=True)
    if c2.button("Analyze with all agents", type="primary") and code.strip():
        if run_first and not err.strip():
            out = run_code(code, lang)
            if out["note"]:
                st.info(out["note"])
            else:
                st.subheader("▶ Program output")
                st.code(out["stdout"] or "(no output)")
                if out["stderr"]:
                    st.code(out["stderr"], language="text")
                err = out["stderr"] or ""
        with st.spinner("Debugger → Reviewer → Mentor working..."):
            try:
                r = orch.full_analysis(code, err, lang, LANGS[lang])
                t1, t2, t3 = st.tabs(["🐞 Debug Report", "🔍 Code Review", "🎓 Study Plan"])
                with t1:
                    st.markdown(r["debug"].text)
                    show_sources(r["debug"].sources)
                with t2:
                    st.markdown(r["review"].text)
                with t3:
                    st.markdown(r["plan"].text)
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Quiz ----------
else:
    st.header("📝 Quiz Generator")
    c1, c2, c3 = st.columns(3)
    topic = c1.text_input("Topic", "Python lists and loops")
    level = c2.selectbox("Level", ["beginner", "intermediate", "advanced"])
    n = c3.slider("Questions", 3, 10, 5)
    if st.button("Generate quiz", type="primary"):
        with st.spinner("Generating..."):
            try:
                st.session_state.quiz = orch.quiz.generate(topic, level, n)
                st.session_state.graded = False
                for k in [k for k in st.session_state if k.startswith("q_")]:
                    del st.session_state[k]
            except Exception as e:
                st.error(f"Could not generate quiz: {e}")
    quiz = st.session_state.get("quiz")
    if quiz:
        for i, q in enumerate(quiz):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            st.radio("Choose", q["options"], index=None, key=f"q_{i}", label_visibility="collapsed")
        if st.button("Submit answers"):
            st.session_state.graded = True
        if st.session_state.get("graded"):
            score = 0
            for i, q in enumerate(quiz):
                chosen = st.session_state.get(f"q_{i}")
                correct = q["options"][q["answer_index"]]
                if chosen == correct:
                    score += 1
                    st.success(f"Q{i+1}: Correct ✅ — {q['explanation']}")
                else:
                    st.error(f"Q{i+1}: Wrong ❌ (answer: {correct}) — {q['explanation']}")
            st.metric("Score", f"{score} / {len(quiz)}")