"""
Predefined prompts for claim analysis.
Each prompt can specify a preferred model.

Available Models:
- Mistral: mistral-small-latest, mistral-large-latest
- Gemini: gemini-2.0-flash, gemini-1.5-pro
"""

PROMPTS = {
    "default": {
        "name": "Štandardná analýza",
        "description": "Základná analýza poistnej udalosti",
        "model": "auto",  # Uses configured provider's default
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

Return ONLY valid JSON."""
    },
    
    "detailed_medical": {
        "name": "Detailná zdravotná analýza",
        "description": "Podrobná analýza zdravotných nárokov s dôrazom na diagnózy a liečbu",
        "model": "auto",
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

Return ONLY valid JSON."""
    },
    
    "fraud_detection": {
        "name": "Detekcia podvodov",
        "description": "Analýza zameraná na identifikáciu podozrivých prvkov",
        "model": "auto",
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

Return ONLY valid JSON."""
    },
    
    "quick_review": {
        "name": "Rýchle posúdenie",
        "description": "Zjednodušená rýchla analýza pre jednoduché prípady",
        "model": "auto",
        "template": """Quick insurance claim review. Provide concise assessment.

CLAIM:
{claim_text}

POLICY:
{context}

JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: 0.0-1.0
- reasoning: Brief explanation (max 2 sentences)

Return ONLY valid JSON."""
    },
    
    "slovak_language": {
        "name": "Slovenská analýza",
        "description": "Analýza v slovenskom jazyku",
        "model": "auto",
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
    },
    
    "comprehensive": {
        "name": "Komplexná analýza",
        "description": "Najdôkladnejšia analýza so všetkými aspektmi",
        "model": "auto",
        "template": """You are a senior insurance claim analyst performing a comprehensive review. Analyze every aspect of this claim.

POLICY DOCUMENTS:
{context}

CLAIM DETAILS:
{claim_text}

Perform thorough analysis including:
1. Policy coverage verification
2. Claim validity assessment
3. Documentation completeness
4. Timeline consistency
5. Amount verification
6. Fraud indicators check
7. Regulatory compliance

Provide a comprehensive JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: Score 0.0-1.0
- reasoning: Detailed multi-paragraph explanation
- coverage_analysis: Assessment of policy coverage applicability
- documentation_status: List of provided vs missing documents
- timeline_assessment: Analysis of event timeline
- amount_verification: Assessment of claimed amounts
- fraud_indicators: Any suspicious patterns (can be empty array)
- compliance_notes: Regulatory considerations
- missing_info: Required additional information
- next_steps: Recommended actions

Return ONLY valid JSON."""
    },
    
    "damage_assessment": {
        "name": "Hodnotenie škôd",
        "description": "Špecializovaná analýza pre majetkové škody",
        "model": "auto",
        "template": """You are a property damage assessment specialist. Evaluate the following property damage claim.

POLICY DOCUMENTS:
{context}

CLAIM DETAILS:
{claim_text}

Analyze:
- Type and extent of damage
- Cause determination
- Coverage applicability
- Repair vs replacement assessment
- Cost reasonableness

Provide JSON output with:
- recommendation: "APPROVE", "REJECT", or "INVESTIGATE"
- confidence: Score 0.0-1.0
- damage_type: Category of damage
- damage_severity: "minor", "moderate", "major", or "total_loss"
- cause_determination: Identified cause of damage
- coverage_applicable: Boolean indicating if damage is covered
- estimated_cost_reasonable: Boolean
- reasoning: Detailed explanation
- missing_info: Required documentation

Return ONLY valid JSON."""
    }
}


def get_prompt_list():
    """Returns list of available prompts with metadata"""
    from app.core.config import get_settings
    settings = get_settings()
    
    # Determine current model based on provider
    default_model = "auto"
    if settings.LLM_PROVIDER.lower() == "mistral":
        default_model = settings.LLM_MODEL_VERSION or "mistral-small-latest"
    elif settings.LLM_PROVIDER.lower() == "gemini":
        default_model = settings.LLM_MODEL_VERSION or "gemini-2.0-flash"
    
    return {
        "prompts": [
            {
                "id": key,
                "name": value["name"],
                "description": value.get("description", ""),
                "model": default_model if value.get("model") == "auto" else value.get("model", default_model)
            }
            for key, value in PROMPTS.items()
        ],
        "default": "default"
    }


def get_prompt(prompt_id: str) -> dict:
    """Returns the full prompt configuration for a specific prompt ID"""
    if prompt_id in PROMPTS:
        return PROMPTS[prompt_id]
    return PROMPTS["default"]


def get_prompt_template(prompt_id: str) -> str:
    """Returns the template for a specific prompt ID"""
    if prompt_id in PROMPTS:
        return PROMPTS[prompt_id]["template"]
    return PROMPTS["default"]["template"]
