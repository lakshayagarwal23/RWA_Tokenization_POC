class ValueAgent:
    def assess(self, asset):
        value = asset.get("estimated_value", 0)
        asset_type = asset.get("asset_type", "unknown")
        ranges = {
            "real_estate": (10000, 1_000_000_000),
            "vehicle": (1000, 2_000_000),
            "artwork": (500, 100_000_000),
            "equipment": (100, 5_000_000),
            "commodity": (50, 10_000_000),
        }
        min_val, max_val = ranges.get(asset_type, (0, float('inf')))
        if min_val <= value <= max_val:
            return {"score": 1.0, "notes": "Value within typical range"}
        elif value < min_val:
            return {"score": 0.4, "notes": "Value below expected"}
        else:
            return {"score": 0.6, "notes": "Value above expected"}

class RiskAgent:
    def assess(self, asset):
        desc = asset.get("description", "").lower()
        if "unknown" in desc or len(desc) < 20:
            return {"score": 0.4, "notes": "Description vague or too short"}
        return {"score": 1.0, "notes": "Description seems adequate"}

class ConsistencyAgent:
    def assess(self, asset):
        asset_type = asset.get("asset_type", "")
        desc = asset.get("description", "").lower()
        keywords = {
            "real_estate": ["apartment", "sqft", "deed"],
            "vehicle": ["engine", "model", "mileage"],
            "artwork": ["artist", "painting"],
        }
        hits = sum(1 for word in keywords.get(asset_type, []) if word in desc)
        score = 0.5 + 0.1 * hits
        return {"score": min(score, 1.0), "notes": f"Found {hits} asset-specific keywords"}

class DescriptionQualityAgent:
    def assess(self, asset):
        desc = asset.get("description", "").strip().lower()
        if len(desc) < 50 or any(term in desc for term in ["unknown", "n/a", "none"]):
            return {"score": 0.4, "notes": "Description is too short or vague"}
        return {"score": 1.0, "notes": "Description is detailed and specific"}

class ValueConsistencyAgent:
    def assess(self, asset):
        value = asset.get("estimated_value", 0)
        desc = asset.get("description", "").lower()
        if "old" in desc and value > 1_000_000:
            return {"score": 0.5, "notes": "High value for 'old' asset"}
        if "luxury" in desc and value < 100_000:
            return {"score": 0.5, "notes": "Low value for 'luxury' asset"}
        return {"score": 1.0, "notes": "Value matches description"}

class LocationSpecificityAgent:
    def assess(self, asset):
        location = asset.get("location", "").strip().lower()
        if not location or location in ["unknown", "n/a", "none"]:
            return {"score": 0.4, "notes": "Location is vague or missing"}
        if len(location) < 3:
            return {"score": 0.6, "notes": "Location too short"}
        if "india" in location:
            return {"score": 1.0, "notes": "Location is specific and recognized (India)"}
        indian_states = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
            "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh",
            "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
            "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
            "west bengal", "delhi", "jammu", "kashmir", "ladakh", "puducherry", "chandigarh", "dadra",
            "daman", "daman and diu", "andaman", "nicobar", "lakshadweep"
        ]
        if any(state in location for state in indian_states):
            return {"score": 1.0, "notes": "Location is specific and recognized (India)"}
        return {"score": 1.0, "notes": "Location is specific"}

class UserInteractionAgent:
    def query(self, asset):
        questions = []
        if not asset.get("location"):
            questions.append("Can you specify the asset's location?")
        if asset.get("estimated_value", 0) == 0:
            questions.append("What is the estimated value?")
        if len(asset.get("description", "")) < 20:
            questions.append("Please provide a more detailed description.")
        return questions

class CoordinatorAgent:
    def __init__(self):
        self.agents = [
            ValueAgent(), RiskAgent(), ConsistencyAgent(),
            DescriptionQualityAgent(), ValueConsistencyAgent(),
            LocationSpecificityAgent()
        ]
        self.user_interaction_agent = UserInteractionAgent()

    def verify(self, asset):
        results = {}
        for agent in self.agents:
            agent_name = agent.__class__.__name__
            results[agent_name] = agent.assess(asset)
        scores = [r["score"] for r in results.values()]
        avg_score = sum(scores) / len(scores)
        status = "verified" if avg_score >= 0.7 else ("requires_review" if avg_score >= 0.5 else "rejected")
        questions = self.user_interaction_agent.query(asset)
        return {
            "overall_score": round(avg_score, 2),
            "status": status,
            "breakdown": results,
            "follow_up_questions": questions,
            "explanation": [r["notes"] for r in results.values()]
        }
