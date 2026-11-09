"""All agents + the orchestrator. Each agent = a role (system prompt) + optional RAG access."""
import json
from dataclasses import dataclass, field
from llm import chat


@dataclass
class AgentResult:
    agent: str
    text: str
    sources: list = field(default_factory=list)


class BaseAgent:
    name = "base"
    system = ""
    use_rag = False
    max_tokens = 1500

    def __init__(self, retriever=None):
        self.retriever = retriever

    def _context(self, query):
        if not (self.use_rag and self.retriever):
            return "", []
        hits = self.retriever.search(query)
        ctx = "\n\n".join(f"[{h['source']}]\n{h['text']}" for h in hits)
        return ctx, hits

    def run(self, user_input: str, history: list | None = None) -> AgentResult:
        ctx, hits = self._context(user_input)
        content = user_input if not ctx else (
            f"Reference material (use if relevant):\n{ctx}\n\n---\nStudent request:\n{user_input}")
        messages = (history or [])[-8:] + [{"role": "user", "content": content}]
        return AgentResult(self.name, chat(self.system, messages, self.max_tokens), hits)


class TutorAgent(BaseAgent):
    name = "Tutor Agent"
    use_rag = True
    system = ("You are a patient programming tutor for students. Explain concepts step by step with simple "
              "analogies and short code examples. Ground answers in the reference material when provided. "
              "End with one small practice exercise. Use markdown.")


class ReviewerAgent(BaseAgent):
    name = "Code Review Agent"
    use_rag = True
    system = ("You are a senior engineer doing a code review for a student. Output markdown with sections: "
              "**Summary**, **Strengths**, **Issues** (bugs, readability, performance, security), "
              "**Improved Code** (full corrected version), **What to Learn Next**. Be kind but precise.")


class DebuggerAgent(BaseAgent):
    name = "Debugging Agent"
    use_rag = True
    system = ("You are a debugging coach. Given code and optionally an error message or output, do: "
              "1) Identify the root cause in plain language, 2) point to the exact line(s), "
              "3) give the fixed code, 4) explain how to avoid this bug in future. "
              "Do not just hand over the answer; teach the reasoning.")


class MentorAgent(BaseAgent):
    name = "Mentor Agent"
    system = ("You are a learning mentor. Given a debugging report and a code review for the same student code, "
              "write a short personalised study plan: 3 weak concepts spotted, 3 resources/topics to study, "
              "and 2 practice tasks. Keep it motivating and under 200 words.")


class QuizAgent(BaseAgent):
    name = "Quiz Agent"
    use_rag = True
    max_tokens = 2500
    system = ("You generate multiple-choice quizzes about programming. Respond with ONLY valid JSON, no prose, "
              'in this format: {"questions":[{"question":"...","options":["A","B","C","D"],'
              '"answer_index":0,"explanation":"..."}]}. Exactly 4 options per question, one correct.')

    def generate(self, topic: str, level: str, n: int) -> list:
        res = self.run(f"Create {n} {level}-level multiple-choice questions on: {topic}")
        raw = res.text
        data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        return data["questions"]


ROUTER_PROMPT = ("Classify the student's message into exactly one label: tutor (concept questions / how-to), "
                 "reviewer (asks to review or improve code), debugger (error, bug, code not working). "
                 "Reply with the single label only.")


class Orchestrator:
    """Supervisor agent: routes requests and coordinates multi-agent pipelines."""

    def __init__(self, retriever):
        self.agents = {
            "tutor": TutorAgent(retriever),
            "reviewer": ReviewerAgent(retriever),
            "debugger": DebuggerAgent(retriever),
        }
        self.mentor = MentorAgent()
        self.quiz = QuizAgent(retriever)

    def route(self, message: str) -> str:
        try:
            label = chat(ROUTER_PROMPT, [{"role": "user", "content": message}], max_tokens=10).strip().lower()
        except Exception:
            return "tutor"
        return next((k for k in self.agents if k in label), "tutor")

    def handle(self, message: str, history: list | None = None) -> AgentResult:
        return self.agents[self.route(message)].run(message, history)

    def full_analysis(self, code: str, error: str = "", language: str = "Python", tag: str = "python") -> dict:
        """Pipeline: Debugger -> Reviewer -> Mentor (each agent builds on the previous output)."""
        prompt = (f"Language: {language}\n```{tag}\n{code}\n```"
                  + (f"\n\nCompiler/runtime error or output:\n```\n{error}\n```" if error else "")
                  + f"\n\nAnswer for {language}. Any code you write must be {language}.")
        debug = self.agents["debugger"].run(prompt)
        review = self.agents["reviewer"].run(prompt)
        plan = self.mentor.run(f"LANGUAGE: {language}\n\nDEBUG REPORT:\n{debug.text}\n\nCODE REVIEW:\n{review.text}")
        return {"debug": debug, "review": review, "plan": plan}