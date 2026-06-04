import re
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def retrieve(self, goal: str, k: int = 5) -> list[Tool]:
        """Score tools by keyword overlap with goal text and return top-K."""
        goal_tokens = set(re.findall(r"\w+", goal.lower()))
        if not goal_tokens:
            return []

        scored: list[tuple[float, Tool]] = []
        for tool in self._tools.values():
            text = (tool.name + " " + tool.description).lower()
            text_tokens = set(re.findall(r"\w+", text))
            overlap = len(goal_tokens & text_tokens)
            score = overlap / len(goal_tokens) if goal_tokens else 0.0
            scored.append((score, tool))

        scored.sort(key=lambda x: (-x[0], x[1].name))
        return [tool for _, tool in scored[:k]]


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="search_docs",
            description="Search documentation and knowledge base for relevant information",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        )
    )
    registry.register(
        Tool(
            name="search_web",
            description="Search the web for current information and news",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        )
    )
    registry.register(
        Tool(
            name="read_file",
            description="Read the contents of a file from the filesystem",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        )
    )
    registry.register(
        Tool(
            name="write_file",
            description="Write content to a file on the filesystem",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        )
    )
    registry.register(
        Tool(
            name="calculate",
            description="Perform mathematical calculations and computations",
            parameters={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
        )
    )
    registry.register(
        Tool(
            name="summarize",
            description="Summarize text content into key points",
            parameters={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        )
    )
    registry.register(
        Tool(
            name="translate",
            description="Translate text between languages",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}, "target_language": {"type": "string"}},
                "required": ["text", "target_language"],
            },
        )
    )
    registry.register(
        Tool(
            name="query_database",
            description="Query a database for structured data",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        )
    )
    registry.register(
        Tool(
            name="send_email",
            description="Send an email message to a recipient",
            parameters={
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"],
            },
        )
    )
    registry.register(
        Tool(
            name="list_files",
            description="List files and directories in a given path",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        )
    )
    return registry
