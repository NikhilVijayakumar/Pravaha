from typing import Dict, Any, List, Optional
from pravaha.domain.bot.model.utility_request import UtilityRequest

class CalculatorTool:
    def run(self, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        if not inputs:
            return "No inputs provided."
        
        results = []
        for inp in inputs:
            op = inp.get("operation")
            a = inp.get("a")
            b = inp.get("b")
            
            if op == "add":
                results.append(a + b)
            elif op == "multiply":
                results.append(a * b)
            else:
                results.append(f"Unknown operation: {op}")
        
        return results if len(results) > 1 else results[0]
