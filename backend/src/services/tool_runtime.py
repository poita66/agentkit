import asyncio

from backend.src.services.tool_registry import Tool, ToolRegistry


class ToolRuntime:
    def __init__(self, registry: ToolRegistry):
        self._registry = registry
        self._max_retries = 3

    async def execute(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool and return structured result.

        Returns:
        {
            "ok": bool,
            "data": dict | None,
            "error": {"code": str, "message": str, "recoverable": bool} | None
        }
        """
        tool = self._registry.get(tool_name)
        if tool is None:
            return {
                "ok": False,
                "data": None,
                "error": {"code": "TOOL_NOT_FOUND", "message": f"Tool '{tool_name}' not found", "recoverable": False},
            }

        result = await self._invoke_tool(tool, arguments)
        if result["ok"]:
            return result

        error = result.get("error", {})
        if error.get("recoverable", False):
            return await self._retry(tool_name, arguments, error)

        return result

    async def _invoke_tool(self, tool: Tool, arguments: dict) -> dict:
        """Invoke a tool. Default stub returns success, unless arguments contain err_* keywords."""
        await asyncio.sleep(0.5)
        for value in arguments.values():
            if isinstance(value, str):
                if "err_nonrecover" in value:
                    return {
                        "ok": False,
                        "data": None,
                        "error": {
                            "code": "INVALID_ARGUMENT",
                            "message": "Non-recoverable tool error",
                            "recoverable": False,
                        },
                    }
                if "err_recover" in value:
                    return {
                        "ok": False,
                        "data": None,
                        "error": {"code": "BAD_REQUEST", "message": "Bad request", "recoverable": True},
                    }
        return {"ok": True, "data": {"result": f"Executed {tool.name} with {arguments}"}, "error": None}

    async def _retry(self, tool_name: str, arguments: dict, original_error: dict) -> dict:
        """Retry a recoverable error with exponential backoff."""
        last_error = original_error
        for attempt in range(1, self._max_retries + 1):
            await asyncio.sleep(0.01 * (2**attempt))
            tool = self._registry.get(tool_name)
            if tool is None:
                return {
                    "ok": False,
                    "data": None,
                    "error": {
                        "code": "TOOL_NOT_FOUND",
                        "message": f"Tool '{tool_name}' not found",
                        "recoverable": False,
                    },
                }
            result = await self._invoke_tool(tool, arguments)
            if result["ok"]:
                return result
            last_error = result.get("error", last_error)

        if last_error.get("code") == "BAD_REQUEST":
            return {
                "ok": False,
                "data": None,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": last_error.get("message", "unknown"),
                    "recoverable": True,
                },
            }
        return {
            "ok": False,
            "data": None,
            "error": {
                "code": "RETRIES_EXHAUSTED",
                "message": f"All {self._max_retries} retries failed: {last_error.get('message', 'unknown')}",
                "recoverable": last_error.get("recoverable", False),
            },
        }
