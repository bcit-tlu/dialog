from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    subject_domain: str = "computer science"
    max_questions_per_session: int = 10
    initial_difficulty: int = 3  # 1-5 scale
    materials_dir: str = "materials"

    class Config:
        env_file = ".env"
        env_prefix = "ASSESS_"


settings = Settings()
