import yaml
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List


class ConfigLoader:
    """Loader for YAML configuration files"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self._config is None:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        
        return self._config
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        config = self.load()
        return config.get('llm', {})
    
    def get_presidio_config(self) -> Dict[str, Any]:
        """Get Presidio configuration"""
        config = self.load()
        return config.get('presidio', {})
    
    def get_country_config(self, country: str) -> Dict[str, Any]:
        """Get country-specific Presidio configuration"""
        presidio_config = self.get_presidio_config()
        countries = presidio_config.get('countries', {})
        return countries.get(country, {})
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration"""
        config = self.load()
        return config.get('rag', {})
    
    def get_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Get all prompt templates"""
        config = self.load()
        return config.get('prompts', {})
    
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Get specific prompt template by ID"""
        prompts = self.get_prompts()
        if prompt_id not in prompts:
            raise ValueError(f"Prompt ID '{prompt_id}' not found in configuration")
        return prompts[prompt_id]
    
    def get_prompt_list(self) -> List[Dict[str, str]]:
        """Get list of available prompts with metadata"""
        prompts = self.get_prompts()
        return [
            {
                "id": key,
                "name": value.get("name", key),
                "description": value.get("description", "")
            }
            for key, value in prompts.items()
        ]
    
    def reload(self):
        """Force reload configuration from file"""
        self._config = None
        return self.load()


@lru_cache()
def get_config_loader() -> ConfigLoader:
    """Get cached configuration loader instance"""
    return ConfigLoader()

