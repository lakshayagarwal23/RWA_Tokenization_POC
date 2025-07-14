import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GENAI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

def fallback_asset_type(description: str) -> str:
    """
    Fallback mapping if LLM fails to categorize asset type.
    """
    description = description.lower()
    if any(word in description for word in ['apartment', 'flat', 'bedroom', 'sqft', 'deed', 'property', 'house']):
        return 'real_estate'
    elif any(word in description for word in ['engine', 'model', 'mileage', 'car', 'vehicle', 'truck', 'bike']):
        return 'vehicle'
    elif any(word in description for word in ['artist', 'painting', 'canvas', 'sculpture', 'artwork']):
        return 'artwork'
    elif any(word in description for word in ['serial', 'manufacturer', 'warranty', 'equipment', 'machine']):
        return 'equipment'
    elif any(word in description for word in ['weight', 'grade', 'purity', 'commodity', 'gold', 'silver', 'oil']):
        return 'commodity'
    else:
        return 'unknown'

def clean_llm_output(content: str) -> str:
    """
    Cleans LLM output by removing markdown/code block markers and extracting JSON.
    """
    # Remove triple backticks and 'json' markers
    content = re.sub(r"^```(?:json)?", "", content, flags=re.MULTILINE)
    content = re.sub(r"```$", "", content, flags=re.MULTILINE)
    content = content.strip()
    # Remove any leading text before the JSON object
    json_start = content.find("{")
    if json_start != -1:
        content = content[json_start:]
    return content

def extract_asset_info_with_llm(user_input: str) -> dict:
    """
    Calls Gemini LLM to extract asset information from user input.
    Accepts any city/town in India as valid. Falls back to keyword mapping if LLM fails or returns 'unknown'.
    """
    print("✅ Calling Gemini for asset info extraction...")
    prompt = f"""
You are an intelligent assistant that extracts structured information from asset descriptions.
Extract and return the following fields in JSON:
- asset_type: One of [real_estate, vehicle, artwork, equipment, commodity]
- estimated_value: A number (preferably in INR, or fallback to USD if only that is given), no commas or currency symbol
- location: City or region (as precise as possible, e.g., 'Etawah, Uttar Pradesh, India' or 'Mumbai, India' or 'Bandra, Mumbai, India')
- description: The original user input

USER INPUT:
\"\"\"{user_input}\"\"\"

Return only valid JSON:
{{
  "asset_type": "...",
  "estimated_value": ...,
  "location": "...",
  "description": "..."
}}
"""
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        print("Gemini raw response:", repr(content))
        cleaned = clean_llm_output(content)
        if not cleaned or not cleaned.startswith("{"):
            raise ValueError("LLM did not return valid JSON.")
        data = json.loads(cleaned)
        asset_type = data.get("asset_type", "unknown")
        if asset_type == "unknown":
            asset_type = fallback_asset_type(data.get("description", user_input))
        # Accept any location string as valid; do not penalize for unknown/small cities
        location = data.get("location", "unknown")
        return {
            "asset_type": asset_type,
            "estimated_value": float(data.get("estimated_value", 0)),
            "location": location,
            "description": data.get("description", user_input)
        }
    except Exception as e:
        print("❌ Error parsing Gemini response:", e)
        asset_type = fallback_asset_type(user_input)
        return {
            "asset_type": asset_type,
            "estimated_value": 0,
            "location": "unknown",
            "description": user_input
        }
