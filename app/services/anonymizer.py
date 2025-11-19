from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class AnonymizerService:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self._add_custom_recognizers()

    def _add_custom_recognizers(self):
        # Slovak Birth Number (Rodné číslo)
        # Format: YYMMDD/XXXX or YYMMDDXXXX
        rc_pattern = Pattern(name="slovak_rc_pattern", regex=r"\b\d{6}[/]?\d{3,4}\b", score=0.9)
        rc_recognizer = PatternRecognizer(supported_entity="SK_RODNE_CISLO", patterns=[rc_pattern])
        self.analyzer.registry.add_recognizer(rc_recognizer)

        # Slovak IBAN
        iban_pattern = Pattern(name="slovak_iban_pattern", regex=r"\bSK\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}\b", score=1.0)
        iban_recognizer = PatternRecognizer(supported_entity="SK_IBAN", patterns=[iban_pattern])
        self.analyzer.registry.add_recognizer(iban_recognizer)

    def anonymize(self, text: str) -> str:
        if not text:
            return ""
            
        # Analyze
        results = self.analyzer.analyze(text=text, language='en') # Presidio default model is English, works okay for general entities
        
        # Anonymize
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "SK_RODNE_CISLO": OperatorConfig("replace", {"new_value": "<RODNE_CISLO>"}),
                "SK_IBAN": OperatorConfig("replace", {"new_value": "<IBAN>"}),
                "PERSON": OperatorConfig("replace", {"new_value": "<OSOBA>"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<TELEFON>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"})
            }
        )
        
        return anonymized_result.text
