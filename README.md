# Risk-Adaptive Agentic AI Framework

Reproducible research prototype and evaluation harness for risk-adaptive
Edge-IoT threat detection and incident response.

## Step 1: run the starter API

1. Activate the Python 3.11 virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and leave the values blank for this step.
4. Start the API with `uvicorn api.main:app --reload`.
5. Open `http://127.0.0.1:8000/health`.

Run the checks with `pytest`.

## Security convention

Credentials belong only in the local `.env` file, which is excluded from Git.
Never commit an API key, token, or password.

