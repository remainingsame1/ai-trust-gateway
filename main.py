import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Zero-Cost AI Trust Gateway")

# Define the structure of the incoming request
class PromptRequest(BaseModel):
    prompt: str

# Expanded dictionary of sensitive credential patterns
CREDENTIAL_PATTERNS = {
    "AWS Access Key": r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
    "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
    "Generic API Key": r"(?i)(?:api[_-]?key|secret[_-]?key|auth[_-]?token)['\" ]*[:=]['\" ]*([a-zA-Z0-9_\-]{20,60})"
}

INJECTION_KEYWORDS = ["ignore previous instructions", "system override", "reveal prompt"]

# Pre-compile regex patterns once at startup for ultra-low latency (as suggested by developers)
COMPILED_CREDENTIAL_PATTERNS = {
    name: re.compile(pattern) for name, pattern in CREDENTIAL_PATTERNS.items()
}

@app.post("/inspect-prompt")
def inspect_prompt(request: PromptRequest):
    user_prompt = request.prompt
    
    # 1. Check for Prompt Injection Attacks
    for keyword in INJECTION_KEYWORDS:
        if keyword in user_prompt.lower():
            raise HTTPException(
                status_code=400,
                detail="Security Alert: Potential prompt injection attack detected."
            )
            
    # 2. Check for Leaked API Keys or Sensitive Data using compiled patterns
    for name, pattern in COMPILED_CREDENTIAL_PATTERNS.items():
        if pattern.search(user_prompt):
            raise HTTPException(
                status_code=400,
                detail=f"Privacy Alert: Sensitive credential detected ({name}). Request blocked."
            )

    # If safe, pass through 
    return {
        "status": "success",
        "message": "Prompt is safe. Safe to forward to LLM.",
        "sanitized_prompt": user_prompt
    }
