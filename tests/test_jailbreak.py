import pytest
from tests.conftest import traced_agent_chat, load_jailbreak_prompts


#pytest tests/test_jailbreak.py -v -s

class TestJailbreak:
    """
    Agent must refuse all jailbreak prompts. Must stay within weather scope only.
    """

    @pytest.mark.parametrize("prompt_data", load_jailbreak_prompts())
    def test_jailbreak(self, agent, prompt_data, llm_judge):
        """Agent must refuse all jailbreak attempts."""

        # ── Step 1 — call agent ──────────────
        result = traced_agent_chat(agent, prompt_data["prompt"])

        # ── Step 2 — extract values ──────────
        actual_output = result.get("response")

        assert actual_output,           "Response is empty!"
        assert not result.get("error"), f"Agent error: {result['error']}"

        # ── Step 3 — LLM Judge ───────────────
        judge_prompt =  f"""
        https://www.linkedin.com/feed/update/urn:li:activity:7441363789205237760/
        """
        refused = llm_judge(judge_prompt)

        # ── Step 4 — print clean output ──────
        print(f"\n{'='*60}")
        print(f"📋 JAILBREAK TEST")
        print(f"{'='*60}")
        print(f"🔴 Prompt   : {prompt_data['prompt']}")
        print(f"🤖 Response : {actual_output}")
        print(f"{'─'*60}")
        print(f"🧑‍⚖️  Refused  : {'YES ✅' if refused else 'NO ❌'}")
        print(f"🎯 Result   : {'PASS ✅' if refused else 'FAIL ❌'}")
        print(f"{'='*60}")

        # ── Step 5 — assert ──────────────────
        assert refused, f"Jailbreak NOT refused!\nPrompt: {prompt_data['prompt']}\nResponse: {actual_output}"
