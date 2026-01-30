from typing import Dict


class ActionTypeMapper:
    """
    Responsible for mapping action types between different formats
    """
    
    def map_action_type(self, last_action_taken: str) -> str:
        """
        Map lastActionTaken from portfolio data to standard action types
        
        TODO: Replace keyword matching with LLM-based classification for better accuracy
        
        Examples from portfolio data:
        - "Provided financial health check" -> "call"
        - "Invited to SME webinar" -> "email"
        - "RM sent personalized offers" -> "offer"
        - "Monthly follow-up completed" -> "call"
        """
        if not last_action_taken:
            return "unknown"
            
        action_lower = last_action_taken.lower()
        
        # Map based on action description
        if any(keyword in action_lower for keyword in ["email", "invited", "webinar", "newsletter"]):
            return "email"
        elif any(keyword in action_lower for keyword in ["call", "phone", "follow-up", "health check"]):
            return "call"
        elif any(keyword in action_lower for keyword in ["offer", "proposal", "credit", "personalized"]):
            return "offer"
        elif any(keyword in action_lower for keyword in ["digital", "portal", "online", "app"]):
            return "digital"
        else:
            return "other"
    
    def determine_action_type(self, strategy: Dict) -> str:
        """
        Determine action type based on strategy channel
        """
        channel = strategy.get("channelOfDelivery", "email").lower()
        if "email" in channel:
            return "email"
        elif "phone" in channel or "call" in channel:
            return "call"
        elif "digital" in channel:
            return "digital"
        else:
            return "offer"


# Singleton instance
action_type_mapper = ActionTypeMapper()