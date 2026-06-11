from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama Cloud via OpenAI-compatible API
    ollama_base_url: str = "https://ollama.com"
    ollama_api_key: str = ""
    ollama_model: str = "gemma4:31b-cloud"

    # Processing defaults
    max_chunk_tokens: int = 800
    min_chunk_tokens: int = 100

    # API
    host: str = "0.0.0.0"
    port: int = 8000

    # Mock mode — run the graph without real LLM calls
    mock_llm: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
