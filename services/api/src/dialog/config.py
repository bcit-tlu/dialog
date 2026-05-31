from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_base_url: str = "https://ollama.com"
    ollama_api_key: str = ""
    ollama_model: str = "gemma4:31b-cloud"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 4

    @property
    def client_kwargs(self) -> dict:
        if self.ollama_api_key:
            return {"headers": {"Authorization": f"Bearer {self.ollama_api_key}"}}
        return {}


settings = Settings()
