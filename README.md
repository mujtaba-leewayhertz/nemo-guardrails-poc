# NeMo Guardrails API Demo

This is a FastAPI-based demo application that implements NeMo Guardrails for chat message validation.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is artificial intelligence?"
    }
  ]
}
```

## Features

- Input validation using NeMo Guardrails
  - Safety checks for harmful content
  - Quality checks for unclear input
- Output validation using NeMo Guardrails
  - Safety checks for inappropriate responses
  - Quality checks for unclear responses
- Automatic response generation with GPT-3.5-turbo

## Response Format

```json
{
  "message": "Artificial intelligence is...",
  "validation_status": {
    "input_valid": true,
    "output_valid": true
  }
}
```

## Guardrails Configuration

The application uses two main configuration files:
1. `config.yml` - Main NeMo Guardrails configuration
2. `rails.co` - Colang rules for input and output validation

You can modify these files to add or change validation rules. 