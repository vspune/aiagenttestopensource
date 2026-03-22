"""
agent.py
--------
Core Weather Agent powered by OLLAMA.
Location: src/agent.py

Parameters exposed:
  - temperature    : randomness (0.0 - 2.0)
  - max_tokens     : response length
  - top_p          : word pool size (0.0 - 1.0)
  - top_k          : word choice limit (1 - 100)
  - repeat_penalty : stops repetition (1.0 - 2.0)
"""

import sys
import os
import json
import time
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Fix path FIRST
sys.path.insert(0, os.path.dirname(__file__))

# Then import tools
from tools import TOOL_REGISTRY, TOOL_SCHEMAS

# Add src/ folder to path
sys.path.insert(0, os.path.dirname(__file__))


# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL   = "qwen2.5:7b"

SYSTEM_PROMPT = """You are a helpful Weather Assistant.
You have access to these tools:
- get_weather(city): current weather
- get_forecast(city, days): N-day forecast
- convert_temperature(value, from_unit, to_unit): unit conversion
- get_location_info(city): city details

When the user asks about weather or locations, call the appropriate tool.
Always respond in a friendly, concise manner.
If a city is invalid or not found, politely inform the user.
Never make up weather data — always use tools for real data.
"""


# ─────────────────────────────────────────────────────────
# WEATHER AGENT CLASS
# ─────────────────────────────────────────────────────────
class WeatherAgent:
    """
    OLLAMA-powered Weather Agent with 4 tools.

    Args:
        model          (str):   OLLAMA model to use
        base_url       (str):   OLLAMA server URL
        tools_enabled  (bool):  Enable/disable tool calling
        temperature    (float): Randomness — 0.0 (stable) to 2.0 (creative)
        max_tokens     (int):   Max response length in tokens
        top_p          (float): Word pool size — 0.0 to 1.0
        top_k          (int):   Word choice limit — 1 to 100
        repeat_penalty (float): Stops repetition — 1.0 to 2.0
        stateful       (bool):  Maintain conversation history
    """

    def __init__(
        self,
        model:          str   = DEFAULT_MODEL,
        base_url:       str   = OLLAMA_BASE_URL,
        tools_enabled:  bool  = True,
        temperature:    float = 0.7,
        max_tokens:     int   = 1024,
        top_p:          float = 0.9,
        top_k:          int   = 40,
        repeat_penalty: float = 1.1,
        stateful:       bool  = True,
    ):
        # ── Server settings ───────────────────────────────
        self.model    = model
        self.base_url = base_url

        # ── Behaviour settings ────────────────────────────
        self.tools_enabled = tools_enabled
        self.stateful      = stateful

        # ── LLM parameters ────────────────────────────────
        self.temperature    = temperature     # 0.0=stable, 2.0=creative
        self.max_tokens     = max_tokens      # max words in response
        self.top_p          = top_p           # word pool size
        self.top_k          = top_k           # word choice limit
        self.repeat_penalty = repeat_penalty  # stops repetition

        # ── Conversation history ──────────────────────────
        self.history: list = []               # only used when stateful=True


    # ─────────────────────────────────────────────────────
    # PUBLIC — chat() : main entry point
    # ─────────────────────────────────────────────────────
    def chat(self, user_message: str) -> dict:
        """
        Send a message to the agent and get a response.

        Returns dict with keys:
            response      (str)        - Final text answer
            tool_called   (str|None)   - Tool name if used
            tool_args     (dict|None)  - Arguments passed to tool
            tool_result   (any|None)   - Raw tool output
            latency_sec   (float)      - Total response time
            model         (str)        - Model used
            error         (str|None)   - Error message if failed
        """
        start = time.time()

        # ── Build message list ────────────────────────────
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if self.stateful:
            messages += self.history
        messages.append({"role": "user", "content": user_message})

        # ── Prepare result template ───────────────────────
        result = {
            "response":    None,
            "tool_called": None,
            "tool_args":   None,
            "tool_result": None,
            "latency_sec": None,
            "model":       self.model,
            "error":       None,
        }

        try:
            # ── Step 1: Build payload with ALL LLM params ─
            payload = {
                "model":    self.model,
                "messages": messages,
                "stream":   False,
                "options": {
                    "temperature":    self.temperature,    # 0.0 - 2.0
                    "num_predict":    self.max_tokens,     # response length
                    "top_p":          self.top_p,          # word pool
                    "top_k":          self.top_k,          # word limit
                    "repeat_penalty": self.repeat_penalty, # repetition
                },
            }

            # ── Add tools only if enabled ──────────────────
            if self.tools_enabled:
                payload["tools"] = TOOL_SCHEMAS

            # ── Step 2: Call OLLAMA ────────────────────────
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=250,
            )
            resp.raise_for_status()
            data    = resp.json()
            message = data.get("message", {})

            # ── Step 3: Check if model wants to call tool ──
            tool_calls = message.get("tool_calls", [])

            if tool_calls and self.tools_enabled:

                # Extract tool name and arguments
                tool_call = tool_calls[0]
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                # Convert string args to dict if needed
                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)

                result["tool_called"] = tool_name
                result["tool_args"]   = tool_args

                # ── Step 4: Execute the tool ───────────────
                tool_fn     = TOOL_REGISTRY.get(tool_name)
                tool_output = tool_fn(**tool_args)
                result["tool_result"] = tool_output

                # ── Step 5: Send tool result back to OLLAMA ─
                messages.append({
                    "role":       "assistant",
                    "content":    "",
                    "tool_calls": tool_calls,
                })
                messages.append({
                    "role":    "tool",
                    "content": json.dumps(tool_output),
                    "name":    tool_name,
                })

                # ── Step 6: Get final human response ──────
                payload2 = {
                    "model":    self.model,
                    "messages": messages,
                    "stream":   False,
                    "options":  payload["options"],  # same LLM params
                }
                resp2      = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload2,
                    timeout=120,
                )
                resp2.raise_for_status()
                final_text = resp2.json()["message"]["content"]

            else:
                # No tool call — direct text answer
                final_text = message.get("content", "")

            result["response"] = final_text

            # ── Step 7: Update history if stateful ────────
            if self.stateful:
                self.history.append({
                    "role":    "user",
                    "content": user_message,
                })
                self.history.append({
                    "role":    "assistant",
                    "content": final_text,
                })

        except ValueError as e:
            result["error"]    = f"Tool Error: {str(e)}"
            result["response"] = f"Sorry, I couldn't process that: {str(e)}"
        except requests.RequestException as e:
            result["error"]    = f"API Error: {str(e)}"
            result["response"] = "Sorry, I'm having trouble connecting."
        except Exception as e:
            result["error"]    = f"Unexpected Error: {str(e)}"
            result["response"] = "An unexpected error occurred."

        result["latency_sec"] = round(time.time() - start, 3)
        return result


    # ─────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────
    def reset_history(self):
        """Clear conversation history."""
        self.history = []

    def get_history(self) -> list:
        """Return current conversation history."""
        return self.history

    def set_temperature(self, temp: float):
        """Override temperature at runtime."""
        if not 0.0 <= temp <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        self.temperature = temp

    def set_top_p(self, top_p: float):
        """Override top_p at runtime."""
        if not 0.0 <= top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")
        self.top_p = top_p

    def set_top_k(self, top_k: int):
        """Override top_k at runtime."""
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        self.top_k = top_k

    def disable_tools(self):
        """Disable tool calling."""
        self.tools_enabled = False

    def enable_tools(self):
        """Enable tool calling."""
        self.tools_enabled = True

    def ping(self) -> bool:
        """Check if OLLAMA server is reachable."""
        try:
            r = requests.get(self.base_url, timeout=5)
            return r.status_code == 200
        except Exception:
            return False