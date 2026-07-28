# AI Trust Gateway 🛡️

A lightweight, zero-cost Python proxy middleware designed to act as an input firewall for LLM applications. It intercepts prompts in real-time to catch prompt injections, jailbreaks, and leaked credentials (like API keys or personal data) before they ever reach an AI model.

## Features
* **Prompt Injection Detection:** Blocks common override commands and system hijack attempts.
* **Credential & PII Guardrails:** Uses regex patterns to instantly catch exposed API keys or sensitive credit card data.
* **Ultra-Low Latency:** Built on FastAPI for fast local execution.

## Quick Start

1. Clone the repository and install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
