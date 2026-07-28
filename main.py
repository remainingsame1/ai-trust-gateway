import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Zero-Cost AI Trust Gateway")

# Define the structure of the incoming request
class PromptRequest(BaseModel):
    prompt: str

# Regular expressions to catch sensitive info & common prompt injections
API_KEY_REGEX = r"(sk-[a-zA-Z0-9]{20,})"
CREDIT_CARD_REGEX = r"\b(?:\d[ -]*?){13,16}\b"
INJECTION_KEYWORDS = ["ignore previous instructions", "system override", "reveal prompt"]

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

    # 2. Check for Leaked API Keys or Secrets
    if re.search(API_KEY_REGEX, user_prompt) or re.search(CREDIT_CARD_REGEX, user_prompt):
        raise HTTPException(
            status_code=400, 
            detail="Privacy Alert: Sensitive credentials or personal data detected. Request blocked."
        )

    # If safe, pass through (In production, you would forward this to OpenAI/Anthropic here)
    return {
        "status": "success",
        "message": "Prompt is safe. Safe to forward to LLM.",
        "sanitized_prompt": user_prompt
    }
