# agents_modular.py

class BasicInfoAgent:
    def assess(self, asset):
        score = 0.0
        notes = []
        if asset.get("description") and len(asset["description"]) > 20:
            score += 0.3
        else:
            notes.append("Description is missing or too short.")
        if asset.get("asset_type") and asset["asset_type"] != "unknown":
            score += 0.3
        else:
            notes.append("Asset type is missing or unknown.")
        if asset.get("location"):
            score += 0.2
        else:
            notes.append("Location is missing.")
        if asset.get("estimated_value", 0) > 0:
            score += 0.2
        else:
            notes.append("Estimated value is missing or zero.")
        return {
            "score": round(min(score, 1.0), 2),
            "notes": "All basic info present." if score >= 0.8 else "; ".join(notes)
        }

class ValueAgent:
    def __init__(self):
        self.value_ranges = {
            'real_estate': {'min': 10000, 'max': 1_000_000_000},
            'vehicle': {'min': 1000, 'max': 2_000_000},
            'artwork': {'min': 500, 'max': 100_000_000},
            'equipment': {'min': 100, 'max': 5_000_000},
            'commodity': {'min': 50, 'max': 10_000_000}
        }

    def assess(self, asset):
        value = asset.get("estimated_value", 0)
        asset_type = asset.get("asset_type", "unknown")
        if asset_type not in self.value_ranges:
            return {"score": 0.5, "notes": "Unknown asset type"}
        r = self.value_ranges[asset_type]
        if r["min"] <= value <= r["max"]:
            return {"score": 1.0, "notes": "Value within typical range"}
        elif value < r["min"]:
            return {"score": 0.4, "notes": "Value below expected"}
        return {"score": 0.6, "notes": "Value above expected"}

class JurisdictionAgent:
    def assess(self, asset):
        location = asset.get("location", "")
        loc = location.upper()
        mapping = {
            'IN': ['INDIA', 'MUMBAI', 'DELHI', 'BANGALORE', 'PUNE'],
            'US': ['USA', 'UNITED STATES', 'NEW YORK'],
            'UK': ['UNITED KINGDOM', 'LONDON'],
            'CA': ['CANADA'],
            'EU': ['GERMANY', 'FRANCE', 'ITALY', 'EUROPE'],
            'SG': ['SINGAPORE']
        }
        for code, keywords in mapping.items():
            if any(city in loc for city in keywords):
                if code == "IN":
                    return {"score": 0.9, "notes": "Jurisdiction recognized as India"}
                else:
                    return {"score": 0.9, "notes": f"Jurisdiction recognized as {code}"}
        return {"score": 0.5, "notes": "Jurisdiction not recognized"}

class AssetSpecificAgent:
    def assess(self, asset):
        asset_type = asset.get("asset_type", "unknown")
        description = asset.get("description", "").lower()
        indicators = {
            "real_estate": ["flat", "apartment", "bedroom", "sqft", "deed"],
            "vehicle": ["engine", "model", "mileage", "year"],
            "artwork": ["artist", "canvas", "painting"],
            "equipment": ["serial", "manufacturer", "warranty"],
            "commodity": ["weight", "grade", "purity"]
        }
        if asset_type not in indicators:
            return {"score": 0.5, "notes": "Unknown asset type"}
        score = 0.5
        hits = 0
        for word in indicators[asset_type]:
            if word in description:
                score += 0.1
                hits += 1
        notes = f"Found {hits} asset-specific keywords." if hits else "No asset-specific keywords found."
        return {"score": round(min(score, 1.0), 2), "notes": notes}

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
            results[key] = agent_result["score"]
            explanations.append(f"{key}: {agent_result['notes']}")
        avg_score = sum(results.values()) / len(results)
        status = "verified" if avg_score >= 0.7 else ("requires_review" if avg_score >= 0.5 else "rejected")
        return {
            "overall_score": round(avg_score, 2),
            "status": status,
            "breakdown": results,
            "agent_notes": explanations
        }
