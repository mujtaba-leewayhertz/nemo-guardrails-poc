from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add the current directory to the Python path
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DEMO_DIR)

try:
    from main import rails, check_safety, check_jailbreak, check_hallucination
except ImportError as e:
    print(f"Failed to import from main.py: {str(e)}")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing guardrails: {str(e)}")
    sys.exit(1)

app = FastAPI(
    title="Jailbreak Detection API",
    description="API for detecting and preventing AI jailbreak attempts",
    version="1.0.0"
)

class JailbreakRequest(BaseModel):
    text: str
    is_safety_question: Optional[bool] = False

class JailbreakResponse(BaseModel):
    is_jailbreak: bool
    is_hallucination: bool
    is_input_check_failed: bool
    is_output_check_failed: bool
    response: str
    confidence: float
    detected_patterns: list[str]
    input_check_reason: Optional[str] = None
    output_check_reason: Optional[str] = None

@app.post("/detect", response_model=JailbreakResponse)
async def detect_jailbreak(request: JailbreakRequest):
    """
    Detect if the given text contains a jailbreak attempt or hallucination.
    
    - **text**: The text to analyze
    - **is_safety_question**: Whether this is a safety-related question (default: False)
    """
    try:
        # First check input safety
        is_input_safe = check_safety(request.text) == "yes"
        is_jailbreak_attempt = check_jailbreak(request.text) == "yes"
        
        # Initialize response flags
        is_jailbreak = False
        is_hallucination = False
        is_input_check_failed = False
        is_output_check_failed = False
        input_check_reason = None
        output_check_reason = None
        confidence = 0.0
        detected_patterns = []
        
        # Handle input check failure
        if not is_input_safe:
            is_input_check_failed = True
            if any(word in request.text.lower() for word in ["bomb", "weapon", "harm", "kill", "hurt"]):
                input_check_reason = "safety_concern"
            elif any(word in request.text.lower() for word in ["drug", "illegal", "hack", "steal"]):
                input_check_reason = "illegal"
            response_content = "I'm sorry, but I cannot assist with that request as it involves potentially harmful or illegal activities."
            return JailbreakResponse(
                is_jailbreak=False,
                is_hallucination=False,
                is_input_check_failed=True,
                is_output_check_failed=False,
                response=response_content,
                confidence=0.9,
                detected_patterns=["unsafe_input"],
                input_check_reason=input_check_reason,
                output_check_reason=None
            )
        
        # Handle jailbreak attempt
        if is_jailbreak_attempt:
            response_content = "I've detected an attempt to bypass system restrictions. I must maintain my safety protocols and cannot comply with such requests."
            return JailbreakResponse(
                is_jailbreak=True,
                is_hallucination=False,
                is_input_check_failed=False,
                is_output_check_failed=False,
                response=response_content,
                confidence=0.9,
                detected_patterns=["jailbreak_detected"],
                input_check_reason=None,
                output_check_reason=None
            )
        
        # If input is safe and not a jailbreak attempt, generate response
        response = rails.generate(messages=[{"role": "user", "content": request.text}])
        
        # Handle different response formats
        if isinstance(response, str):
            response_content = response
        elif isinstance(response, dict):
            response_content = response.get('content', '')
        elif isinstance(response, list):
            response_content = response[0].get('content', '') if response else ""
        else:
            response_content = str(response)
        
        # Check for hallucination in response
        is_hallucination = check_hallucination(response_content) == "yes"
        
        # Check output safety
        is_output_safe = check_safety(response_content) == "yes"
        if not is_output_safe:
            is_output_check_failed = True
            if any(word in response_content.lower() for word in ["bomb", "weapon", "harm", "kill", "hurt"]):
                output_check_reason = "safety_concern"
            elif any(word in response_content.lower() for word in ["drug", "illegal", "hack", "steal"]):
                output_check_reason = "illegal"
            response_content = "I apologize, but I cannot provide that response as it may contain inappropriate content."
        
        # Set confidence based on checks
        if is_hallucination:
            confidence = 0.8
            detected_patterns.append("hallucination_detected")
        elif is_output_check_failed:
            confidence = 0.9
            detected_patterns.append("unsafe_output")
        else:
            confidence = 0.5
        
        return JailbreakResponse(
            is_jailbreak=is_jailbreak,
            is_hallucination=is_hallucination,
            is_input_check_failed=is_input_check_failed,
            is_output_check_failed=is_output_check_failed,
            response=response_content,
            confidence=confidence,
            detected_patterns=detected_patterns,
            input_check_reason=input_check_reason,
            output_check_reason=output_check_reason
        )
        
    except Exception as e:
        print(f"Error in detect_jailbreak: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 