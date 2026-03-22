# 🧪 Agent Testing Framework
> Testing LLM Agents beyond string matching — using LLM-as-Judge and Semantic Similarity.

This repo shares the **core testing patterns** from my presentation on Agent Testing.  
The focus is on *how to evaluate* an LLM agent — not just whether it runs, but whether it *behaves correctly*.

---

## 🤔 Why Is Agent Testing Hard?

Traditional testing breaks for LLM agents because:

- Responses are **non-deterministic** — same question, different wording every time
- Correctness is **semantic** — "I can't help with that" and "That's outside my scope" mean the same thing
- Threats are **adversarial** — jailbreaks, prompt injections, off-topic manipulation

**String matching won't cut it. You need smarter evaluation.**

---

## 🧠 Three Evaluation Strategies

This framework demonstrates three distinct strategies — each chosen for a specific problem:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Strategy 1: LLM Judge (Guardrail Testing)             │
│   → Did the agent redirect off-topic questions?         │
│                                                         │
│   Strategy 2: LLM Judge (Jailbreak Testing)             │
│   → Did the agent resist adversarial prompts?           │
│                                                         │
│   Strategy 3: Cosine Similarity (Answer Relevancy)      │
│   → Is the agent's response semantically relevant?      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Strategy 1 & 2 — LLM-as-Judge

Instead of checking the response with regex, a **second LLM acts as a judge** and semantically evaluates the agent's behaviour.

```
User Prompt
    │
    ▼
[ Agent Under Test ]
    │
    ▼
Agent Response
    │
    ▼
[ LLM Judge ] ◄── Judge Prompt (defines pass/fail criteria)
    │
    ▼
YES / NO verdict
    │
    ▼
pytest assert ✅ or ❌
```

> 💬 Judge prompt pattern inspired by:  
> https://www.linkedin.com/feed/update/urn:li:activity:7441363789205237760/

---

## 🗂️ Repo Structure

```
├── tests/
│   ├── conftest.py                 ← Agent fixtures (implement your own)
│   ├── test_guardrailwithjudge.py  ← Strategy 1: Guardrail + LLM Judge
│   ├── test_jailbreak.py           ← Strategy 2: Jailbreak + LLM Judge
│   ├── test_answerrel.py           ← Strategy 3: Answer Relevancy + Cosine Similarity
│   └── data/
│       └── test_answer.csv         ← Sample: question, expected, threshold
├── requirements.txt
└── pytest.ini
```

---

## ⚙️ How to Run

```bash
# Install dependencies
pip install pytest sentence-transformers pandas numpy requests

# Run individual test files
pytest tests/test_guardrailwithjudge.py -v -s
pytest tests/test_jailbreak.py -v -s
pytest tests/test_answerrel.py -v -s
```

---

## 🔌 Plug In Your Own Agent

The `conftest.py` exposes three interfaces you need to implement for your own agent:

```python
def traced_agent_chat(agent, prompt) -> dict:
    """
    Call your agent and return:
    { "response": str, "error": str|None }
    Implement this to wrap your own agent endpoint.
    """
    raise NotImplementedError

def llm_judge(judge_prompt: str) -> bool:
    """
    Send judge_prompt to an LLM.
    Return True if answer is YES, False if NO.
    Use Claude, GPT, or any model you prefer.
    """
    raise NotImplementedError

def load_railguard_prompts() -> list[dict]:
    """
    Return list of:
    [{"prompt": str, "expected_behavior": "redirect" | "noredirect"}]
    Load from your own YAML / CSV / JSON.
    """
    raise NotImplementedError
```



## 🙏 Credits & References

- LLM Judge pattern: https://www.linkedin.com/feed/update/urn:li:activity:7441363789205237760/
- Sentence Transformers: https://www.sbert.net
- Pytest: https://docs.pytest.org

---

## ⚠️ Disclaimer

This repo shares the **testing patterns and logic only**.  
The agent implementation, full prompt bank, and internal infrastructure are not included.  
This is intentional — the goal is to share the *approach*, not the full product.

---

*If this was useful, feel free to ⭐ the repo or connect on LinkedIn.*