import re
import json
from typing import Dict, List

class VerificationAgent:
    def __init__(self):
        self.verification_threshold = 0.7
        self.value_ranges = {
            'real_estate': {'min': 10000, 'max': 1_000_000_000},
            'vehicle': {'min': 1000, 'max': 2_000_000},
            'artwork': {'min': 500, 'max': 100_000_000},
            'equipment': {'min': 100, 'max': 5_000_000},
            'commodity': {'min': 50, 'max': 10_000_000}
        }

    def verify_asset(self, asset_data: Dict) -> Dict:
        result = {
            'overall_score': 0.0,
            'status': 'pending',
            'breakdown': {},
            'issues': [],
            'recommendations': [],
            'next_steps': []
        }
        try:
            basic_score = self._verify_basic_information(asset_data)
            value_score = self._verify_value(asset_data)
            jurisdiction_score = self._verify_jurisdiction(asset_data)
            asset_specific_score = self._verify_asset_specific(asset_data)
            result["breakdown"].update({
                "basic_info": basic_score,
                "value_assessment": value_score,
                "jurisdiction": jurisdiction_score,
                "asset_specific": asset_specific_score
            })
            scores = [basic_score, value_score, jurisdiction_score, asset_specific_score]
            result["overall_score"] = round(sum(scores) / len(scores), 2)
            if result["overall_score"] >= self.verification_threshold:
                result["status"] = "verified"
            elif result["overall_score"] >= 0.5:
                result["status"] = "requires_review"
            else:
                result["status"] = "rejected"
            result["recommendations"] = self._generate_recommendations(result)
            result["next_steps"] = self._define_next_steps(result["status"])
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Verification error: {str(e)}")
        return result

    def _verify_basic_information(self, asset_data: Dict) -> float:
        score = 0.0
        if asset_data.get("description") and len(asset_data["description"]) > 20:
            score += 0.3
        if asset_data.get("asset_type") and asset_data["asset_type"] != "unknown":
            score += 0.3
        if asset_data.get("location"):
            score += 0.2
        if asset_data.get("estimated_value", 0) > 0:
            score += 0.2
        return round(min(score, 1.0), 2)

    def _verify_value(self, asset_data: Dict) -> float:
        value = asset_data.get("estimated_value", 0)
        asset_type = asset_data.get("asset_type", "unknown")
        if asset_type not in self.value_ranges:
            return 0.5
        r = self.value_ranges[asset_type]
        if r["min"] <= value <= r["max"]:
            return 1.0
        elif value < r["min"]:
            return 0.4
        return 0.6

    def _verify_jurisdiction(self, asset_data: Dict) -> float:
        jurisdiction = self._extract_jurisdiction(asset_data.get("location", ""))
        if jurisdiction == "IN":
            return 0.9
        elif jurisdiction != "OTHER":
            return 0.9
        return 0.5

    def _verify_asset_specific(self, asset_data: Dict) -> float:
        asset_type = asset_data.get("asset_type", "unknown")
        description = asset_data.get("description", "").lower()
        indicators = {
            "real_estate": [
                "flat", "apartment", "bedroom", "sqft", "deed", "house", "property", "building", "land", "condo", "villa", "bathroom", "plot", "bungalow"
            ],
            "vehicle": [
                "engine", "model", "mileage", "year", "car", "truck", "motorcycle", "boat", "plane", "vehicle", "sedan", "suv", "registration"
            ],
            "artwork": [
                "artist", "canvas", "painting", "sculpture", "art", "artwork", "oil painting", "frame"
            ],
            "equipment": [
                "serial", "manufacturer", "warranty", "machinery", "equipment", "tool", "device", "machine", "operating hours", "condition"
            ],
            "commodity": [
                "weight", "grade", "purity", "gold", "silver", "oil", "wheat", "commodity", "metal", "oz", "certificate", "assay", "quality"
            ]
        }
        if asset_type not in indicators:
            return 0.5
        score = 0.5
        for word in indicators[asset_type]:
            if word in description:
                score += 0.05  # More granular, so maxes out with more keywords
        return round(min(score, 1.0), 2)

    def _extract_jurisdiction(self, location: str) -> str:
        if not location:
            return ''
        loc = location.lower()
        if "india" in loc:
            return "IN"
        indian_states = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
            "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh",
            "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab",
            "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
            "west bengal", "delhi", "jammu", "kashmir", "ladakh", "puducherry", "chandigarh", "dadra",
            "daman", "daman and diu", "andaman", "nicobar", "lakshadweep"
        ]
        if any(state in loc for state in indian_states):
            return "IN"
        mapping = {
            'US': ['usa', 'united states', 'america', 'new york', 'california', 'texas'],
            'UK': ['united kingdom', 'england', 'scotland', 'wales', 'london'],
            'CA': ['canada', 'toronto', 'vancouver', 'montreal'],
            'EU': ['germany', 'france', 'spain', 'italy', 'netherlands'],
            'SG': ['singapore']
        }
        for code, keywords in mapping.items():
            if any(city in loc for city in keywords):
                return code
        return 'OTHER'

    def _generate_recommendations(self, result: Dict) -> List[str]:
        recos = []
        b = result.get("breakdown", {})
        if b.get("basic_info", 0) < 0.8:
            recos.append("Provide a more complete asset description.")
        if b.get("value_assessment", 0) < 0.8:
            recos.append("Provide a formal valuation or appraisal document.")
        if b.get("jurisdiction", 0) < 0.8:
            recos.append("Clarify the asset's location or city.")
        if b.get("asset_specific", 0) < 0.8:
            recos.append("Include more asset-specific details like documents, specs, or characteristics.")
        return recos

    def _define_next_steps(self, status: str) -> List[str]:
        if status == "verified":
            return ["Proceed to tokenization", "Create token on blockchain", "Generate smart contract"]
        elif status == "requires_review":
            return ["Add more details", "Request manual review"]
        else:
            return ["Asset rejected", "Revise asset information"]
