# Agentic AI Blockchain Asset Tokenization Platform

## Overview


This project leverages advanced Large Language Models (LLMs) and a modular agentic AI framework to automate, explain, and scale the verification and tokenization of real-world assets (RWAs) such as real estate, vehicles, and artwork. The platform is designed for transparency, explainability, and scalability, supporting any city or town in India (and globally).

## Features

- **LLM-Powered Asset Parsing:**  
  Extracts structured asset data from free-form user descriptions using Gemini (or similar) LLMs, with robust fallback logic.

- **Modular Agentic Verification:**  
  Independent AI agents evaluate each asset for value, risk, consistency, description quality, location specificity, and more.

- **Explainable Decisions:**  
  Every asset receives a transparent verification breakdown and actionable recommendations.

- **Tokenization Workflow:**  
  Verified assets can be tokenized (mock blockchain), with all actions logged and traceable.

- **Modern Web Interface:**  
  User-friendly frontend for asset submission, verification, and tokenization status tracking.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agentic-rwa-tokenization.git
cd agentic-rwa-tokenization
```

### 2. Set Up the Environment

- Install Python 3.8+.
- Create and activate a virtual environment:

  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

- Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

### 3. Configure Environment Variables

- Copy `.env.example` to `.env` and fill in your Gemini API key and other secrets:

  ```
  GEMINI_API_KEY=your_gemini_api_key_here
  FLASK_ENV=development
  SECRET_KEY=your_secret_key
  ```

### 4. Initialize the Database

```bash
python -c "from app.models.database import db; db.create_all()"
```

### 5. Run the Application

```bash
python main.py
```

- The app will be available at [http://localhost:5000](http://localhost:5000)

## Project Structure

```
/app/
  agents/
    llm_utils.py
    verification_agent.py
    agents_modular.py
    tokenization_agent.py
  models/
    database.py
main.py
print_records.py
requirements.txt
.env
/static/
/templates/
```

- **agents/**: All AI agent modules (LLM parsing, modular verification, tokenization).
- **models/**: ORM models for User, Asset, Transaction.
- **main.py**: Flask backend and API endpoints.
- **print_records.py**: Utility for printing database records.
- **static/** and **templates/**: Frontend assets and HTML templates.

## Agentic AI Framework

| Agent Name                | Role & Description                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------------|
| LLM Parsing Agent         | Extracts structured fields from user input using Gemini LLM; falls back to keyword mapping.        |
| ValueAgent                | Checks if asset value is within plausible range for its type.                                      |
| RiskAgent                 | Flags vague or suspicious descriptions.                                                           |
| ConsistencyAgent          | Ensures asset type matches description keywords.                                                  |
| DescriptionQualityAgent   | Rewards detailed, specific descriptions.                                                          |
| ValueConsistencyAgent     | Checks if value matches claims in description.                                                    |
| LocationSpecificityAgent  | Accepts any Indian (or global) location; validates jurisdiction.                                  |
| UserInteractionAgent      | Generates clarifying questions if required info is missing.                                       |
| CoordinatorAgent          | Aggregates all agent outputs, computes final score and status, and provides explainable results.  |

## Usage Instructions

1. **Submit an Asset:**  
   Use the web form to enter your wallet address, a detailed asset description, and (optionally) your email.

2. **Verification:**  
   The backend parses your description and runs modular agentic verification. You can view the verification score, breakdown, and recommendations in the UI.

3. **Tokenization:**  
   If your asset is verified, you can tokenize it with a single click. Token details (ID, contract address, etc.) are displayed and stored.

4. **Review and Audit:**  
   All assets, verifications, and tokenizations are stored in the database. Use `print_records.py` or a SQLite browser for inspection.

## Example Asset Description

> A spacious 3-bedroom apartment flat in Etawah, Uttar Pradesh, India, 1200 sqft, with clear title deed and all property documents. Recently valued at ₹2,500,000 by a certified government valuer. The property includes 2 bathrooms, a balcony, and covered parking. Built in 2018 and ready for immediate sale.

## API Endpoints

| Endpoint                        | Description                                 |
|----------------------------------|---------------------------------------------|
| `/api/intake`                   | Submit a new asset for parsing & storage    |
| `/api/verify/`        | Trigger agentic verification                |
| `/api/tokenize/`      | Tokenize a verified asset                   |
| `/api/asset/`         | Get asset details and transaction history   |
| `/api/assets/`  | List all assets for a user                  |
| `/api/stats`                    | Platform statistics                         |

## Best Practices

- Provide detailed, specific asset descriptions for best verification results.
- Ensure your `.env` file is set up with valid API keys and secrets.
- Use the modular agentic AI framework to add or customize verification logic as your use case evolves.
- For academic or enterprise deployments, extend the tokenization agent for real blockchain integration.
\
