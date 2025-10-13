"""Configuration management for LiuAgent."""
import os
import toml
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pathlib import Path


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["*"]


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    api_version: Optional[str] = None
    deployment_name: Optional[str] = None


class KnowledgeBaseConfig(BaseModel):
    vector_db_path: str = "./data/chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"
    max_results: int = 5


class SearchConfig(BaseModel):
    primary_engine: str = "duckduckgo"
    fallback_engines: List[str] = ["google", "bing"]
    max_results: int = 10
    timeout: int = 10
    language: str = "zh-CN"
    region: str = "cn"


class GoogleSearchConfig(BaseModel):
    api_key: str = ""
    search_engine_id: str = ""


class UploadConfig(BaseModel):
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = [".pdf", ".docx", ".txt"]
    upload_path: str = "./uploads"


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///./data/liuagent.db"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file_path: str = "./logs/liuagent.log"
    max_file_size: str = "10MB"
    backup_count: int = 5


class Config(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    knowledge_base: KnowledgeBaseConfig = Field(default_factory=KnowledgeBaseConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    upload: UploadConfig = Field(default_factory=UploadConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Alternative LLM configurations
    llm_configs: Dict[str, LLMConfig] = Field(default_factory=dict)
    google_search: GoogleSearchConfig = Field(default_factory=GoogleSearchConfig)


def load_config(config_path: str = "config/config.toml") -> Config:
    """Load configuration from TOML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Try to copy from example
        example_file = Path("config/config.example.toml")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, config_file)
            print(f"Created {config_path} from example. Please update with your API keys.")
        else:
            # Create default config
            config = Config()
            save_config(config, config_path)
            print(f"Created default {config_path}. Please update with your API keys.")
            return config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        # Handle alternative LLM configurations
        llm_configs = {}
        if 'llm' in data:
            for key, value in data['llm'].items():
                if isinstance(value, dict) and 'provider' in value:
                    llm_configs[key] = LLMConfig(**value)
        
        # Remove nested LLM configs from main data
        if 'llm' in data:
            main_llm = {k: v for k, v in data['llm'].items() if not isinstance(v, dict)}
            data['llm'] = main_llm
        
        config = Config(**data)
        config.llm_configs = llm_configs
        
        # Handle Google search config
        if 'search' in data and 'google' in data['search']:
            config.google_search = GoogleSearchConfig(**data['search']['google'])
        
        return config
        
    except Exception as e:
        print(f"Error loading config: {e}")
        return Config()


def save_config(config: Config, config_path: str = "config/config.toml") -> None:
    """Save configuration to TOML file."""
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict for TOML serialization
    data = config.model_dump()
    
    with open(config_file, 'w', encoding='utf-8') as f:
        toml.dump(data, f)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Config:
    """Reload configuration from file."""
    global _config
    _config = load_config()
    return _config
