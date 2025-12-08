from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import yaml
from typing import Dict, List, Optional
import os
import re

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
    
    # Add country-specific recognizers from config
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
    
    # Add Slovak-specific recognizers for SK country
    if country == "SK":
        # Slovak names with titles (MUDr., Ing., etc.)
        sk_titled_name_pattern = Pattern(
            name="sk_titled_name",
            regex=r'\b(MUDr\.|Ing\.|Mgr\.|JUDr\.|PhDr\.|RNDr\.|doc\.|prof\.|PaedDr\.|ThDr\.|MVDr\.|RSDr\.)\s*[A-ZÁČĎÉÍĽŇÓŔŠŤÚÝŽ][a-záčďéíľňóŕšťúýž]+\s+[A-ZÁČĎÉÍĽŇÓŔŠŤÚÝŽ][a-záčďéíľňóŕšťúýž]+',
            score=0.95
        )
        sk_titled_recognizer = PatternRecognizer(
            supported_entity="SK_PERSON",
            patterns=[sk_titled_name_pattern]
        )
        analyzer_engine.registry.add_recognizer(sk_titled_recognizer)
        
        # Slovak IBAN (SK followed by 22 digits, with or without spaces)
        sk_iban_pattern = Pattern(
            name="sk_iban",
            regex=r'\bSK\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{0,4}\b',
            score=0.98
        )
        sk_iban_recognizer = PatternRecognizer(
            supported_entity="SK_IBAN",
            patterns=[sk_iban_pattern]
        )
        analyzer_engine.registry.add_recognizer(sk_iban_recognizer)
        
        # Slovak phone numbers
        sk_phone_pattern = Pattern(
            name="sk_phone",
            regex=r'\b(\+421|0)[\s]?[0-9]{3}[\s/]?[0-9]{3}[\s]?[0-9]{3}\b',
            score=0.9
        )
        sk_phone_recognizer = PatternRecognizer(
            supported_entity="SK_PHONE",
            patterns=[sk_phone_pattern]
        )
        analyzer_engine.registry.add_recognizer(sk_phone_recognizer)
        
        # Slovak rodné číslo (birth number)
        sk_rodne_cislo_pattern = Pattern(
            name="sk_rodne_cislo",
            regex=r'\b\d{6}[/]?\d{3,4}\b',
            score=0.95
        )
        sk_rodne_cislo_recognizer = PatternRecognizer(
            supported_entity="RODNE_CISLO",
            patterns=[sk_rodne_cislo_pattern]
        )
        analyzer_engine.registry.add_recognizer(sk_rodne_cislo_recognizer)
    
    return analyzer_engine


def get_entities_for_country(country: str) -> Optional[List[str]]:
    """
    Get list of entities to detect for a specific country.
    For non-English countries, we disable English NER (PERSON detection)
    and use only regex-based patterns.
    """
    if country == "SK":
        # For Slovak - use ONLY specific regex-based entities
        # Strict list to minimize false positives
        return [
            "RODNE_CISLO",      # Slovak birth number (regex)
            "SK_IBAN",          # Slovak IBAN (regex)
            "SK_PERSON",        # Slovak names with titles (regex)
            "SK_PHONE",         # Slovak phone numbers (regex)
            "EMAIL_ADDRESS",    # Email (works universally)
            # Note: PHONE_NUMBER and IBAN removed - too many false positives
        ]
    elif country == "IT":
        return [
            "CODICE_FISCALE",
            "IBAN",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "CREDIT_CARD",
            "IP_ADDRESS",
        ]
    elif country == "DE":
        return [
            "STEUER_ID",
            "IBAN",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "CREDIT_CARD",
            "IP_ADDRESS",
        ]
    
    # For other countries, use all entities including English NER
    return None


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
    
    For Slovak (SK) documents:
    - Uses ONLY regex-based detection (no English NER)
    - Detects: rodné číslo, IBAN, phone, email, names with titles
    - Avoids false positives like "Poistenec" -> <OSOBA>
    """
    try:
        # Initialize analyzer with country-specific recognizers
        country_analyzer = initialize_analyzer(request.country)
        
        # Get entities to analyze for this country
        # For SK, we limit to regex-only entities to avoid English NER false positives
        entities_to_analyze = get_entities_for_country(request.country)
        
        # Analyze text
        results = country_analyzer.analyze(
            text=request.text,
            language=request.language,
            entities=entities_to_analyze
        )
        
        # Filter results to only include allowed entities for this country
        # This prevents Presidio from detecting entities we didn't ask for
        if entities_to_analyze:
            results = [r for r in results if r.entity_type in entities_to_analyze]
        
        # Define operators for anonymization - only for allowed entities
        # No DEFAULT operator to prevent unwanted anonymization
        operators = {}
        
        # Add country-specific operators ONLY for entities we want to detect
        if request.country == "SK":
            operators = {
                "RODNE_CISLO": OperatorConfig("replace", {"new_value": "<RODNE_CISLO>"}),
                "SK_IBAN": OperatorConfig("replace", {"new_value": "<IBAN>"}),
                "SK_PERSON": OperatorConfig("replace", {"new_value": "<OSOBA>"}),
                "SK_PHONE": OperatorConfig("replace", {"new_value": "<TELEFON>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            }
        elif request.country == "IT":
            operators = {
                "CODICE_FISCALE": OperatorConfig("replace", {"new_value": "<CODICE_FISCALE>"}),
                "IBAN": OperatorConfig("replace", {"new_value": "<IBAN>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            }
        elif request.country == "DE":
            operators = {
                "STEUER_ID": OperatorConfig("replace", {"new_value": "<STEUER_ID>"}),
                "IBAN": OperatorConfig("replace", {"new_value": "<IBAN>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            }
        else:
            # Default operators for other countries
            operators = {
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            }
        
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
