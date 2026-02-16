from typing import List, Dict, Any, Optional

class PolicyEngine:
    def __init__(self):
        # Define allowed roles for each tool
        self.tool_policies = {
            "database_query": ["admin"],
            "file_access": ["admin"]
        }

    def check_policy(self, tool_name: Optional[str], role: str) -> Dict[str, Any]:
        if not tool_name:
            return {
                "tool_score": 0.0,
                "authorized": True,
                "reason": None
            }
            
        allowed_roles = self.tool_policies.get(tool_name)
        
        # Unknown tool -> unauthorized
        if allowed_roles is None:
             return {
                "tool_score": 1.0,
                "authorized": False,
                "reason": f"Unknown tool '{tool_name}' requested"
            }

        if role in allowed_roles:
            return {
                "tool_score": 0.0,
                "authorized": True,
                "reason": None
            }
        else:
            return {
                "tool_score": 1.0,
                "authorized": False,
                "reason": f"Role '{role}' not authorized for tool '{tool_name}'"
            }
