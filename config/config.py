"""
Configuration Management
Loads settings from config.yaml and .env
"""
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings


# Load environment variables
load_dotenv()


class AppConfig(BaseSettings):
    """Application configuration from environment and YAML"""
    
    # OpenAI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Database
    database_url: str = Field(default="sqlite:///data/db/plc_data.db", env="DATABASE_URL")
    
    # RAG
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_dir: str = "data/vector_store"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 3
    
    # PLC Simulation
    plc_update_interval_ms: int = 500
    enable_simulation: bool = True
    
    # GUI
    window_width: int = 1400
    window_height: int = 900
    theme: str = "light"
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env


def load_yaml_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def merge_configs() -> AppConfig:
    """Merge YAML and environment configurations"""
    yaml_config = load_yaml_config()
    config = AppConfig()
    
    # Override with YAML values if present
    if "openai" in yaml_config:
        config.openai_model = yaml_config["openai"].get("model", config.openai_model)
        config.openai_temperature = yaml_config["openai"].get("temperature", config.openai_temperature)
        config.openai_max_tokens = yaml_config["openai"].get("max_tokens", config.openai_max_tokens)
    
    if "rag" in yaml_config:
        config.embedding_model = yaml_config["rag"].get("embedding_model", config.embedding_model)
        config.chunk_size = yaml_config["rag"].get("chunk_size", config.chunk_size)
        config.chunk_overlap = yaml_config["rag"].get("chunk_overlap", config.chunk_overlap)
        config.top_k_results = yaml_config["rag"].get("top_k_results", config.top_k_results)
        config.vector_store_dir = yaml_config["rag"].get("vector_store_dir", config.vector_store_dir)
    
    if "plc" in yaml_config:
        config.plc_update_interval_ms = yaml_config["plc"].get("update_interval_ms", config.plc_update_interval_ms)
        config.enable_simulation = yaml_config["plc"].get("enable_simulation", config.enable_simulation)
    
    if "gui" in yaml_config:
        config.window_width = yaml_config["gui"].get("window_width", config.window_width)
        config.window_height = yaml_config["gui"].get("window_height", config.window_height)
        config.theme = yaml_config["gui"].get("theme", config.theme)
    
    return config


# Global configuration instance
settings = merge_configs()
