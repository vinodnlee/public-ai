import sys
import os

# Add src to path
sys.path.append(os.path.abspath("."))

from src.agent.deepagent_builder import build_supervisor_graph
from src.db.adapters.factory import get_adapter
from src.semantic.layer import SemanticLayer
from src.agent.events import AgentEvent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables.base import RunnableBinding
from langchain_core.tools import BaseTool

from src.tools.get_schema_context import get_schema_context_tool
print(f"DEBUG: get_schema_context_tool type: {type(get_schema_context_tool)}")
print(f"DEBUG: has func attr: {hasattr(get_schema_context_tool, 'func')} value: {get_schema_context_tool.func}")
print(f"DEBUG: has coroutine attr: {hasattr(get_schema_context_tool, 'coroutine')} value: {get_schema_context_tool.coroutine}")

from langchain_core.runnables import RunnableBinding

def check_for_runnable_binding(obj, path="root"):
    if isinstance(obj, RunnableBinding):
        print(f"!!! FOUND RunnableBinding at {path}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_for_runnable_binding(item, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_for_runnable_binding(v, f"{path}.{k}")

async def debug_tools():
    print("Testing tool types...")
    adapter = get_adapter()
    semantic_layer = SemanticLayer(adapter)
    captured_events = []
    checkpointer = InMemorySaver()
    
    # Check dependencies
    print("Checking dependencies for RunnableBinding...")
    check_for_runnable_binding(adapter, "adapter")
    check_for_runnable_binding(semantic_layer, "semantic_layer")
    
    agent = build_supervisor_graph(
        adapter,
        semantic_layer,
        captured_events,
        checkpointer
    )
    print("Agent built successfully!")
    
    # Try to find the tool in the graph's tool node
    try:
        tool_node = agent.get_node("tools")
        wrapper_tool = tool_node.tools_by_name.get("get_schema_context")
        print(f"DEBUG: wrapper_tool type: {type(wrapper_tool)}")
        print(f"DEBUG: wrapper_tool name: {wrapper_tool.name}")
    except Exception as e:
        print(f"DEBUG: Could not inspect tools: {e}")
    
    print("Running agent...")
    try:
        inputs = {"messages": [{"role": "user", "content": "show me the tables"}]}
        config = {"configurable": {"thread_id": "debug"}}
        async for event in agent.astream_events(inputs, config=config, version="v2"):
            # print(event["event"])
            pass
        print("Agent ran successfully!")
    except Exception as e:
        print(f"Agent run FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_tools())
