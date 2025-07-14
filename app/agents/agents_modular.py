import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load Gemini API key from .env
load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
# Use the latest recommended Gemini model for agentic AI
llm_model = genai.GenerativeModel("gemini-2.0-flash")

def call_llm(prompt):
    response = llm_model.generate_content(prompt)
    content = response.text.strip()
    # Remove code block formatting if present
    cleaned = re.sub(r"^``````$", "", content, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # Fallback: try to extract JSON from text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"score": 0.5, "notes": "LLM output parsing failed."}

class BasicInfoAgent:
    def assess(self, asset):
        prompt = f"""
You are an AI agent checking if all basic asset information is present and complete.
Asset fields:
- Type: {asset.get('asset_type')}
- Value: {asset.get('estimated_value')}
- Location: {asset.get('location')}
- Description: {asset.get('description')}
Score 1.0 if all fields are present and detailed, 0.5 if some are missing, 0.0 if mostly missing. Explain.
Respond as JSON: {{"score": float, "notes": "..."}}
"""
        return call_llm(prompt)

class ValueAgent:
    def assess(self, asset):
        prompt = f"""
You are an AI agent evaluating if the asset's estimated value is plausible for its type and location.
Asset fields:
- Type: {asset.get('asset_type')}
- Value: {asset.get('estimated_value')}
- Location: {asset.get('location')}
- Description: {asset.get('description')}
Score 1.0 if value is plausible, 0.4 if too low, 0.6 if too high, 0.5 if unknown. Explain.
Respond as JSON: {{"score": float, "notes": "..."}}
"""
        return call_llm(prompt)

class JurisdictionAgent:
    def assess(self, asset):
        prompt = f"""
You are an AI agent verifying the jurisdiction/location of the asset.
Asset fields:
- Location: {asset.get('location')}
Score 0.9 if location is specific and recognized (especially any Indian city/state/UT), 0.5 if vague or missing. Explain.
Respond as JSON: {{"score": float, "notes": "..."}}
"""
        return call_llm(prompt)

class AssetSpecificAgent:
    def assess(self, asset):
        prompt = f"""
You are an AI agent checking if the asset description contains type-specific details and keywords.
Asset fields:
- Type: {asset.get('asset_type')}
- Description: {asset.get('description')}
Score 1.0 if many relevant details/keywords, 0.5 if some, 0.0 if none. Explain.
Respond as JSON: {{"score": float, "notes": "..."}}
"""
        return call_llm(prompt)

class CoordinatorAgent:
    def __init__(self):
        self.agents = [
            ("basic_info", BasicInfoAgent()),
            ("value_assessment", ValueAgent()),
            ("jurisdiction", JurisdictionAgent()),
            ("asset_specific", AssetSpecificAgent())
        ]

    def verify(self, asset):
        results = {}
        explanations = []
        for key, agent in self.agents:
            agent_result = agent.assess(asset)
            results[key] = agent_result.get("score", 0.5)
            explanations.append(f"{key}: {agent_result.get('notes', '')}")
        avg_score = sum(results.values()) / len(results)
        status = "verified" if avg_score >= 0.7 else ("requires_review" if avg_score >= 0.5 else "rejected")
        return {
            "overall_score": round(avg_score, 2),
            "status": status,
            "breakdown": results,
            "agent_notes": explanations
        }
