from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import yaml
from typing import Dict, List, Optional
import os

app = FastAPI(title="Presidio Anonymization API")

# Global instances
analyzer = None
anonymizer = None
config = None


class AnonymizeRequest(BaseModel):
    text: str
    country: str
    language: str = "en"


class AnonymizeResponse(BaseModel):
    anonymized_text: str
    entities_found: List[dict]


def load_config():
    """Load configuration from YAML file"""
    config_path = os.getenv("CONFIG_PATH", "/app/config/settings.yaml")
    if not os.path.exists(config_path):
        # Return default config if file doesn't exist
        return {
            "presidio": {
                "countries": {
                    "SK": {"recognizers": {}},
                    "IT": {"recognizers": {}},
                    "DE": {"recognizers": {}}
                }
            }
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_recognizer(entity_name: str, pattern: str, score: float = 0.9) -> PatternRecognizer:
    """Create a custom pattern recognizer"""
    pattern_obj = Pattern(name=f"{entity_name}_pattern", regex=pattern, score=score)
    return PatternRecognizer(
        supported_entity=entity_name,
        patterns=[pattern_obj]
    )


def initialize_analyzer(country: str):
    """Initialize analyzer with country-specific recognizers"""
    global analyzer, config
    
    if config is None:
        config = load_config()
    
    analyzer_engine = AnalyzerEngine()
    
    # Get country configuration
    presidio_config = config.get("presidio", {})
    countries = presidio_config.get("countries", {})
    country_config = countries.get(country, {})
    
    # Add country-specific recognizers
    recognizers_config = country_config.get("recognizers", {})
    for entity_name, entity_config in recognizers_config.items():
        if isinstance(entity_config, dict):
            pattern = entity_config.get("pattern", "")
            score = entity_config.get("score", 0.9)
            if pattern:
                recognizer = create_recognizer(
                    entity_name.upper(),
                    pattern,
                    score
                )
                analyzer_engine.registry.add_recognizer(recognizer)
    
    return analyzer_engine


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global anonymizer, config
    anonymizer = AnonymizerEngine()
    config = load_config()


@app.get("/")
def read_root():
    return {"service": "Presidio Anonymization API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(request: AnonymizeRequest):
    """
    Anonymize text using Presidio with country-specific recognizers.
    
    Args:
        request: AnonymizeRequest with text, country, and language
        
    Returns:
        AnonymizeResponse with anonymized text and found entities
    """
    try:
        # Initialize analyzer with country-specific recognizers
        country_analyzer = initialize_analyzer(request.country)
        
        # Analyze text
        results = country_analyzer.analyze(
            text=request.text,
            language=request.language
        )
        
        # Define operators for anonymization
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<OSOBA>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<TELEFON>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
        }
        
        # Add country-specific operators
        if request.country == "SK":
            operators["RODNE_CISLO"] = OperatorConfig("replace", {"new_value": "<RODNE_CISLO>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
        elif request.country == "IT":
            operators["CODICE_FISCALE"] = OperatorConfig("replace", {"new_value": "<CODICE_FISCALE>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
        elif request.country == "DE":
            operators["STEUER_ID"] = OperatorConfig("replace", {"new_value": "<STEUER_ID>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
        
        # Anonymize
        anonymized_result = anonymizer.anonymize(
            text=request.text,
            analyzer_results=results,
            operators=operators
        )
        
        # Format entities found
        entities_found = [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score
            }
            for result in results
        ]
        
        return AnonymizeResponse(
            anonymized_text=anonymized_result.text,
            entities_found=entities_found
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")


@app.get("/countries")
def get_supported_countries():
    """Get list of supported countries"""
    global config
    if config is None:
        config = load_config()
    
    presidio_config = config.get("presidio", {})
    countries = presidio_config.get("countries", {})
    
    return {
        "countries": list(countries.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

