# Predefined prompts for claim analysis

PROMPTS = {
    "default": {
        "name": "Štandardná analýza",
        "description": "Základná analýza poistnej udalosti",
        "template": """You are an expert insurance claim adjuster. Your task is to analyze the following claim based on the provided policy documents.

POLICY DOCUMENTS:
{context}

CLAIM DETAILS:
{claim_text}

Analyze the claim and provide a JSON output with the following fields:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: A score between 0.0 and 1.0
- reasoning: A detailed explanation of your decision citing specific parts of the policy.
- missing_info: List of any missing information if applicable.

Return ONLY the JSON."""
    },
    
    "detailed_medical": {
        "name": "Detailná zdravotná analýza",
        "description": "Podrobná analýza zdravotných nárokov s dôrazom na diagnózy a liečbu",
        "template": """You are a medical insurance claim specialist. Analyze the following medical claim with focus on:
- Diagnosis codes (ICD-10)
- Treatment procedures
- Medical necessity
- Policy coverage

POLICY DOCUMENTS:
{context}

CLAIM DETAILS:
{claim_text}

Provide a JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: Score 0.0-1.0
- reasoning: Detailed medical justification
- missing_info: List of missing medical documentation
- medical_codes_found: List of ICD-10 or procedure codes identified
- treatment_appropriateness: Assessment of treatment plan

Return ONLY the JSON."""
    },
    
    "fraud_detection": {
        "name": "Detekcia podvodov",
        "description": "Analýza zameraná na identifikáciu podozrivých prvkov",
        "template": """You are a fraud detection specialist for insurance claims. Analyze the claim for potential red flags:

POLICY DOCUMENTS:
{context}

CLAIM DETAILS:
{claim_text}

Look for:
- Inconsistencies in the narrative
- Unusual timing or patterns
- Missing or suspicious documentation
- Exaggerated claims

Provide a JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: Score 0.0-1.0
- reasoning: Explanation of findings
- fraud_risk_score: Score 0.0-1.0 indicating fraud likelihood
- red_flags: List of suspicious elements found
- missing_info: Required additional documentation

Return ONLY the JSON."""
    },
    
    "quick_review": {
        "name": "Rýchle posúdenie",
        "description": "Zjednodušená rýchla analýza pre jednoduché prípady",
        "template": """Quick insurance claim review. Provide concise assessment.

CLAIM:
{claim_text}

POLICY:
{context}

JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: 0.0-1.0
- reasoning: Brief explanation (max 2 sentences)

Return ONLY the JSON."""
    },
    
    "slovak_language": {
        "name": "Slovenská analýza",
        "description": "Analýza v slovenskom jazyku",
        "template": """Si expert na poistné nároky. Analyzuj nasledujúci nárok.

DOKUMENTY POISTKY:
{context}

DETAILY NÁROKU:
{claim_text}

Poskytni JSON výstup s:
- recommendation: "APPROVE", "REJECT", alebo "INVESTIGATE"
- confidence: Skóre 0.0-1.0
- reasoning: Podrobné vysvetlenie rozhodnutia v slovenčine
- missing_info: Zoznam chýbajúcich informácií

Vráť IBA JSON."""
    }
}

def get_prompt_list():
    """Returns list of available prompts with metadata"""
    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"]
        }
        for key, value in PROMPTS.items()
    ]

def get_prompt_template(prompt_id: str) -> str:
    """Returns the template for a specific prompt ID"""
    if prompt_id in PROMPTS:
        return PROMPTS[prompt_id]["template"]
    return PROMPTS["default"]["template"]
