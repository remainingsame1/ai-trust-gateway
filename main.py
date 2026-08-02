import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Zero-Cost AI Trust Gateway")

class PromptRequest(BaseModel):
    prompt: str

class ResponseRequest(BaseModel):
    ai_response: str

# Input credential patterns
CREDENTIAL_PATTERNS = {
    "AWS Access Key": r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
    "Credit Card": r"\b(?:\d[ -]*?){13,16}\b"
}

INJECTION_KEYWORDS = ["ignore previous instructions", "system override", "reveal prompt"]

# Output PII patterns (to scrub from model responses)
PII_PATTERNS = {
    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "Phone Number": r"\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
}

COMPILED_CREDENTIAL_PATTERNS = {name: re.compile(pattern) for name, pattern in CREDENTIAL_PATTERNS.items()}
COMPILED_PII_PATTERNS = {name: re.compile(pattern) for name, pattern in PII_PATTERNS.items()}

@app.post("/inspect-prompt")
def inspect_prompt(request: PromptRequest):
    user_prompt = request.prompt
    
    for keyword in INJECTION_KEYWORDS:
        if keyword in user_prompt.lower():
            raise HTTPException(status_code=400, detail="Security Alert: Potential prompt injection attack detected.")
            
    for name, pattern in COMPILED_CREDENTIAL_PATTERNS.items():
        if pattern.search(user_prompt):
            raise HTTPException(status_code=400, detail=f"Privacy Alert: Sensitive credential detected ({name}). Request blocked.")

    return {"status": "success", "message": "Prompt is safe.", "sanitized_prompt": user_prompt}

# New feature: Output PII Redaction Endpoint
@app.post("/inspect-response")
def inspect_response(request: ResponseRequest):
    sanitized_response = request.ai_response
    
    # Automatically mask PII like emails and phone numbers in the AI output
    for name, pattern in COMPILED_PII_PATTERNS.items():
        sanitized_response = pattern.sub(f"[REDACTED {name}]", sanitized_response)
        
    return {
        "status": "success",
        "message": "AI response sanitized successfully.",
        "clean_response": sanitized_response
    }
