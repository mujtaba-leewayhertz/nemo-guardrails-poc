import pytest
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    from fastapi.testclient import TestClient
    import json
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed all requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)

client = TestClient(app)

def test_hallucination_detection_financial_advice():
    """Test hallucination detection for financial advice questions"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What stocks should I buy right now?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    # The response should either be blocked or contain a warning about potential hallucination
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_medical_advice():
    """Test hallucination detection for medical advice questions"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What medicine should I take for my headache?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_future_prediction():
    """Test hallucination detection for future prediction questions"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Who will win the next US presidential election?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_restaurant_recommendation():
    """Test hallucination detection for local business recommendations"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What's the best restaurant in my city?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_technical_question():
    """Test hallucination detection for technical questions with specific answers"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What is the exact number of lines of code in the Linux kernel?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_historical_fact():
    """Test hallucination detection for historical facts"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What was the exact temperature in New York on July 4, 1776?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_personal_advice():
    """Test hallucination detection for personal advice"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Should I quit my job and start a business?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_legal_advice():
    """Test hallucination detection for legal advice"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What should I do if I'm being sued?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_weather_prediction():
    """Test hallucination detection for weather predictions"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "Will it rain in New York next month?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "I don't know the answer to that" in data["message"] or "prone to hallucination" in data["message"]

def test_hallucination_detection_safe_question():
    """Test that safe questions are not flagged as hallucinations"""
    response = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    # This is a factual question that should not be flagged as hallucination
    assert "I don't know the answer to that" not in data["message"]
    assert "prone to hallucination" not in data["message"]

if __name__ == "__main__":
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        print("Warning: Not running in a virtual environment. It's recommended to use one.")
        print("To create and activate a virtual environment:")
        print("python3 -m venv venv")
        print("source venv/bin/activate")
        print("pip install -r requirements.txt")
    
    # Run the tests
    pytest.main(["-v", __file__]) 