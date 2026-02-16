from typing import Dict, Any, List

class RiskEngine:
    def calculate_risk(self, injection_score: float, tool_score: float) -> float:
        # Formula: 0.6 * injection_score + 0.4 * tool_score
        return round(0.6 * injection_score + 0.4 * tool_score, 2)

    def evaluate(self, final_risk: float, tool_authorized: bool) -> Dict[str, Any]:
        blocked = False
        reasons = []

        # If tool matching failed (score 1.0) usually implies block, but relying on formula logic:
        # If tool_score 1.0 -> 0.4 contribution.
        # If injection 0.1 -> 0.6*0.1 = 0.06. Total 0.46 (Safe)
        # BUT tool_policy returning "authorized=False" should probably be a BLOCK regardless of score?
        # Specification says:
        # "If unauthorized: tool_score = 1.0, authorized = false"
        # "Compute: final_risk = 0.6 * injection + 0.4 * tool"
        # "Apply thresholds: >= 0.75 -> blocked, 0.5-0.75 -> flagged"
        # Use strictly the formula and thresholds, plus authorization check separately if needed.
        # But wait, if unauthorized, is it blocked?
        # The prompt says: "Apply thresholds... >= 0.75 -> blocked". 
        # It doesn't explicitly say "Block if unauthorized". 
        # However, it says "Enforces tool invocation policies".
        # If tool is unauthorized, it logically should be blocked.
        # But I must follow "Apply thresholds" logic for risk. 
        # Let's check: unauthorized (1.0) means min risk 0.4.
        # Match 1 pattern (0.6) + Unauthorized (1.0) -> 0.36 + 0.4 = 0.76 -> Blocked. Correct.
        # No patterns (0.1) + Unauthorized (1.0) -> 0.06 + 0.4 = 0.46 -> Safe? 
        # That seems like a logic hole in the user's spec if they want strict enforcement.
        # BUT: "Enforces tool invocation policies".
        # If authorized=False, I should probably ensure it is blocked.
        # The PROMPT says: "Return EXACT response format... blocked: bool".
        # It says "Apply thresholds:" for risk.
        # I will assume that "blocked" is true IF (risk >= 0.75 OR not authorized).
        # Let's re-read: "If unauthorized: tool_score = 1.0, authorized = false"
        # Then "Compute final_risk". Then "Apply thresholds".
        # If I strictly follow thresholds, a safe prompt with unauthorized tool might pass (0.46).
        # However, "Enforces tool invocation policies" implies it must stop it.
        # I will enforce: if not tool_authorized, blocked = True, reason added.
        
        if not tool_authorized:
            blocked = True
            reasons.append("Tool policy violation")

        if final_risk >= 0.75:
            blocked = True
            reasons.append("High risk detected")
        elif final_risk >= 0.5:
            if not blocked: # Don't unblock if already blocked
                blocked = False # Flagged only
            reasons.append("Medium risk flagged")
        else:
            # < 0.5
            pass # Safe

        return {
            "final_risk": final_risk,
            "blocked": blocked,
            "reasons": reasons
        }
