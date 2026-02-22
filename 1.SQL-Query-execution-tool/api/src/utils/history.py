"""Chat history and message formatting utilities."""

from src.cache.redis_client import get_session_history, set_session_history

async def build_chat_messages(session_id: str, query: str) -> list[dict]:
    """Fetch session history from Redis and format it with the new user query."""
    history = await get_session_history(session_id) or []
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if isinstance(m.get("role"), str) and isinstance(m.get("content"), str)
    ]
    messages.append({"role": "user", "content": query})
    return messages

async def save_chat_response(session_id: str, messages: list[dict], full_response: str) -> None:
    """Append the final assistant response and save the tail to Redis."""
    new_history = messages + [{"role": "assistant", "content": full_response}]
    await set_session_history(session_id, new_history[-20:])
