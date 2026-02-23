from unittest.mock import MagicMock, patch

from src.llm.model_switch import (
    build_dynamic_model_switch_middleware,
    should_use_advanced_model,
)
from langchain.agents.middleware import ModelRequest


def test_should_use_advanced_model_threshold() -> None:
    assert should_use_advanced_model(13, 12) is True
    assert should_use_advanced_model(12, 12) is False
    assert should_use_advanced_model(3, 12) is False


def test_dynamic_model_switch_selects_lightweight_for_short_conversation() -> None:
    settings = MagicMock()
    settings.llm_lightweight_model = "light"
    settings.llm_advanced_model = "heavy"
    settings.model_switch_message_threshold = 4

    light = MagicMock(name="light")
    heavy = MagicMock(name="heavy")

    with patch("src.llm.model_switch.get_llm", side_effect=[light, heavy]):
        middleware = build_dynamic_model_switch_middleware(settings)

    base_model = MagicMock(name="base")
    req = ModelRequest(
        model=base_model,
        messages=[MagicMock(), MagicMock()],
        tools=[],
    )
    captured = {}

    def handler(new_req):
        captured["model"] = new_req.model
        return MagicMock()

    middleware.wrap_model_call(req, handler)
    assert captured["model"] is light


def test_dynamic_model_switch_selects_advanced_for_long_conversation() -> None:
    settings = MagicMock()
    settings.llm_lightweight_model = "light"
    settings.llm_advanced_model = "heavy"
    settings.model_switch_message_threshold = 2

    light = MagicMock(name="light")
    heavy = MagicMock(name="heavy")

    with patch("src.llm.model_switch.get_llm", side_effect=[light, heavy]):
        middleware = build_dynamic_model_switch_middleware(settings)

    base_model = MagicMock(name="base")
    req = ModelRequest(
        model=base_model,
        messages=[MagicMock(), MagicMock(), MagicMock()],
        tools=[],
    )
    captured = {}

    def handler(new_req):
        captured["model"] = new_req.model
        return MagicMock()

    middleware.wrap_model_call(req, handler)
    assert captured["model"] is heavy
