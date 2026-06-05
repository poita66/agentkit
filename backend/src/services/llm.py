import asyncio
import json
import random
from pathlib import Path


class MockLLM:
    """Deterministic mock LLM that reads responses from a scenario JSON file."""

    def __init__(self, scenario_path: str | Path):
        self._responses = self._load_scenario(scenario_path)
        self._index = 0

    @staticmethod
    def _load_scenario(path: str | Path) -> list[dict]:
        with open(Path(path)) as f:
            data = json.load(f)
        return data.get("responses", data) if isinstance(data, dict) else data

    async def call(self, goal: str, past_steps: list[dict], available_tools: list[dict]) -> dict:
        """Return the next response from the scenario.

        Simulates 1-2s LLM latency.

        Returns either:
        - {"type": "tool_call", "tool_name": ..., "arguments": ..., "cost": ...}
        - {"type": "final_answer", "answer": ..., "cost": ...}
        """
        await asyncio.sleep(random.uniform(1.0, 2.0))
        if self._index >= len(self._responses):
            return {"type": "final_answer", "answer": "No more scenario steps.", "cost": 0.0}

        response = self._responses[self._index]
        self._index += 1
        return response

    def reset(self):
        self._index = 0
