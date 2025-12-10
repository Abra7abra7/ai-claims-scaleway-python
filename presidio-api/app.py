from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import yaml
import re
from typing import Dict, List, Optional
import os

app = FastAPI(title="Presidio Anonymization API")

# Global instances - CACHE pre analyzers (setri RAM a CPU)
analyzer_cache: Dict[str, AnalyzerEngine] = {}
anonymizer = None
config = None

# Mapovanie krajiny na jazyk
COUNTRY_LANGUAGE_MAP = {
    "SK": "xx",   # Multilingual (slovencina nie je v spaCy priamo)
    "IT": "it",   # Taliancina
    "DE": "de",   # Nemcina
    "EN": "en",   # Anglictina
}

# Mapovanie jazyka na spaCy model
LANGUAGE_MODEL_MAP = {
    "xx": "xx_ent_wiki_sm",   # Multilingual
    "it": "it_core_news_sm",
    "de": "de_core_news_sm",
    "en": "en_core_web_sm",
}

# Slova ktore indikuju ze meno je DOKTOR (nie pacient) - tieto NEanonymizujeme
DOCTOR_CONTEXT_WORDS = [
    r'\bMUDr\.?\s*',
    r'\bMDDr\.?\s*',
    r'\bMVDr\.?\s*',
    r'\bPhDr\.?\s*',
    r'\bJUDr\.?\s*',
    r'\bIng\.?\s*',
    r'\bMgr\.?\s*',
    r'\bDr\.?\s*',
    r'\bdoktor\s+',
    r'\bdoktorka\s+',
    r'\blekar\s+',
    r'\blekarka\s+',
    r'\bprimár\s+',
    r'\bprimarka\s+',
    r'\borderujuci\s+',
    r'\bosetrujuci\s+',
    r'\bvysetrujuci\s+',
]

# Slova ktore indikuju ze meno je PACIENT - tieto anonymizujeme
PATIENT_CONTEXT_WORDS = [
    r'\bpacient\s+',
    r'\bpacientka\s+',
    r'\bpoisteny\s+',
    r'\bpoistena\s+',
    r'\bpoistnik\s+',
    r'\bklient\s+',
    r'\bklientka\s+',
    r'\bmeno\s+a\s+priezvisko\s*:?\s*',
    r'\bmeno\s*:?\s*',
    r'\bpriezvisko\s*:?\s*',
    r'\btrvale\s+bydlisko\s*:?\s*',
    r'\badresa\s*:?\s*',
]


class AnonymizeRequest(BaseModel):
    text: str
    country: str
    language: Optional[str] = None  # Ak None, pouzije sa podla country


class AnonymizeResponse(BaseModel):
    anonymized_text: str
    entities_found: List[dict]


