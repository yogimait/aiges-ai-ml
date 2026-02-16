from typing import List, Dict, Any

class RuleBasedDetector:
    def __init__(self):
        self.patterns = {
            "ignore_instructions": ["ignore previous instructions", "ignore all previous instructions"],
            "reveal_system_prompt": ["reveal system prompt", "show me your system prompt", "what is your system prompt"],
            "act_as_developer": ["act as developer", "act as a developer", "you are a developer"],
            "bypass_restrictions": ["bypass restrictions", "ignore safety guidelines"],
            "system_prompt": ["system prompt"],
            "jailbreak": ["jailbreak", "DAN mode"]
        }

    def detect(self, prompt: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        matched_categories = []
        
        for category, triggers in self.patterns.items():
            for trigger in triggers:
                if trigger in prompt_lower:
                    matched_categories.append(category)
                    break 
        
        count = len(matched_categories)
        
        if count >= 2:
            score = 0.8
        elif count == 1:
            score = 0.6
        else:
            score = 0.1
            
        return {
            "injection_score": score,
            "matched_categories": matched_categories
        }
