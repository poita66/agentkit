import pytest
from unittest.mock import patch, MagicMock

from backend.src.services.tool_registry import ToolRegistry, Tool
from backend.src.services.tool_runtime import ToolRuntime


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(Tool(name="search_docs", description="Search docs", parameters={}))
    reg.register(Tool(name="calculate", description="Calculate", parameters={}))
    return reg


@pytest.fixture
def runtime(registry):
    return ToolRuntime(registry)


@pytest.mark.asyncio
async def test_dispatch_success(runtime):
    result = await runtime.execute("search_docs", {"query": "test"})
    assert result["ok"] is True
    assert result["error"] is None
    assert result["data"] is not None


@pytest.mark.asyncio
async def test_dispatch_tool_not_found(runtime):
    result = await runtime.execute("nonexistent", {"query": "test"})
    assert result["ok"] is False
    assert result["error"] is not None
    assert result["error"]["code"] == "TOOL_NOT_FOUND"
    assert result["error"]["recoverable"] is False


@pytest.mark.asyncio
async def test_recoverable_error_retry_succeeds(registry):
    rt = ToolRuntime(registry)
    call_count = 0

    def mock_invoke(tool, args):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return {
                "ok": False,
                "data": None,
                "error": {"code": "NETWORK_TIMEOUT", "message": "Timeout", "recoverable": True},
            }
        return {"ok": True, "data": {"result": "success"}, "error": None}

    with patch.object(rt, "_invoke_tool", mock_invoke):
        result = await rt.execute("search_docs", {"query": "test"})
    assert result["ok"] is True
    assert call_count == 3


@pytest.mark.asyncio
async def test_recoverable_error_all_retries_fail(registry):
    rt = ToolRuntime(registry)

    def mock_invoke(tool, args):
        return {
            "ok": False,
            "data": None,
            "error": {"code": "NETWORK_TIMEOUT", "message": "Timeout", "recoverable": True},
        }

    with patch.object(rt, "_invoke_tool", mock_invoke):
        result = await rt.execute("search_docs", {"query": "test"})
    assert result["ok"] is False
    assert result["error"]["code"] == "RETRIES_EXHAUSTED"
    assert result["error"]["recoverable"] is False


@pytest.mark.asyncio
async def test_non_recoverable_error_no_retry(registry):
    rt = ToolRuntime(registry)

    def mock_invoke(tool, args):
        return {
            "ok": False,
            "data": None,
            "error": {"code": "INVALID_ARGUMENT", "message": "Bad arg", "recoverable": False},
        }

    with patch.object(rt, "_invoke_tool", mock_invoke):
        result = await rt.execute("search_docs", {"query": "test"})
    assert result["ok"] is False
    assert result["error"]["code"] == "INVALID_ARGUMENT"
    assert result["error"]["recoverable"] is False
