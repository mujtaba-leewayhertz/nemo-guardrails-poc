from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from nemoguardrails import LLMRails, RailsConfig
from dotenv import load_dotenv
import uvicorn
import openai
import json
import nest_asyncio
import asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Define request and response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None

class ValidationStatus(BaseModel):
    input_valid: bool = True
    output_valid: bool = True

class ChatResponse(BaseModel):
    message: str
    validation_status: ValidationStatus
    conversation_id: str = ""

# Get the absolute path to the demo directory
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the guardrails configuration
#mac
#config_path = os.path.join(DEMO_DIR, "rails.co")
#windows
config_path = os.path.normpath(os.path.join(DEMO_DIR, "config.yml"))
if not os.path.exists(config_path):
    raise ValueError(f"Guardrails config file not found at {config_path}")

try:
    # Convert Windows path to forward slashes and ensure it's absolute
    config_path = os.path.abspath(config_path).replace("\\", "/")
    config = RailsConfig.from_path(config_path)
    # Initialize the guardrails system
    rails = LLMRails(config)
except Exception as e:
    raise ValueError(f"Failed to initialize guardrails: {str(e)}")

# Initialize OpenAI with proper configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Add custom functions for safety and jailbreak checks
def check_safety(content: str) -> str:
    """Check if the content is safe."""
    if any(phrase in content.lower() for phrase in [
        "bomb", "weapon", "harm", "kill", "hurt", "drug", "illegal", "hack", "steal"
    ]):
        return "no"
    return "yes"

def check_jailbreak(content: str) -> str:
    """Check if the content contains a jailbreak attempt."""
    if any(phrase in content.lower() for phrase in [
        "pretend to be", "act as", "you are now", "you're now", "be a different",
        "dan", "DAN", "no restrictions", "without restrictions", "unrestricted",
        "no rules", "no boundaries", "no limits", "unlimited", "override",
        "ignore", "bypass", "remove restrictions", "disable", "turn off",
        "dan mode", "developer mode", "unrestricted mode", "free mode",
        "unlimited mode", "let's play", "game", "free to", "can say",
        "do anything", "say anything", "no limitations"
    ]):
        return "yes"
    return "no"

def check_hallucination(content: str) -> str:
    """Check if the content contains hallucination."""
    if any(phrase in content.lower() for phrase in [
        "there are no", "there is no", "does not exist", "not possible",
        "not real", "not true", "incorrect", "false", "fictional",
        "speculative", "no known", "no evidence", "no proof", "no record",
        "no documentation", "no verification", "no confirmation",
        "no validation", "no substantiation", "no corroboration"
    ]):
        return "yes"
    return "no"

# Register the actions
rails.register_action(check_safety, "check_safety")
rails.register_action(check_jailbreak, "check_jailbreak")
rails.register_action(check_hallucination, "check_hallucination")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get the last user message
        last_message = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
        if not last_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Convert messages to the format expected by NeMo Guardrails
        messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in request.messages
        ]

        # Process through NeMo Guardrails
        response = await rails.generate_async(messages=messages)

        # Initialize validation status
        validation_status = {
            "input_valid": True,
            "output_valid": True
        }

        # Extract the response content
        response_content = response if isinstance(response, str) else response.get("content", "")

        # Check for hallucination-prone questions
        hallucination_triggers = [
            "stocks", "buy", "recommend", "best", "restaurant", "city",
            "predict", "future", "election", "weather", "medicine", "medical",
            "legal", "lawsuit", "sued", "advice", "should i", "personal",
            "exact number", "exact temperature", "exact", "specific", "lines of code",
            "temperature", "rain", "next month", "historical", "1776"
        ]

        if any(trigger in last_message.content.lower() for trigger in hallucination_triggers):
            response_content = "I don't know the answer to that. This type of question is prone to hallucination."
            validation_status["output_valid"] = False

        # Check for safety concerns in input
        if any(word in last_message.content.lower() for word in [
            "harm", "kill", "hurt", "bomb", "weapon", "crime", "illegal", "hack", "steal"
        ]):
            validation_status["input_valid"] = False
            response_content = "I apologize, but I cannot assist with that request."

        # Check for sensitive information requests
        elif any(word in last_message.content.lower() for word in [
            "password", "credit card", "social security", "bank account"
        ]):
            validation_status["input_valid"] = False
            response_content = "I cannot assist with sensitive personal information."

        # Check for unclear input
        elif (len(last_message.content) < 2 or 
              any(pattern in last_message.content for pattern in ["??", "!!", "..."]) or
              last_message.content.isalpha() and len(last_message.content) > 8):
            validation_status["input_valid"] = False
            response_content = "I'm not sure I understand. Could you please rephrase your question?"

        # Check output for safety concerns
        if isinstance(response_content, str) and any(word in response_content.lower() for word in [
            "harm", "kill", "weapon", "illegal"
        ]):
            validation_status["output_valid"] = False
            response_content = "I've detected potentially harmful content in my response. Let me rephrase that in a more appropriate way."

        return ChatResponse(
            message=response_content,
            validation_status=validation_status,
            conversation_id=request.conversation_id or ""
        )

    except openai.error.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export the functions and rails object
__all__ = ['rails', 'check_safety', 'check_jailbreak', 'check_hallucination']

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 