from backend.src.services.tool_registry import Tool, ToolRegistry


def test_retrieve_returns_top_k():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation for information", parameters={}))
    registry.register(Tool(name="search_web", description="Search the web for current information", parameters={}))
    registry.register(Tool(name="calculate", description="Perform mathematical calculations", parameters={}))

    tools = registry.retrieve("search for documentation", k=2)
    assert len(tools) == 2
    assert tools[0].name == "search_docs"


def test_retrieve_keyword_matching():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation", parameters={}))
    registry.register(Tool(name="send_email", description="Send email to recipient", parameters={}))

    tools = registry.retrieve("send an email", k=5)
    assert tools[0].name == "send_email"


def test_retrieve_empty_goal():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation", parameters={}))
    tools = registry.retrieve("", k=5)
    assert len(tools) == 0


def test_retrieve_k_larger_than_registry():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation", parameters={}))
    registry.register(Tool(name="calculate", description="Perform calculations", parameters={}))
    tools = registry.retrieve("search calculate", k=10)
    assert len(tools) == 2


def test_retrieve_no_overlap():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation", parameters={}))
    tools = registry.retrieve("xyz abc qrs", k=5)
    assert len(tools) == 1
    assert tools[0].name == "search_docs"


def test_retrieve_score_ordering():
    registry = ToolRegistry()
    registry.register(Tool(name="search_docs", description="Search documentation and knowledge base", parameters={}))
    registry.register(Tool(name="search_web", description="Search the web for current information", parameters={}))
    registry.register(Tool(name="calculate", description="Perform mathematical calculations", parameters={}))

    tools = registry.retrieve("search documentation knowledge", k=5)
    assert tools[0].name == "search_docs"
    assert tools[1].name == "search_web"
