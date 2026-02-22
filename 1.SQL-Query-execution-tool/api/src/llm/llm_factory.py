from typing import Any
from src.config.settings import get_settings
from src.log import get_logger

logger = get_logger(__name__)
settings = get_settings()


def get_llm(**overrides: Any):
    provider = (overrides.pop("provider", None) or settings.llm_provider).lower()
    logger.info("Loading LLM | provider=%s model=%s", provider, settings.llm_model)

    match provider:

        case "openai":
            from langchain_openai import ChatOpenAI  # type: ignore
            kwargs: dict[str, Any] = {
                "model":       settings.llm_model,
                "api_key":     settings.llm_api_key,
                "max_tokens":  settings.llm_max_tokens,
                "temperature": settings.llm_temperature,
            }
            if settings.llm_base_url:
                kwargs["base_url"] = settings.llm_base_url.rstrip("/")
            kwargs.update(overrides)
            return ChatOpenAI(**kwargs)

        case "azure":
            from langchain_openai import AzureChatOpenAI  # type: ignore
            kwargs = {
                "azure_deployment": settings.llm_model,
                "api_key":          settings.llm_api_key,
                "max_tokens":       settings.llm_max_tokens,
                "temperature":      settings.llm_temperature,
            }
            if settings.llm_base_url:
                kwargs["azure_endpoint"] = settings.llm_base_url.rstrip("/")
            kwargs.update(overrides)
            return AzureChatOpenAI(**kwargs)

        case "anthropic":
            from langchain_anthropic import ChatAnthropic  # type: ignore
            kwargs = {
                "model":       settings.llm_model,
                "api_key":     settings.llm_api_key,
                "max_tokens":  settings.llm_max_tokens,
                "temperature": settings.llm_temperature,
            }
            kwargs.update(overrides)
            return ChatAnthropic(**kwargs)

        case "google":
            from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
            kwargs = {
                "model":       settings.llm_model,
                "google_api_key": settings.llm_api_key,
                "max_output_tokens": settings.llm_max_tokens,
                "temperature": settings.llm_temperature,
            }
            kwargs.update(overrides)
            return ChatGoogleGenerativeAI(**kwargs)

        case "ollama":
            from langchain_ollama import ChatOllama  # type: ignore
            kwargs = {
                "model":       settings.llm_model,
                "temperature": settings.llm_temperature,
            }
            if settings.llm_base_url:
                kwargs["base_url"] = settings.llm_base_url.rstrip("/")
            kwargs.update(overrides)
            return ChatOllama(**kwargs)

        case _:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{provider}'. "
                "Supported values: openai | azure | anthropic | google | ollama"
            )
