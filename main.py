import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. Combined and optimized regex for secrets/sensitive data
secret_patterns = [
    r"api[_-]?key",
    r"password",
    r"secret[_-]?token",
]
combined_secrets_regex = re.compile("|".join(f"(?:{p})" for p in secret_patterns), re.IGNORECASE)

# 2. Robust prompt injection patterns handling optional whitespace evasion (e.g., "ignorepreviousinstruction")
injection_patterns = [
    r"ignore\s*previous\s*instructions",
    r"disregard\s*all\s*prior\s*guidelines",
]
combined_injection_regex = re.compile("|".join(f"(?:{p})" for p in injection_patterns), re.IGNORECASE)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/proxy")
def evaluate_prompt(req: PromptRequest):
    # Check for prompt injections using the robust combined pattern
    if combined_injection_regex.search(req.prompt):
        raise HTTPException(status_code=400, detail="Potential prompt injection detected.")
    
    # Check for leaked credentials/secrets
    if combined_secrets_regex.search(req.prompt):
        raise HTTPException(status_code=400, detail="Leaked credential or secret detected.")
        
    return {"status": "safe", "prompt": req.prompt}