def load_config():
    """Load configuration from YAML file"""
    config_path = os.getenv("CONFIG_PATH", "/app/config/settings.yaml")
    if not os.path.exists(config_path):
        return {
            "presidio": {
                "score_threshold": 0.35,
                "countries": {
                    "SK": {"recognizers": {}},
                    "IT": {"recognizers": {}},
                    "DE": {"recognizers": {}}
                }
            }
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_recognizer(entity_name: str, pattern: str, score: float = 0.9, language: str = "xx") -> PatternRecognizer:
    """Create a custom pattern recognizer"""
    pattern_obj = Pattern(name=f"{entity_name}_pattern", regex=pattern, score=score)
    recognizer = PatternRecognizer(
        supported_entity=entity_name,
        patterns=[pattern_obj],
        supported_language=language
    )
    return recognizer


def is_doctor_name(text: str, start: int, end: int) -> bool:
    """Check if the detected name is likely a doctor (should NOT be anonymized)"""
    # Pozri 50 znakov pred menom
    context_before = text[max(0, start - 50):start].lower()
    
    for pattern in DOCTOR_CONTEXT_WORDS:
        if re.search(pattern, context_before, re.IGNORECASE):
            return True
    return False


def is_patient_name(text: str, start: int, end: int) -> bool:
    """Check if the detected name is likely a patient (SHOULD be anonymized)"""
    # Pozri 50 znakov pred menom
    context_before = text[max(0, start - 50):start].lower()
    
    for pattern in PATIENT_CONTEXT_WORDS:
        if re.search(pattern, context_before, re.IGNORECASE):
            return True
    return False


def get_analyzer(country: str, language: Optional[str] = None) -> AnalyzerEngine:
    """Get or create cached analyzer for country/language"""
    global analyzer_cache, config
    
    # Urcit jazyk
    if language is None:
        language = COUNTRY_LANGUAGE_MAP.get(country, "xx")
    
    cache_key = f"{country}_{language}"
    
    if cache_key in analyzer_cache:
        return analyzer_cache[cache_key]
    
    if config is None:
        config = load_config()
    
    # Vytvorit NLP engine s multilingvalnym modelom
    model_name = LANGUAGE_MODEL_MAP.get(language, "xx_ent_wiki_sm")
    
    # Konfiguracia pre NLP engine
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": language, "model_name": model_name}
        ]
    }
    
    try:
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        
        # Vytvorit AnalyzerEngine s custom NLP engine
        analyzer_engine = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=[language]
        )
    except Exception as e:
        print(f"Warning: Could not load model for {language}, falling back to xx: {e}")
        # Fallback na multilingual model
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "xx", "model_name": "xx_ent_wiki_sm"}
            ]
        }
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        analyzer_engine = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["xx"]
        )
        language = "xx"
    
    # Pridat country-specific recognizers
    presidio_config = config.get("presidio", {})
    countries = presidio_config.get("countries", {})
    country_config = countries.get(country, {})
    
    recognizers_config = country_config.get("recognizers", {})
    for entity_name, entity_config in recognizers_config.items():
        if isinstance(entity_config, dict):
            pattern = entity_config.get("pattern", "")
            score = entity_config.get("score", 0.9)
            if pattern:
                recognizer = create_recognizer(
                    entity_name.upper(),
                    pattern,
                    score,
                    language
                )
                analyzer_engine.registry.add_recognizer(recognizer)
    
    # Cache
    analyzer_cache[cache_key] = analyzer_engine
    print(f"Created and cached analyzer for {country} ({language})")
    return analyzer_engine


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup - preload common analyzers"""
    global anonymizer, config
    anonymizer = AnonymizerEngine()
    config = load_config()
    
    # Ziskaj score_threshold z configu
    presidio_config = config.get("presidio", {})
    score_threshold = presidio_config.get("score_threshold", 0.35)
    
    print("Presidio API starting up...")
    print(f"Supported countries: {list(COUNTRY_LANGUAGE_MAP.keys())}")
    print(f"Score threshold: {score_threshold}")
    
    # Preload analyzers for faster first request
    for country in ["SK", "IT", "DE"]:
        try:
            get_analyzer(country)
            print(f"Preloaded analyzer for {country}")
        except Exception as e:
            print(f"Warning: Could not preload analyzer for {country}: {e}")
    
    print("Presidio API ready!")


@app.get("/")
def read_root():
    presidio_config = config.get("presidio", {}) if config else {}
    return {
        "service": "Presidio Anonymization API",
        "status": "running",
        "supported_countries": list(COUNTRY_LANGUAGE_MAP.keys()),
        "cached_analyzers": list(analyzer_cache.keys()),
        "score_threshold": presidio_config.get("score_threshold", 0.35)
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cached_analyzers": len(analyzer_cache)
    }


@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize_text(request: AnonymizeRequest):
    """
    Anonymize text using Presidio with country-specific recognizers.
    Filters out doctor names but keeps patient names for anonymization.
    
    Args:
        request: AnonymizeRequest with text, country, and optional language
        
    Returns:
        AnonymizeResponse with anonymized text and found entities
    """
    try:
        # Urcit jazyk
        language = request.language or COUNTRY_LANGUAGE_MAP.get(request.country, "xx")
        
        # Pouzit cached analyzer
        country_analyzer = get_analyzer(request.country, language)
        
        # Ziskaj score_threshold z configu
        presidio_config = config.get("presidio", {}) if config else {}
        score_threshold = presidio_config.get("score_threshold", 0.35)
        
        # Analyze text s nizsim thresholdom
        results = country_analyzer.analyze(
            text=request.text,
            language=language,
            score_threshold=score_threshold
        )
        
        # Filtruj vysledky - odstran mena doktorov
        filtered_results = []
        for result in results:
            # Ak je to PERSON, skontroluj ci to nie je doktor
            if result.entity_type == "PERSON":
                if is_doctor_name(request.text, result.start, result.end):
                    print(f"Skipping doctor name: {request.text[result.start:result.end]}")
                    continue
            filtered_results.append(result)
        
        # Define operators for anonymization
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<OSOBA>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<TELEFON>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<ADRESA>"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "<DATUM>"}),
            "NRP": OperatorConfig("replace", {"new_value": "<NARODNOST>"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<KARTA>"}),
        }
        
        # Add country-specific operators
        if request.country == "SK":
            operators["RODNE_CISLO"] = OperatorConfig("replace", {"new_value": "<RODNE_CISLO>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
            operators["PSC"] = OperatorConfig("replace", {"new_value": "<PSC>"})
            operators["TELEFON_SK"] = OperatorConfig("replace", {"new_value": "<TELEFON>"})
            operators["CISLO_DOMU"] = OperatorConfig("replace", {"new_value": "<CISLO>"})
        elif request.country == "IT":
            operators["CODICE_FISCALE"] = OperatorConfig("replace", {"new_value": "<CODICE_FISCALE>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
        elif request.country == "DE":
            operators["STEUER_ID"] = OperatorConfig("replace", {"new_value": "<STEUER_ID>"})
            operators["IBAN"] = OperatorConfig("replace", {"new_value": "<IBAN>"})
        
        # Anonymize s filtrovanymi vysledkami
        anonymized_result = anonymizer.anonymize(
            text=request.text,
            analyzer_results=filtered_results,
            operators=operators
        )
        
        # Format entities found
        entities_found = [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": request.text[result.start:result.end]
            }
            for result in filtered_results
        ]
        
        return AnonymizeResponse(
            anonymized_text=anonymized_result.text,
            entities_found=entities_found
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")


@app.get("/countries")
def get_supported_countries():
    """Get list of supported countries and their languages"""
    presidio_config = config.get("presidio", {}) if config else {}
    return {
        "countries": COUNTRY_LANGUAGE_MAP,
        "cached_analyzers": list(analyzer_cache.keys()),
        "score_threshold": presidio_config.get("score_threshold", 0.35)
    }


@app.post("/test")
def test_anonymization():
    """Test endpoint with sample Slovak text"""
    test_text = """
    Pacient: Ján Novák
    Rodné číslo: 850615/1234
    Trvalé bydlisko: Hlavná 15, 851 01 Bratislava
    Telefón: +421 905 123 456
    IBAN: SK89 1100 0000 0012 3456 7890
    
    Ošetrujúci lekár: MUDr. Peter Horváth
    Diagnóza: J06.9 - Akútna infekcia horných dýchacích ciest
    """
    
    request = AnonymizeRequest(text=test_text, country="SK")
    return anonymize_text(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
