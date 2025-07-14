# verification_agent.py

from typing import Dict, List
from app.agents.agents_modular import CoordinatorAgent

class VerificationAgent:
    def __init__(self):
        self.verification_threshold = 0.7
        self.coordinator = CoordinatorAgent()

    def verify_asset(self, asset_data: Dict) -> Dict:
        try:
            verification_result = self.coordinator.verify(asset_data)
            result = {
                'overall_score': verification_result.get('overall_score', 0.0),
                'status': verification_result.get('status', 'pending'),
                'breakdown': verification_result.get('breakdown', {}),
                'agent_notes': verification_result.get('agent_notes', []),
                'recommendations': self._generate_recommendations(verification_result),
                'next_steps': self._define_next_steps(verification_result.get('status', 'pending')),
                'issues': []
            }
        except Exception as e:
            result = {
                'overall_score': 0.0,
                'status': 'error',
                'breakdown': {},
                'agent_notes': [],
                'recommendations': [],
                'next_steps': [],
                'issues': [f"Verification error: {str(e)}"]
            }
        return result

    def _generate_recommendations(self, verification_result: Dict) -> List[str]:
        recos = []
        b = verification_result.get("breakdown", {})
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
